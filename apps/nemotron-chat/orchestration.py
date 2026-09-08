"""Small, approval-gated orchestration layer for the local chat app.

This module deliberately uses only the Python standard library.  It is an
adapter seam for a future NeMo Agent Toolkit integration, not an agent runtime.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Callable

ALLOWED_TOOLS = {
    "list_files",
    "read_files",
    "pubmed_search",
    "extraction_report_plan",
    "python_syntax_check",
}
PLAN_TTL_SECONDS = 15 * 60
_plans: dict[str, dict[str, Any]] = {}


def _app_file(relative_name: str) -> Path:
    root = Path(__file__).resolve().parent
    candidate = (root / relative_name).resolve()
    if root != candidate and root not in candidate.parents:
        raise ValueError("O arquivo precisa estar dentro de apps/nemotron-chat")
    if not candidate.is_file() or candidate.suffix.lower() != ".py":
        raise ValueError("A verificação só aceita um arquivo Python existente do app")
    return candidate


def _clean_plans() -> None:
    cutoff = time.time() - PLAN_TTL_SECONDS
    for plan_id, plan in list(_plans.items()):
        if plan["created_at"] < cutoff:
            _plans.pop(plan_id, None)


def propose_tools(request: dict[str, Any]) -> dict[str, Any]:
    """Validate requested tools and return a non-executing approval plan."""
    requested = request.get("tools")
    if not isinstance(requested, list) or not requested:
        raise ValueError("Informe uma lista não vazia de ferramentas")
    normalized = []
    for item in requested:
        if not isinstance(item, dict) or item.get("name") not in ALLOWED_TOOLS:
            raise ValueError("Ferramenta não permitida")
        args = item.get("args", {})
        if not isinstance(args, dict):
            raise ValueError("Os argumentos da ferramenta devem ser um objeto")
        if item["name"] == "python_syntax_check":
            if args.get("command") != "python -m py_compile":
                raise ValueError("O único comando permitido é: python -m py_compile")
            _app_file(str(args.get("file", "")))
        normalized.append({"name": item["name"], "args": args})
    _clean_plans()
    plan_id = uuid.uuid4().hex
    _plans[plan_id] = {"created_at": time.time(), "tools": normalized}
    return {
        "plan_id": plan_id,
        "requires_approval": True,
        "expires_in_seconds": PLAN_TTL_SECONDS,
        "tools": [{"name": item["name"], "args": _safe_args(item["args"])} for item in normalized],
    }


def _safe_args(args: dict[str, Any]) -> dict[str, Any]:
    # Plans are returned to the browser, so never echo values that look like credentials.
    return {
        key: ("[redacted]" if any(word in key.lower() for word in ("key", "token", "secret", "password")) else value)
        for key, value in args.items()
    }


def _list_files(args: dict[str, Any], workspace: Callable[[], Path]) -> dict[str, Any]:
    root = workspace()
    extensions = {".txt", ".md", ".py", ".js", ".ts", ".json", ".yaml", ".yml", ".html", ".css"}
    files = sorted(
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in extensions
    )[:200]
    return {"files": files}


def _read_files(args: dict[str, Any], workspace: Callable[[], Path]) -> dict[str, Any]:
    root = workspace()
    names = args.get("files")
    if not isinstance(names, list) or len(names) > 10:
        raise ValueError("Informe até 10 arquivos selecionados")
    output = []
    for name in names:
        candidate = (root / str(name)).resolve()
        if root not in candidate.parents or candidate.suffix.lower() not in {".txt", ".md", ".py", ".js", ".ts", ".json", ".yaml", ".yml", ".html", ".css"}:
            raise ValueError("Arquivo fora da pasta autorizada ou extensão não permitida")
        if not candidate.is_file():
            raise ValueError(f"Arquivo não encontrado: {name}")
        output.append({"file": str(candidate.relative_to(root)), "content": candidate.read_text(encoding="utf-8", errors="replace")[:12000]})
    return {"files": output}


def execute_plan(plan_id: str, approved: bool, workspace: Callable[[], Path]) -> dict[str, Any]:
    if approved is not True:
        raise PermissionError("A aprovação explícita é obrigatória")
    _clean_plans()
    plan = _plans.pop(plan_id, None)
    if plan is None:
        raise ValueError("Plano inexistente, expirado ou já executado")
    results = []
    for item in plan["tools"]:
        name, args = item["name"], item["args"]
        if name == "list_files":
            result = _list_files(args, workspace)
        elif name == "read_files":
            result = _read_files(args, workspace)
        elif name == "pubmed_search":
            result = {"status": "placeholder", "message": "Busca PubMed/PMC será conectada em uma integração futura."}
        elif name == "extraction_report_plan":
            result = {"status": "planned", "message": "Extração e relatório foram planejados; nenhuma fonte foi alterada."}
        else:
            file_path = _app_file(str(args.get("file", "")))
            completed = subprocess.run(
                [sys.executable, "-m", "py_compile", str(file_path)],
                cwd=Path(__file__).resolve().parent,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            result = {"file": str(file_path.name), "ok": completed.returncode == 0}
            if completed.stderr:
                result["error"] = completed.stderr[-2000:]
        results.append({"tool": name, "result": result})
    return {"approved": True, "results": results}
