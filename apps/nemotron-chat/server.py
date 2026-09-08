"""Local, dependency-free chat app for NVIDIA Nemotron-compatible APIs."""

from __future__ import annotations

import json
import mimetypes
import os
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from orchestration import execute_plan, propose_tools

ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / "public"
MEMORY_FILE = ROOT / "data" / "memories.json"


def load_env_file() -> None:
    env_file = ROOT / ".env"
    if not env_file.is_file():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        value = value.strip().strip("\"'")
        if name and name not in os.environ:
            os.environ[name] = value


load_env_file()
PORT = int(os.getenv("NEMOTRON_PORT", "8787"))
ALLOWED_EXTENSIONS = {".txt", ".md", ".py", ".js", ".ts", ".json", ".yaml", ".yml", ".html", ".css"}
PROVIDERS = {
    "nvidia": {
        "base_url": "https://integrate.api.nvidia.com/v1",
        "key_env": "NVIDIA_API_KEY",
        "default_model": "nvidia/nemotron-3-super-120b-a12b",
        "models": [
            "nvidia/nemotron-3-ultra-550b-a55b",
            "nvidia/nemotron-3-super-120b-a12b",
            "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
        ],
    },
    "huggingface": {
        "base_url": "https://router.huggingface.co/v1",
        "key_env": "HF_TOKEN",
        "default_model": "nvidia/Llama-3.1-Nemotron-70B-Instruct",
        "models": [
            "nvidia/Llama-3.1-Nemotron-70B-Instruct",
            "nvidia/Llama-3.3-Nemotron-Super-49B-v1",
        ],
    },
}
memory_lock = threading.Lock()
key_pool_lock = threading.Lock()
key_pool_calls: dict[str, int] = {}
CALLS_PER_KEY = 3


def workspace_path() -> Path:
    default = Path(r"C:\Users\bella\OneDrive\Documentos\TDAH TCC")
    if not default.is_dir():
        default = Path.home() / "Desktop"
    if not default.is_dir():
        default = Path.home()
    configured = os.getenv("NEMOTRON_WORKSPACE_DIR", str(default))
    path = Path(configured).expanduser().resolve()
    if not path.is_dir():
        raise ValueError(f"A pasta configurada não existe: {path}")
    return path


def read_memories() -> list[dict[str, str]]:
    if not MEMORY_FILE.exists():
        return []
    try:
        value = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        return value if isinstance(value, list) else []
    except json.JSONDecodeError:
        return []


def get_key_pool(provider_name: str, provider: dict) -> list[str]:
    """Read a provider's key pool without exposing keys to the browser."""
    pool_name = f"{provider_name.upper()}_API_KEYS"
    raw_pool = os.getenv(pool_name, "").strip()
    if raw_pool:
        try:
            values = json.loads(raw_pool)
        except json.JSONDecodeError as error:
            raise ValueError(f"{pool_name} deve ser um array JSON de chaves") from error
        if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
            raise ValueError(f"{pool_name} deve conter apenas textos")
        keys = [value.strip() for value in values if value.strip()]
    else:
        keys = [os.getenv(provider["key_env"], "").strip()]
    if not keys or not keys[0]:
        raise ValueError(f"Configure {pool_name} ou {provider['key_env']} antes de iniciar o app")
    return keys


def ordered_keys(provider_name: str, keys: list[str]) -> list[str]:
    with key_pool_lock:
        calls = key_pool_calls.get(provider_name, 0)
        start = (calls // CALLS_PER_KEY) % len(keys)
        key_pool_calls[provider_name] = calls + 1
    return keys[start:] + keys[:start]


def json_response(handler: BaseHTTPRequestHandler, status: int, value: object) -> None:
    payload = json.dumps(value, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(payload)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(payload)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        print(format % args)

    def do_GET(self) -> None:
        route = urlparse(self.path).path
        if route == "/api/config":
            try:
                root = workspace_path()
                json_response(self, 200, {
                    "workspace": str(root),
                    "providers": PROVIDERS,
                    "memories": read_memories(),
                })
            except ValueError as error:
                json_response(self, 400, {"error": str(error)})
            return
        if route == "/api/files":
            try:
                root = workspace_path()
                files = [
                    str(path.relative_to(root))
                    for path in root.rglob("*")
                    if path.is_file() and path.suffix.lower() in ALLOWED_EXTENSIONS
                ][:200]
                json_response(self, 200, {"files": files})
            except ValueError as error:
                json_response(self, 400, {"error": str(error)})
            return
        file_path = PUBLIC / ("index.html" if route == "/" else route.lstrip("/"))
        if not file_path.is_file() or PUBLIC not in file_path.resolve().parents:
            json_response(self, 404, {"error": "Não encontrado"})
            return
        content = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(str(file_path))[0] or "text/plain")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self) -> None:
        route = urlparse(self.path).path
        try:
            size = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(size) or b"{}")
            if route == "/api/chat":
                json_response(self, 200, {"message": call_model(body)})
            elif route == "/api/memories":
                memory = save_memory(body)
                json_response(self, 201, memory)
            elif route == "/api/tools/plan":
                json_response(self, 200, propose_tools(body))
            elif route in {"/api/tools/execute", "/api/tools/code-run/approve"}:
                result = execute_plan(body.get("plan_id", ""), body.get("approved"), workspace_path)
                json_response(self, 200, result)
            else:
                json_response(self, 404, {"error": "Não encontrado"})
        except PermissionError as error:
            json_response(self, 403, {"error": str(error)})
        except (ValueError, KeyError, json.JSONDecodeError) as error:
            json_response(self, 400, {"error": str(error)})
        except RuntimeError as error:
            json_response(self, 502, {"error": str(error)})


def collect_context(file_names: list[str]) -> str:
    root = workspace_path()
    chunks = []
    for name in file_names[:10]:
        candidate = (root / name).resolve()
        if root not in candidate.parents or candidate.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue
        if candidate.is_file():
            text = candidate.read_text(encoding="utf-8", errors="replace")[:12000]
            chunks.append(f"\n--- {candidate.relative_to(root)} ---\n{text}")
    return "".join(chunks)


def call_model(request: dict) -> dict:
    provider_name = request.get("provider", "nvidia")
    provider = PROVIDERS.get(provider_name)
    if provider is None:
        raise ValueError("Provedor inválido")
    keys = ordered_keys(provider_name, get_key_pool(provider_name, provider))
    model = request.get("model") or provider["default_model"]
    if not isinstance(model, str) or not model.strip():
        raise ValueError("Informe um identificador de modelo")
    model_warning = None if model in provider["models"] else (
        f"Modelo '{model}' não está na lista local; a API do provedor fará a validação."
    )
    messages = request.get("messages")
    if not isinstance(messages, list) or not messages:
        raise ValueError("Envie pelo menos uma mensagem")
    system = (
        "Responda em português. Você é um assistente de pesquisa. "
        "Não alegue ter executado ações que não executou."
    )
    if request.get("mode") == "agent":
        system += " Organize a resposta como conversa de agente, com plano e próximos passos."
    context = collect_context(request.get("files", []))
    memories = request.get("memories", [])
    if isinstance(memories, list):
        context += "".join(
            f"\n--- Memória: {memory.get('title', 'Sem título')} ---\n{memory.get('text', '')}"
            for memory in memories
            if isinstance(memory, dict) and memory.get("text")
        )[:40000]
    if context:
        messages = [{"role": "system", "content": system + "\nArquivos selecionados:" + context}] + messages
    else:
        messages = [{"role": "system", "content": system}] + messages
    payload: dict = {
        "model": model,
        "messages": messages,
        "max_tokens": min(int(request.get("max_tokens", 2048)), 8192),
        "temperature": 0.4,
    }
    if request.get("thinking") and provider_name == "nvidia":
        payload["chat_template_kwargs"] = {"enable_thinking": True}
        payload["reasoning_budget"] = min(int(request.get("reasoning_budget", 8192)), 16384)
    failures = []
    for key in keys:
        http_request = urllib.request.Request(
            provider["base_url"] + "/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(http_request, timeout=120) as response:
                result = json.loads(response.read().decode("utf-8"))
            if result.get("error"):
                failures.append(result["error"].get("message", "erro retornado pela API"))
                continue
            message = result.get("choices", [{}])[0].get("message", {})
            return {
                "content": message.get("content", ""),
                "reasoning": message.get("reasoning_content"),
                "warning": model_warning,
            }
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as error:
            if isinstance(error, urllib.error.HTTPError):
                failures.append(f"HTTP {error.code}")
            else:
                failures.append(type(error).__name__)
    raise RuntimeError(f"Nenhuma chave disponível para {provider_name}: {' | '.join(failures)}")


def save_memory(body: dict) -> dict:
    text = str(body.get("text", "")).strip()
    title = str(body.get("title", "Memória")).strip() or "Memória"
    if not text or len(text) > 20000:
        raise ValueError("A memória deve ter entre 1 e 20.000 caracteres")
    item = {"title": title[:200], "text": text}
    with memory_lock:
        memories = read_memories()
        memories.append(item)
        MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        MEMORY_FILE.write_text(json.dumps(memories[-100:], ensure_ascii=False, indent=2), encoding="utf-8")
    return item


if __name__ == "__main__":
    print(f"Nemotron Chat: http://127.0.0.1:{PORT}")
    print(f"Pasta de trabalho: {workspace_path()}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
