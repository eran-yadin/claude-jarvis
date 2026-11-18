# claude-jarvis

Jarvis-style voice assistant built on Claude. Plan: `PLAN.md`.

Two programs, one WebSocket:

- `brain/`  - thinks, calls tools, owns memory (rig now, server later)
- `client/` - talks to you (terminal now, voice in job 3), runs PC actions
- `jarvis-data/` - everything Jarvis saves; copy this dir to move to the server

## setup

```sh
uv venv && uv pip install -e .
cp jarvis-data/secrets.env.example jarvis-data/secrets.env   # then paste the key in an editor
chmod 600 jarvis-data/secrets.env
```

## run (job 1)

```sh
uv run uvicorn brain.main:app --host 127.0.0.1 --port 8765   # terminal 1
uv run python -m client.terminal                             # terminal 2
```

## offline test (fake model, no key, no cost)

```sh
uv run python -m tests.test_text_loop
```

## job 1 is done when

Typing "what time is it" gets an answer that used the `get_time` tool.

Fill the TODOs in this order: `brain/llm.py` -> `brain/agent.py` -> `brain/main.py` -> `client/terminal.py`.
