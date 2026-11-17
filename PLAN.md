# Claude x Jarvis — Architecture Plan

_As of 2026-11-17. Live doc: https://claude.ai/artifact/5STNK9ZWB2EXwuVet7G4Qs_

## Goal and scope

Jarvis is a voice assistant built on Claude: say a wake word, speak, and it answers out loud and acts. Version 1 runs entirely on the CachyOS desktop for testing. After that, the brain and everything it saves move to the home server, so any machine that can reach the server becomes a Jarvis terminal.

First-version skills: morning briefing, PC control, hardware and smart home, and general chat with memory. A desk camera that can photograph the table comes later.

The one design rule that follows from this: **build it as client and server from day one, even while both run on the same PC.** If the two halves only ever talk over a network API, moving to the server is a change of address and not a rewrite.

## Architecture

Two programs that talk over one WebSocket. The client handles sound and local actions; the brain handles thinking and state.

```
mic -> wake word -> record -> speech-to-text --text--> BRAIN
speaker <- text-to-speech <--reply text-- BRAIN
PC actions (apps, commands, files) <--tool request-- BRAIN
```

**Client (one per machine, thin)**

- Wake word, recording, speech-to-text, text-to-speech.
- A small local agent that runs PC-control actions on that machine. This matters after the move: the brain will sit on the server, but "open Firefox" has to happen on the PC you are talking to.
- Holds no state except its own config and the brain's address.

**Brain (on the PC now, on the server later)**

- FastAPI service with a WebSocket endpoint, the same pattern as the manhunt backend.
- Claude agent loop: receives text, decides, calls tools, returns text to speak.
- Owns memory, conversation history, credentials and all non-PC tools (email, calendar, news, hardware).

Why this split: audio is heavy and latency-sensitive, so it stays next to the mic. State must be in exactly one place, or two machines will disagree about what Jarvis remembers.

## Voice pipeline

All three stages run locally and are free; only the text goes to Claude. These are the tools most 2026 local-voice builds use; versions are not pinned yet.

| Stage | Pick | Why |
| --- | --- | --- |
| Wake word | [openWakeWord](https://github.com/dscripka/openWakeWord) | Open source, custom wake words, tiny CPU load. Check whether its stock "hey Jarvis" model is good enough before training one. |
| Speech-to-text | [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | Runs on the NVIDIA GPU for low latency; Whisper models are multilingual. |
| Text-to-speech | [Piper](https://github.com/rhasspy/piper) | Fast on CPU. Voice quality is good, not movie-Jarvis; swap later if it bothers you. |

The wake word always stays on the client so no audio leaves the machine until you call it. Speech-to-text can move to the server later if a weak client needs it.

## Skills

Each skill is a set of tools Claude can call. The [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/custom-tools) lets you define a tool as a Python function; the plain Messages API with tool use is the lighter alternative (see open decisions).

| Skill | Tools it needs | Runs on |
| --- | --- | --- |
| Morning briefing | Gmail read, Google Calendar read, news search | Brain |
| PC control | Launch app, run allowlisted command, find/open file, volume/media | Client |
| Hardware / smart home | HTTP or MQTT calls to ESP32 devices, gate, cameras | Brain |
| Chat + memory | Read/write memory files, search past conversations | Brain |
| Desk camera (later) | Capture a frame, send it to Claude as an image | Client or IP camera |

The briefing needs Jarvis's own Google OAuth credentials. The Gmail and Calendar connections used in the Claude app do not carry over to a self-hosted program.

## Memory and data

Everything Jarvis saves lives in one directory, so the server move is: copy the directory, change the brain's address in each client.

```
jarvis-data/
  memory/          # markdown files: facts, preferences, people, projects
  history.sqlite   # conversations, searchable
  config.yaml      # devices, allowlists, voice settings
  secrets.env      # API keys, OAuth tokens - never synced or committed
```

Memory as plain markdown keeps it readable and hand-editable, and Claude handles it well. SQLite covers history without running a database server.

## Privacy: always listening without a cloud mic

No audio ever leaves the machine. The only thing sent to Anthropic is the text of a command you spoke after the wake word, plus whatever a tool returned for that command.

How the design guarantees that:

- **Wake word runs locally.** It looks at a rolling buffer of a second or two held in RAM and throws it away. Nothing is recorded, written to disk or sent until the wake word fires.
- **Speech-to-text runs locally too.** So even after the wake word, the cloud gets a transcript, never your voice or the room.
- **Recording is bounded.** It stops on silence or after a hard time limit, so a false wake cannot turn into an open mic.
- **You can see and stop it.** A tray icon and a chime whenever it is recording, a global mute hotkey, and a push-to-talk mode that disables the wake word entirely. A hardware mute switch on the mic is the only control software cannot override.
- **You can audit it.** Every activation is logged locally with its transcript and what was sent out, so false wakes are visible.
- **No raw audio is stored**, except in an opt-in debug mode.
- **Listen mode is a setting.** `listen_mode: wake_word | push_to_talk` in `config.yaml`, default `wake_word`. The push-to-talk trigger is a generic input: a hotkey now, a hardware button later (a USB HID key or an ESP32 sending an event to the client).

What still reaches Anthropic, so you decide knowingly: your spoken commands as text, the memory and history included as context, tool results such as email contents during a briefing, and later any desk-camera photos you ask for. Check Anthropic's current API data-retention terms before putting email through it.

## Safety

Speech-to-text mishears, and anyone in the room can talk to it, so actions are tiered by what a mistake costs.

| Tier | Examples | Rule |
| --- | --- | --- |
| Read | Briefing, status, search | Runs immediately |
| Reversible | Open app, volume, lights | Runs, says what it did |
| Destructive or physical | Delete files, arbitrary shell, open the gate | Repeats the action back and waits for a spoken "confirm" |

PC commands go through an allowlist in `config.yaml`, not a raw shell. Client and brain share an auth token, which becomes mandatory once the brain is on the server.

Security rules beyond the tiers:

- **Untrusted content cannot give orders.** Emails, web pages and camera text are data. Anything a tool reads can never trigger a tier-3 action without your spoken confirmation, which blocks an email that says "Jarvis, open the gate".
- **Voice is not identity.** A TV or a guest can say the wake word. Physical actions such as the gate need a spoken PIN or stay disabled by voice.
- **Network.** The brain binds to localhost in version 1. On the server it is reachable only over the VPN, with TLS and a per-client token, never port-forwarded to the internet.
- **Secrets.** `secrets.env` is readable only by the Jarvis user, kept out of git and backups. Google access is read-only scopes.
- **Camera.** One frame on explicit request, never a stream, with a physical cover.

## Phases

Each phase ends with something you can use, and voice comes after the brain works so you debug one thing at a time.

1. **Text loop.** Brain service plus a terminal client. Type, Claude answers, one dummy tool proves the tool path.
2. **Memory.** The `jarvis-data/` layout, memory read/write tools, conversation history.
3. **Voice.** Wake word, speech-to-text, text-to-speech on the client. Jarvis now talks.
4. **Skills.** Morning briefing first (read-only, low risk), then PC control, then hardware.
5. **Server move.** Brain and `jarvis-data/` to the server, auth on, second machine as a client.
6. **Desk camera.** Capture tool plus vision.

## Open decisions

- [x] Language: English only for now (decided 2026-11-17).
- [x] Brain framework: plain Messages API with our own tool loop, Claude Haiku 5.5 by default, model swappable in `config.yaml` (decided 2026-11-17).
- [ ] Billing: a self-hosted Jarvis calls the Anthropic API with an API key, billed per use and separate from a Claude app subscription.
- [ ] Network: how other machines reach the server - LAN only, or a VPN such as Tailscale or WireGuard for outside the house.
- [x] Clients: Linux only for now (decided 2026-11-17).
- [ ] First hardware target for the smart-home skill.
- [ ] Wake word: "Hey Jarvis" or something custom.
- [x] Listening default: always listening for the wake word; push-to-talk stays available as a mode (decided 2026-11-17).
- [x] Email in the briefing: sender and subject only for now, more on request later (decided 2026-11-17).
