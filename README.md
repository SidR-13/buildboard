# BuildBoard

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?style=flat-square&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=flat-square&logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-multi--stage-2496ED?style=flat-square&logo=docker&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-EC2%20%7C%20RDS%20%7C%20ECR-232F3E?style=flat-square&logo=amazonaws&logoColor=white)
![Claude](https://img.shields.io/badge/Claude%20API-tool--use-D97757?style=flat-square)

A self-hosted CI/CD monitoring platform: it ingests GitHub Actions webhook
events, computes build health metrics, uses Claude to explain *why* a build
failed, and pushes all of it to a live dashboard over WebSockets — no
polling, no refresh button.

**Live:** [buildboard-siddhesh.duckdns.org](https://buildboard-siddhesh.duckdns.org)

### Contents
[Why I built this](#why-i-built-this) · [Demo](#live-update-demo) · [Screenshots](#screenshots) · [Architecture](#architecture) · [Engineering log](#engineering-log) · [Tech stack](#tech-stack) · [Running locally](#running-locally) · [API](#api)

---

## Why I built this

Every team with a CI pipeline eventually asks the same three questions:
is it healthy, is it slow, and why did it just break. GitHub's own Actions
UI answers none of them well at a glance — you're clicking into individual
runs, reading raw logs, and re-deriving pass rate by eye.

I wanted something that treats build data as a time series instead of a
list of runs: a health score that reacts to *trends*, not just the latest
result; live updates the moment a build finishes, not on refresh; and for
failures, an actual explanation instead of a wall of stack trace.

It's also, deliberately, a vertical slice through a real production stack —
signed webhooks, an async API, a real-time layer, a third-party LLM
integration, containerization, and a CI/CD pipeline that deploys itself.
Every piece is there because the system needed it, not because it looked
good on a list.

## Live update demo

A commit lands on GitHub, Actions runs it, and the dashboard updates itself
— no reload. This is a real webhook round-trip, not a simulated animation:
a build history row and both charts pick up the new run the moment the
backend broadcasts it over WebSocket.

![Live update demo](docs/screenshots/demo-live-update.gif)

## Screenshots

**Dashboard** — health score, pass rate, and average build time per repo, computed from real webhook history.

![Dashboard](docs/screenshots/dashboard.png)

**Repo detail** — build duration trend, pass/fail history, and live updates over WebSockets (no refresh needed when a new build lands).

![Repo detail](docs/screenshots/repo-detail.png)

**Failure analysis** — on a failed build, the last 50 lines of CI logs are sent to Claude, which returns a structured root cause and suggested fix.

![Failure analysis](docs/screenshots/build-detail.png)

---

## Architecture

**Event flow** — a webhook arriving to a metric change on screen:

```mermaid
flowchart TD
    GH["GitHub Actions"] -->|"HMAC-signed webhook"| API["FastAPI backend"]
    API --> DB[("PostgreSQL")]
    API --> WS["WebSocket clients"]
    WS --> UI["React dashboard"]
    DB -->|"metrics query"| UI
    API -->|"on failure"| LOGS["GitHub REST API<br/>last 50 log lines"]
    LOGS --> CLAUDE["Claude API<br/>tool-use, structured output"]
    CLAUDE -->|"root cause + fix"| DB
```

**Deploy path** — a push to `main` reaching production with zero downtime:

```mermaid
flowchart TD
    PUSH["git push main"] --> GHA["GitHub Actions"]
    GHA -->|"OIDC, no stored keys"| ECR["AWS ECR"]
    GHA -->|"ssm:SendCommand"| EC2["EC2 instance"]
    EC2 -->|"pulls image, runs deploy.sh"| BG{"Blue/green swap"}
    BG -->|"health check passes"| OK["Nginx reload<br/>traffic flips"]
    BG -->|"health check fails"| FAIL["Abort<br/>old version stays live"]
```

---

## Engineering log

I built this with an AI pair-programmer (Claude) doing a lot of the typing
and a fair amount of the debugging legwork — that's disclosed here, not
hidden, because it's an honest description of how the code got written.
What it didn't do is make the calls: every tradeoff below is one I decided,
usually after being walked through the options, sometimes after rejecting
the AI's first take. The entries are in build order, kept to the ones that
actually involved a decision or a real bug, not a changelog of every file
touched.

**Webhook lifecycle → one row, not three.**
GitHub sends three separate deliveries per workflow run —
`requested` → `in_progress` → `completed` — not one. First instinct was to
store each as its own row; decided against it once I realized that's not
"history," it's the same run's status flickering three times in the table.
Handler now finds-or-creates a single row keyed on GitHub's `run_id` and
updates it in place, so a run has one identity through its whole lifecycle.
Signature verification (HMAC-SHA256, `hmac.compare_digest` — constant-time,
so timing can't leak the secret) went in from the first version, not bolted
on after; an unauthenticated webhook endpoint accepting arbitrary POSTs
wasn't a version I wanted to ship even for a portfolio project.

**Health score: fought the urge to pick an arbitrary "slow" threshold.**
First draft docked points for any build over some fixed number of seconds.
Killed it before writing it — a monorepo's test suite and a one-file lint
check have nothing in common, so any fixed threshold is just a number I
made up. Landed on scoring build duration by *trend* (this window vs. the
prior one) instead, capped at a 20-point penalty so a flaky-slow week can
soften a passing score but never make a healthy repo read as broken.
Pass/fail rate stays the dominant signal on purpose.

**Flaky-build detection: shipped a known gap instead of over-building.**
Detection groups runs by `(branch, commit_sha)` and flags any group with
both a success and a failure — same commit, two outcomes, most likely
non-determinism. Then found the real gap: GitHub's "re-run failed jobs"
reuses the same `run_id`, and my webhook handler updates that row in place
(the same design decision from the first entry), so a re-run silently
overwrites the original failure before detection ever sees both outcomes.
Fixing it properly means storing `run_attempt` and inserting a new row per
attempt — a real schema change. I explicitly asked myself whether I was
overcomplicating the project chasing a metric that doesn't even appear in
the interview pitch, decided the answer was yes, and documented the
limitation instead of building around it. I'd make the opposite call on a
system other engineers actually relied on.

**A GitHub PAT that "existed" but didn't work.**
Claude API log-fetching returned 401s on the first real test. My check had
confirmed `GITHUB_TOKEN` was *set* in `.env` — it just so happened to still
be the literal placeholder string from `.env.example`, and I'd read
"present" as "valid" without actually looking at the value. Confirmed the
real cause by running the same request with `gh`'s own token side-by-side
and watching it succeed where mine failed. Fix was a fresh, narrowly-scoped
fine-grained PAT (read-only, one repo) — kept deliberately separate from
`gh`'s own broader token rather than reusing it.

**A debug print that "didn't run" — until stdout buffering did.**
Building the WebSocket connection registry, I added temporary print
statements to watch it from inside the running process (a separate script
can't see another process's memory). First run: nothing printed, despite
the code clearly executing on every other check I ran. Root cause was
Python block-buffering stdout once it's piped to a file, not a logic bug —
fixed by confirming with `flush=True`, then removed the debug prints and
explicitly re-ran the full test against the *cleaned-up* code, because
"it worked before I removed the prints" isn't the same claim.

**Proved the container networking story instead of asserting it.**
Docker container-to-container traffic goes over the service name, not
`localhost` — I knew that going in, but the compose file's `DATABASE_URL`
still pointed at `localhost:5432` (correct for host-run dev, wrong from
inside a container). Rather than just fixing it and moving on, I exec'd
into the running backend container and manually attempted a raw socket
connection to `localhost:5432` from inside it, watched it fail with
`Connection refused`, then resolved the service-name hostname to confirm
where the real listener was. Wanted the explanation to survive being
asked "how do you know," not just sound right.

**Least-privilege IAM meant hitting real walls, on purpose.**
The AWS CLI identity for this project has EC2/RDS/ECR permissions and
nothing else — deliberately, not `AdministratorAccess`. That choice has a
cost: creating the EC2 instance's IAM role hit an access-denied wall
(a scoped-down identity can't grant IAM permissions, including to itself),
so that one step had to go through the AWS console under the account
owner instead of the CLI. Then attaching the finished role to the instance
hit a *second*, different wall — `iam:PassRole`, a separate AWS guardrail
against using a role to escalate your own privileges — fixed with one
narrow inline grant scoped to that single role's ARN, not IAM broadly. Two
walls in a row is annoying to debug through; it's also exactly what
least-privilege is supposed to do, and I'd rather hit it while building
than not have it at all.

**The project didn't have a real GitHub repo — until CI/CD needed one.**
Batches 0 through 10 existed only as local files; only a disposable test
fixture had ever been pushed to GitHub. Starting the CI/CD pipeline meant
starting with `git init`, a `.gitignore` for a nested test-fixture repo,
and a private `SidR-13/buildboard` repo — infrastructure work the batch
plan didn't call out, discovered by trying to write a workflow file and
having nowhere to put it.

**OIDC trust denied — diagnosed by reading the actual token, not the docs.**
Wired up GitHub Actions to assume an AWS role via OIDC so no AWS keys
would live in repo secrets. It failed with `Not authorized to perform
sts:AssumeRoleWithWebIdentity` even though the trust policy visually
matched every OIDC tutorial's example. Instead of guessing, I added a
throwaway workflow step that fetched GitHub's real ID token and decoded
its JWT payload to stdout. That showed the actual cause: GitHub now embeds
immutable owner/repo IDs in the `sub` claim by default —
`repo:owner@id/repo@id:ref:...` — a format no tutorial assumes because it's
newer than most of them. Fixed with a wildcard match in the trust policy,
then deleted the debug step once confirmed.

**A security group correctly blocked my own deploy — didn't weaken it to fix that.**
The deploy step's first version SSH'd into EC2, and failed with a TCP
timeout. Root cause: the EC2 security group intentionally locks port 22 to
my own IP, and GitHub's hosted runners connect from rotating ranges — the
firewall was doing exactly its job. The easy fix was opening port 22 to
the internet; I didn't take it. Pivoted the whole deploy step to AWS
Systems Manager instead — `ssm:SendCommand` runs the deploy script over an
authenticated AWS API call through the instance's own IAM role, so port 22
never has to open at all. More moving parts, but the security posture I'd
already decided on stayed intact instead of getting quietly walked back
under deadline pressure.

**Blue-green over "restart with extra steps."**
The batch plan called for a "zero-downtime rolling update" on a single
free-tier EC2 instance — no load balancer, no second server. Restart-based
deploys would have a real (if brief) gap where the site is down; I decided
that didn't actually satisfy the requirement, even though it's the fastest
thing to build. Went with an actual blue-green swap instead: the new
container starts on a spare port, gets health-checked against `/health`
— checking the database connection specifically, not just a 200 — and
only then does Nginx flip traffic to it with a graceful reload. A failed
health check aborts and leaves the current version live; a bad image
can't take the site down.

**Shipped the real Claude output, not the mock, in the README.**
Writing this file, the failure-analysis screenshot showed `[MOCK] Build
failed - AI_MOCK=true, no real analysis performed` — accurate for local
dev, but it undersells the actual feature to anyone reading this. Rather
than pass it off as-is, I flipped `AI_MOCK` off locally for exactly one
real Claude call against a real failed build, captured that, and flipped
it back — the $1.50 project budget accounted for demo-purpose calls like
this from the start. Same standard applied to the dashboard screenshot: it
had one real repo in it and looked sparse, so I registered a second real
GitHub repo with its own webhook and build history rather than fake a
fuller-looking dashboard.

---

## Tech stack

| Layer | Choice | Why |
|---|---|---|
| Backend | Python 3.11, FastAPI | Async I/O for concurrent webhook handling + WebSocket connections without a separate worker model |
| ORM / migrations | SQLAlchemy 2.0, Alembic | Versioned schema changes, not hand-run SQL against production |
| Database | PostgreSQL (RDS in prod) | Relational data with real foreign keys (repos → runs → analyses); managed RDS over self-hosting for backups/patching |
| Real-time | Native FastAPI WebSockets | No separate real-time service needed at this scale |
| AI | Claude API (Haiku dev / Sonnet demo) | Forced tool-use for structured output; model swappable via one env var |
| Frontend | React, TypeScript, Vite, Tailwind, Recharts | Typed API contracts end-to-end; Vite for fast iteration |
| Containers | Docker, multi-stage builds | Identical artifact from a laptop to production |
| Infra | AWS EC2, RDS, ECR, Nginx, Let's Encrypt | Free-tier-covered, no managed services that cost money idle (ELB, NAT Gateway explicitly avoided) |
| CI/CD | GitHub Actions, OIDC, AWS SSM | No long-lived credentials anywhere in the pipeline |

---

## Running locally

```bash
# Postgres
cd backend && docker compose up -d postgres

# Backend
cd backend
python3.11 -m venv venv && ./venv/bin/pip install -r requirements.txt
cp .env.example .env   # DATABASE_URL, GITHUB_WEBHOOK_SECRET, etc. — AI_MOCK=true needs no API key
./venv/bin/alembic upgrade head
./venv/bin/uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
cp .env.example .env
npm run dev
```

`AI_MOCK=true` (the default) skips real Claude calls entirely, so the
whole pipeline runs end-to-end with no API key and no cost.

## API

```
POST /webhooks/github        GitHub webhook receiver (HMAC verified)
GET  /repos                  List monitored repos
GET  /repos/{id}/metrics     Health score, pass rate, flaky-build detection
GET  /repos/{id}/runs        Build history
GET  /runs/{id}               Single build detail
GET  /runs/{id}/analysis      Claude failure analysis
WS   /ws/{repo_id}           Live build updates
GET  /health                  Health check
```
