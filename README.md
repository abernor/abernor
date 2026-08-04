# AI Orchestrator

A minimal, local autonomous build pipeline powered by [Claude](https://www.anthropic.com/).
Give it a goal in plain language and it runs a closed loop of specialized agents —
**Plan → Code → Deploy → Test → Fix** — retrying until the result passes its own checks.

## Architecture

Each stage is a single-responsibility agent (one Claude call). The orchestrator
drives them in sequence and loops the Code/Deploy/Test/Fix cycle until the tests
pass or `MAX_ITERATIONS` is hit.

```
          ┌──────────┐
  goal ──▶│   PLAN   │  turn the goal into a concrete build plan
          └────┬─────┘  + acceptance criteria
               ▼
          ┌──────────┐
          │   CODE   │  implement the plan as runnable code
          └────┬─────┘
               ▼
          ┌──────────┐
          │  DEPLOY  │  write the code to the workspace (stub: local disk)
          └────┬─────┘
               ▼
          ┌──────────┐
          │   TEST   │  check the code against the acceptance criteria
          └────┬─────┘
        pass?  │
      ┌────────┴────────┐
      ▼                 ▼
   ✅ done          ┌──────────┐
                    │   FIX    │  repair using the failing report ──┐
                    └──────────┘                                    │
                          └───── back to DEPLOY ────────────────────┘
```

| Stage  | Module                  | Responsibility |
|--------|-------------------------|----------------|
| Plan   | `src/agents/planner.py` | Goal → implementation plan + acceptance criteria |
| Code   | `src/agents/coder.py`   | Plan → source code |
| Deploy | `src/agents/deployer.py`| Persist code to the workspace (swap for real deploy) |
| Test   | `src/agents/tester.py`  | Evaluate code against the criteria → PASS / FAIL |
| Fix    | `src/agents/fixer.py`   | Failing report → corrected code |

The loop itself lives in `src/orchestrator.py`; configuration in `src/config.py`.

## Project layout

```
.
├── main.py               # CLI entry point
├── requirements.txt
├── .env.example          # copy to .env and fill in
└── src/
    ├── config.py         # settings + Claude client
    ├── orchestrator.py   # the Plan→Code→Deploy→Test→Fix loop
    └── agents/           # one module per stage
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # then add your ANTHROPIC_API_KEY
```

## Usage

```bash
python main.py "Build a CLI that reverses a string"
```

## Configuration

Set in `.env` (see `.env.example`):

| Variable              | Default          | Purpose |
|-----------------------|------------------|---------|
| `ANTHROPIC_API_KEY`   | —                | Claude API key |
| `ORCHESTRATOR_MODEL`  | `claude-opus-5`  | Model used by every agent |
| `ORCHESTRATOR_EFFORT` | `high`           | Reasoning effort (`low`…`max`) |
| `WORKSPACE_DIR`       | `./workspace`    | Where generated artifacts are written |
| `MAX_ITERATIONS`      | `5`              | Max Test→Fix retries before giving up |

## Status

Early scaffold. `DEPLOY` and `TEST` are intentionally simple (write-to-disk and
an LLM-judged check) so the loop runs end to end; replace them with a real deploy
target and an executable test harness as the project grows.
