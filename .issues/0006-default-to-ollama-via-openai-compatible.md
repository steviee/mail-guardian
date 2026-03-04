---
id: 6
title: Default to Ollama via OpenAI-compatible API
status: open
priority: high
labels: []
created: "2026-03-04"
updated: "2026-03-04"
---

Das Projekt soll primär Ollama als LLM-Backend nutzen (via OpenAI-compatible API auf localhost:11434). LiteLLM unterstützt dies bereits via 'ollama/model-name' oder 'ollama_chat/model-name'. Default-Model in settings.yaml auf ein Ollama-Model setzen (z.B. ollama_chat/llama3.2). Fallback auf andere Provider bleibt via LiteLLM möglich.
