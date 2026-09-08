# Nemotron Chat local

Este app usa chamadas HTTP para endpoints OpenAI-compatible; ele não baixa nem instala o modelo. O navegador abre um layout de chat para os modos **Chat** e **Agente**, enquanto o servidor Python mantém a chave fora do HTML, lê uma pasta autorizada e grava memórias em `data/memories.json`.

## Abrir no Windows

No terminal integrado do VS Code, a partir da raiz deste repositório:

```powershell
$env:NVIDIA_API_KEY = "nvapi-sua-chave"
$env:NEMOTRON_WORKSPACE_DIR = "C:\Users\bella\OneDrive\Documentos\TDAH TCC"
python apps\nemotron-chat\server.py
```

Abra `http://127.0.0.1:8787`. Para Hugging Face, use `$env:HF_TOKEN = "hf_seu-token"` e troque o provedor na tela.

### Várias chaves e roteamento

Para um grupo de pesquisadores, configure um pool JSON por provedor. O servidor usa cada chave por três chamadas, passa para a próxima e retorna à primeira em loop. Se a chave selecionada falhar, tenta imediatamente as demais:

```powershell
$env:NVIDIA_API_KEYS = '["nvapi-chave-1","nvapi-chave-2","nvapi-chave-3"]'
$env:HF_API_KEYS = '["hf-token-1","hf-token-2"]'
```

Use `NVIDIA_API_KEY` ou `HF_TOKEN` somente quando houver uma chave única. Nunca coloque esses valores em arquivos versionados. O contador do ciclo é reiniciado quando o servidor reinicia; as chaves nunca são enviadas ao navegador.

GitHub Desktop serve para clonar, versionar e publicar os arquivos; ele não executa o servidor. O VS Code é o local recomendado para abrir o terminal e editar o projeto. A chave nunca deve ser commitada.

## Limites de segurança

Somente arquivos de texto com extensões permitidas são listados, e o servidor impede caminhos fora de `NEMOTRON_WORKSPACE_DIR`. O modo agente conversa e produz planos, mas não executa comandos no computador. Memórias são locais e não entram no Git.
