# BuildBoard — CI/CD Pipeline Monitor & Build Analytics

---

## What This Project Is
A self-hosted CI/CD monitoring platform that gives engineering teams
real-time visibility into their GitHub Actions pipeline health.
It processes webhook events, computes build metrics, analyzes failures
with AI, and displays everything in a live dashboard.

---

## Why We Are Building This
- Every tech company has CI/CD pipelines — resonates in every interview
- Shows Docker, AWS, WebSockets, Webhooks — skills missing from portfolio
- Fully deployable end-to-end on AWS with Docker
- Every feature has a real engineering reason behind it
- Can be demoed live in interviews

---

## My Setup
- OS: macOS (brand new machine — Apple Silicon M1/M2/M3)
- Currently installed: Python only
- Everything else gets installed in Batch 0
- IMPORTANT: All Docker commands must use --platform linux/amd64
  because Mac ARM chips need this flag for compatibility

---

## Tech Stack
- Backend:    Python 3.11, FastAPI (async)
- Database:   PostgreSQL (via Docker locally, RDS on AWS)
- Cache:      Redis (via Docker locally, on EC2 on AWS)
- Real-time:  WebSockets (built into FastAPI)
- AI:         Claude API — Haiku for dev, Sonnet for demo
- Frontend:   React + TypeScript + Tailwind CSS + Recharts
- Containers: Docker + Docker Compose
- Deploy:     AWS EC2 + RDS PostgreSQL + ECR + Nginx
- CI/CD:      GitHub Actions → Docker → ECR → EC2
- Webhooks:   GitHub Webhooks + ngrok for local development

---

## THE RULES — Read Before Every Session

### For Claude In VS Code:
1. Before writing ANY code — explain what it does and why
2. Explain EVERY single line of code written
3. After each batch — tell me exactly what to run to verify
4. Wait for my confirmation before starting the next batch
5. If I ask WHY — stop everything and explain fully
6. Never assume I know something — explain from first principles
7. If something fails — explain WHY it failed before fixing it
8. Always check CLAUDE_CONTEXT.md before doing anything

### For Me:
1. Never accept code I do not understand
2. Ask WHY for every line that is unclear
3. Verify each batch works before saying confirmed
4. Update this file after every batch
5. Start a new session when Claude starts forgetting context

---

## When To Start A New Claude Session

Start a fresh session when ANY of these happen:

```
1. Claude gives wrong answers about decisions made earlier
   Example: It forgets we chose async FastAPI in Batch 1

2. Claude starts regenerating files that already exist
   Example: It rewrites main.py when we are on Batch 4

3. Claude contradicts itself within the same session
   Example: Uses different port numbers than previously set

4. The session has gone longer than 3-4 batches
   Safe to start fresh even if Claude seems fine

5. You get a confusing error Claude cannot explain
   Fresh session + paste the error = better diagnosis

6. Claude stops following the explanation rules
   If it writes code without explaining — start fresh
```

### How To Start A New Session Correctly:

Paste this EXACTLY at the start of every new session:

```
Read CLAUDE_CONTEXT.md completely before doing anything.

We are building BuildBoard — a CI/CD pipeline monitor.
I am on Apple Silicon Mac. All Docker commands need --platform linux/amd64.

Completed batches so far: [LIST THEM]
Current batch to work on: Batch [X] — [BATCH NAME]

Key decisions already made:
[COPY FROM KEY DECISIONS SECTION BELOW]

Rules reminder:
- Explain everything before coding it
- Explain every single line
- Wait for my confirmation between batches
- If I ask why — stop and explain fully

Begin Batch [X] now.
```

---

## Key Decisions Log
UPDATE THIS AFTER EVERY BATCH

```
Batch 0:  Installed via Homebrew: Node v26.8.1 + npm 11.19.0, Docker Desktop 4.89.0
          (engine verified with a working hello-world container run), ngrok 3.39.11.
          VS Code extensions: Python + Pylance were already present, Docker/Containers
          newly installed. Git 2.50.1 and Homebrew were pre-existing. System Python is
          3.14.7, not the 3.11 the stack specifies — plan is to use pyenv in Batch 1 to
          get an isolated Python 3.11 for the backend virtual environment, without
          removing or affecting the system 3.14 install.
Batch 1:  Installed pyenv (brew) + Python 3.11.9 (pyenv install, NOT added to shell
          profile — used only via direct path ~/.pyenv/versions/3.11.9/bin/python3.11
          to avoid affecting system Python 3.14 or any other project). Created backend/
          and frontend/ folder structure per the layout in this file. Created backend/
          venv/ virtual environment using that 3.11.9 interpreter. Installed into venv:
          fastapi 0.141.1, uvicorn 0.52.4, sqlalchemy 2.0.52, alembic 1.19.1,
          pydantic 2.13.5 (see backend/requirements.txt for full frozen list). Wrote
          backend/app/main.py with a GET /health endpoint returning {"status":"ok"}.
          Verified working at http://localhost:8000/health and http://localhost:8000/docs
          via `./venv/bin/uvicorn app.main:app --reload --port 8000` run from backend/.
Batch 2:  Added psycopg2-binary (Postgres driver) and pydantic-settings to venv.
          Created backend/.env + .env.example (DATABASE_URL matches docker-compose
          credentials: postgres/postgres/buildboard) and backend/.gitignore (excludes
          venv/ and .env). Created backend/docker-compose.yml running postgres:16
          on localhost:5432 with a named volume (buildboard_pgdata) for persistence;
          started via `docker compose up -d` from backend/. Created app/config.py
          (pydantic Settings reading .env) and app/database.py (SQLAlchemy engine,
          SessionLocal, Base, get_db dependency). Created 4 SQLAlchemy models under
          app/models/: Repo, WorkflowRun, Job, FailureAnalysis, matching the schema
          in this file, with foreign keys repo_id->repos.id and run_id->workflow_runs.id.
          Initialized Alembic (backend/alembic/), wired env.py to use Base.metadata
          and settings.database_url. Generated + applied first migration
          (8ea237f1f185_create_initial_tables) creating all 4 tables plus Alembic's
          own alembic_version tracking table — verified via `docker exec
          backend-postgres-1 psql -U postgres -d buildboard -c "\dt"`. Updated
          GET /health in main.py to run a real query (SELECT 1) through
          Depends(get_db), verified at http://localhost:8000/health returning
          {"status":"ok","database":"connected"}.
Batch 3:  Installed GitHub CLI (gh) via brew, authenticated as SidR-13. Created a
          private test repo SidR-13/buildboard-test-repo (separate from the main
          BuildBoard project repo) with a minimal .github/workflows/test.yml
          (triggers on push) used purely to generate real workflow_run webhook events.
          Installed ngrok, authenticated with account token. Free ngrok accounts now
          require a reserved static domain (created via dashboard.ngrok.com/domains,
          Agent Endpoint, Public) rather than a random URL - ours is
          https://stereo-amnesty-powdered.ngrok-free.dev, tunneling to localhost:8000.
          Generated a real GITHUB_WEBHOOK_SECRET (in backend/.env, not committed).
          Built app/core/security.py (verify_github_signature - HMAC-SHA256 over raw
          body bytes, hmac.compare_digest for timing-safe comparison) and
          app/routers/webhooks.py (POST /webhooks/github - verifies signature first,
          rejects with 401 if invalid, then for event type "workflow_run" finds-or-
          creates the Repo by full_name and finds-or-creates the WorkflowRun by
          github_run_id, updating status/conclusion/timestamps/duration on each of
          the 3 lifecycle deliveries GitHub sends - requested/in_progress/completed -
          so they collapse into a single row per run). Registered the webhook via
          `gh api repos/SidR-13/buildboard-test-repo/hooks` subscribed to
          workflow_run events, pointed at the ngrok URL. Verified end-to-end: pushed
          a commit to the test repo, confirmed via `docker exec backend-postgres-1
          psql` that the resulting workflow_runs row has status=completed,
          conclusion=success, duration_seconds=8, and the repos row was auto-created
          correctly from the webhook payload.
Batch 4:  Built app/services/metrics_service.py with three functions: calculate_pass_rate,
          calculate_average_duration, calculate_health_score, and detect_flaky_builds.
          Added GET /repos/{repo_id}/metrics endpoint (app/routers/metrics.py,
          registered in main.py) accepting an optional ?days= query param (default 30),
          returning 404 if repo_id doesn't exist. Did this batch in 3 phases, discussing
          the reasoning and tradeoffs before writing each piece. Full discussion +
          decisions + why, in the order they came up:

          PHASE 1 - Pass rate & average duration:
          - Pass rate formula: successes / (successes + failures) over a time window.
            Decision: exclude "cancelled" and "skipped" conclusions from BOTH the
            numerator and denominator entirely (not counted as failures). Why: those
            runs were never actually tested to completion, so counting them as
            failures would unfairly punish a repo for someone cancelling a run, not
            for broken code.
          - Average duration: discussed whether to average over successful runs only,
            or over all completed runs (success+failure+timed_out). Decision:
            successful runs only. Why: failure durations are bimodal, not just noisy -
            a build failing at step 1 (bad syntax) exits in 5 seconds, one failing at
            step 8 (flaky integration test) exits in 4 minutes. Averaging these with
            successes doesn't measure "typical build time," it blends three unrelated
            distributions together. "Avg build time" on a dashboard should mean "how
            long does it normally take," which only full successful runs represent.
          - Time window anchor: discussed started_at vs completed_at for the "last N
            days" filter. For real CI runs the two are nearly identical (minutes
            apart), so this mattered more for semantic correctness than actual query
            results. Decision: completed_at. Why: both metrics already restrict to
            completed/successful rows, so every row being measured already has a
            completed_at - anchoring the window on it means "our health over builds
            that resolved in the last 30 days," which is what a dashboard user
            actually wants to know ("how are we doing lately"), vs started_at's
            "what did we kick off lately."

          PHASE 2 - Health score:
          - Discussed whether duration should factor into the score at all, since
            "slow" has no universal threshold across different repos/pipelines (a
            monorepo test suite vs. a one-file lint check). Decision: score duration
            by TREND (current window's avg vs. the prior equal-length window), not by
            an absolute "under X seconds = good" threshold, since there's no
            threshold that generalizes across repos.
          - Formula decided: health_score = pass_rate - duration_penalty, where
            duration_penalty = 0 if duration held steady or improved, else
            min(20, pct_increase_vs_previous_window). Why capped at 20: pass_rate
            should dominate the score (it's the real broken-vs-working signal); a
            worsening duration trend can only ever shave a currently-100%-passing
            repo down to 80 ("healthy but slower"), never make it look broken.
          - health_score returns None (not 0 or a crash) when there's no run data at
            all in the window - a brand new repo with zero data isn't "unhealthy,"
            it's "no data yet," and those need to be visually distinguishable on a
            dashboard.

          PHASE 3 - Flaky build detection:
          - Detection heuristic: group workflow_runs by (branch, commit_sha); flag
            any group containing both a "success" and a "failure" conclusion. Why
            this signal: if the exact same commit produced both outcomes with no
            code change in between, the most likely explanation is non-determinism
            (flaky test/infra), not a real bug getting fixed.
          - Discussed restricting detection to the repo's default branch only (to cut
            noise from people iterating on feature branches) and adding a
            time-proximity requirement between the failure and success (same-day
            pairs are a stronger flake signal than pairs weeks apart, which smell
            more like environment drift than test flakiness). Decision: skip both
            refinements for v1 - ship the simple all-branches, no-time-filter version,
            since we don't yet store each repo's default_branch and there's no
            obviously-correct time threshold; revisit only if real data proves noisy.
          - Discussed whether flaky_count should reduce health_score (a third
            penalty, like duration). Decision: no - report flaky_count as a fully
            separate metric alongside health_score, not folded into the formula. Why:
            a health score built from 3 blended heuristics gets hard to reason about;
            two independently-meaningful numbers ("Health: 92, Flaky builds: 2") beat
            one opaque blended number.
          - IMPORTANT LIMITATION DISCOVERED while trying to test this against a real
            re-run: our webhook handler (webhooks.py, from Batch 3) finds-or-creates
            WorkflowRun BY github_run_id and overwrites conclusion in place on every
            delivery - which was the right call in Batch 3 for collapsing GitHub's 3
            lifecycle deliveries (requested/in_progress/completed) into one row per
            run. But it means clicking "Re-run failed jobs" in the GitHub UI - the
            most common real-world flaky-recovery action - keeps the SAME
            github_run_id, so the original failure gets silently overwritten with the
            new success before flaky detection ever sees two conclusions for that
            row. Our detection can therefore only catch genuinely separate run_ids
            that happen to share a commit_sha, not the everyday re-run pattern.
          - Discussed fixing this properly (store run_attempt, insert a new row per
            attempt instead of updating in place - needs a migration) vs. treating it
            as a known limitation. Explicitly discussed "are we overcomplicating this
            project" as a meta-question. Decision: treat as a documented limitation,
            do NOT change the schema now. Why: this is a portfolio project for
            interviews, not a production system - the interview story and resume
            bullets don't even mention flaky detection, while 8+ batches of genuinely
            interview-relevant work remain (Docker on ARM, AWS, WebSockets, the CI/CD
            pipeline itself). Hardening a footnote metric isn't worth delaying that.
            If asked in an interview, "the current version tracks one record per run
            ID; tracking retry attempts separately is a known next step" is a
            perfectly strong answer and arguably shows better judgment than having
            over-built this prematurely.
          - Validated the detection logic itself (not the unreachable-via-real-rerun
            path) by manually inserting a synthetic second workflow_runs row sharing
            the real row's branch+commit_sha but with conclusion=failure and a
            different github_run_id, confirming GET /repos/.../metrics correctly
            returned flaky_count:1 with the right branch/commit_sha, then deleted the
            synthetic row to restore real data.

          Verified end-to-end against the real Batch 3 test repo data after cleanup:
          GET /repos/de3b3ab6-a0ce-4c12-a7b4-8bea68c5a3ba/metrics returns
          {"health_score":100.0,"pass_rate":100.0,"total_runs":1,"successful_runs":1,
          "avg_duration_seconds":8.0,"flaky_count":0,"flaky_commits":[]}.
Batch 5:  Built the Claude AI failure-analysis pipeline in 3 phases. Full discussion +
          decisions + why, in the order they came up:

          PHASE 1 - Fetching logs from GitHub (app/services/github_service.py):
          - Discussed two GitHub API options: per-job logs (needs github_job_id,
            which we don't have since webhooks.py only subscribes to workflow_run
            events, not workflow_job events - the jobs table is unpopulated) vs.
            per-run logs (a ZIP of every job's log, needs only github_run_id, which
            every WorkflowRun already has). Decision: per-run ZIP endpoint. Why:
            avoids subscribing to a second webhook event type and populating an
            unused table just for this - real scope creep for this batch. Tradeoff
            accepted: "last 50 lines" means the last 50 lines of all jobs
            concatenated together, not per-job - a non-issue for our single-job test
            workflow.
          - fetch_run_logs(owner, repo, github_run_id, tail_lines=50) downloads the
            ZIP via httpx (installed fresh - not previously in requirements.txt),
            follows GitHub's redirect to blob storage, unzips in-memory (io.BytesIO,
            no temp file), concatenates every .txt entry's lines, returns only the
            last 50 as one joined string.
          - Why only the last 50 lines (two real reasons, not just "tokens cost
            money"): (1) cost/latency - full CI logs can be thousands of lines,
            almost entirely noise, and the actual error is almost always at the
            tail since that's where execution stopped; (2) signal-to-noise for
            Claude itself - burying 10 relevant error lines inside 5,000 lines of
            successful setup output dilutes the context and risks the model
            referencing irrelevant earlier output, not just costing more.
          - BUG FOUND DURING TESTING: first test call failed with 401 Unauthorized.
            Root cause: backend/.env's GITHUB_TOKEN was still the literal untouched
            placeholder string from .env.example ("your-github-personal-access-
            token") - it had never actually been set to a real token, and an
            earlier check of "does the key exist" was mistakenly read as "does it
            have a real value." Confirmed via `gh api .../logs` succeeding with the
            gh CLI's own separately-stored token while our .env token failed.
            Explicitly decided NOT to reuse/read the gh CLI's token (kept separate
            per instruction) - instead created a dedicated fine-grained PAT scoped
            to ONLY buildboard-test-repo with Actions:Read-only permission (tighter
            scope than gh's broad repo+workflow scopes), pasted directly into
            backend/.env by the user (never shared in chat), then restarted uvicorn
            (required - pydantic-settings only reads .env once at process startup,
            --reload does not pick up .env changes, only .py file changes). Verified
            working after restart - fetch_run_logs correctly pulled real log text
            including runner setup info and the actual "Hello from BuildBoard test
            workflow" output line.

          PHASE 2 - Prompt engineering + Claude call (app/services/claude_service.py):
          - Discussed how to get STRUCTURED output from Claude reliably, since
            failure_analyses has two separate DB columns (claude_analysis,
            suggested_fix) that plain free-text prose can't be reliably split into.
            Decision: use Claude's tool-use (function-calling) with a forced
            tool_choice, not prompting for JSON and parsing text. Why: tool use with
            a JSON Schema (report_failure_analysis: root_cause + suggested_fix, both
            required) guarantees valid, correctly-shaped output from the API itself
            - no regex/text-parsing fragility, no risk of the model chatting back
            free text instead of the two fields we need.
          - Decision: check `AI_MOCK` FIRST, before constructing the Anthropic
            client at all, so a placeholder ANTHROPIC_API_KEY (still unset - real
            key not needed for this batch) never triggers a real network attempt.
            Mock response is explicitly prefixed "[MOCK]" in both fields, so a mock
            row can never be mistaken for real AI output later once this reaches a
            dashboard.
          - Added claude_model setting to config.py (default: Haiku), not
            hardcoded in claude_service.py. Why: matches the stack decision "Haiku
            for dev, Sonnet for demo" - makes the Batch 12 demo swap a one-line env
            var change (CLAUDE_MODEL=...) instead of a code change.
          - Installed the official `anthropic` Python SDK (fresh install, not
            previously in requirements.txt). Verified the mock path directly -
            returns the expected {"root_cause": ..., "suggested_fix": ...} dict
            with both required keys. Real-mode code path (the actual tools= /
            tool_choice= API call) was written per the documented Anthropic tool-
            use pattern but could not be tested this batch since AI_MOCK=true is
            correct/required per the cost-control rules - it will get its first
            real test in whichever batch turns AI_MOCK=false (Batch 12 demo prep,
            per the cost breakdown).

          PHASE 3 - Wiring it together (changes to app/routers/webhooks.py):
          - Discussed whether the webhook handler should wait for the log-fetch +
            Claude-call to finish before responding to GitHub. Decision: no - use
            FastAPI's BackgroundTasks so the webhook responds to GitHub immediately
            and the analysis runs after the response is sent. Why: GitHub expects a
            timely webhook response; blocking on 1-2 external API calls (slow in
            real mode) risks GitHub treating the delivery as failed/slow. Noted the
            specific FastAPI guarantee that makes this safe: background tasks run
            BEFORE a yield-dependency's cleanup code (get_db's `finally: db.close()`)
            executes, so reusing the same `db` session inside the background task
            is safe, not a use-after-close bug.
          - Discussed idempotency: GitHub can redeliver the same "completed" webhook
            more than once (e.g. if it thinks a delivery timed out). Decision: guard
            _generate_failure_analysis with a check for an existing FailureAnalysis
            row by run_id before doing any work, so a redelivered event can't create
            a duplicate row or trigger a second (costly, in real mode) API call pair.
          - _store_workflow_run now returns (repo, run) instead of None, so the
            route handler has what it needs (repo.owner, repo.name, run.* fields)
            to schedule the background task. Trigger condition kept narrow and
            explicit: only status=="completed" AND conclusion=="failure" (not
            cancelled/timed_out) - matches the batch plan's stated scope ("test with
            a real failed build").
          - Tested end-to-end against a REAL failed build, not a synthetic one:
            pushed a commit to the test repo (SidR-13/buildboard-test-repo) adding
            an `exit 1` step to .github/workflows/test.yml, waited for the real
            GitHub Actions run to complete with conclusion=failure, confirmed via
            `docker exec backend-postgres-1 psql`: the workflow_runs row stored
            correctly, and a failure_analyses row was auto-created by the
            background task with the correct run_id link, logs_snippet containing
            the real captured error line ("##[error]Process completed with exit
            code 1."), and the expected [MOCK] analysis/fix text. Also confirmed
            GET /repos/.../metrics correctly reflected the new failure
            (pass_rate/health_score dropped to 50.0, total_runs became 2,
            flaky_count stayed 0 since this failure is a different commit_sha than
            the earlier success, not a retry of the same one).
          - Discussed reverting the test repo's workflow back to always-succeeding
            now that failure-path testing is done (since GitHub emails on every
            failed run). Decision: leave the workflow failing for now, not
            necessary to revert - it's just a test fixture, doesn't affect
            BuildBoard's own code/data correctness, and having a mix of
            success/failure data may actually be useful for later batches (Batch 6
            WebSockets, Batch 8 charts) that benefit from non-uniform demo data.
            Can revert or push a fresh passing commit whenever a "healthy" baseline
            is needed for a specific later demo.
          - DEFERRED (not built this batch): GET /runs/{id}/analysis endpoint from
            the original API list. Decision: defer to whichever future batch builds
            the general read endpoints (GET /repos, GET /repos/{id}/runs, GET
            /runs/{id}) rather than build it alone now - it belongs with its
            sibling read endpoints, not bolted on in isolation. Verified the
            underlying data is correct via direct DB query in the meantime.
Batch 6:  Built live WebSocket updates in 3 phases. Full discussion + decisions + why,
          in the order they came up:

          PHASE 1 - Basic WebSocket endpoint (app/routers/ws.py):
          - WS /ws/{repo_id} added, accepts the connection (FastAPI/Starlette
            handles the HTTP-upgrade handshake automatically), loops on
            receive_text()/send_text() as a plain echo, catches WebSocketDisconnect
            to exit the loop cleanly instead of crashing when a client leaves.
            Purely proving the connect/receive/send/disconnect lifecycle before
            adding any real logic.
          - Verified with a real Python websockets client (not curl - can't speak
            WebSocket): connected, sent a message, got the echo back correctly.
            Also explicitly tested the disconnect path (client closes mid-session)
            and confirmed no traceback/error appears server-side - asked to double-
            check this specifically rather than assume the except block "must be
            fine" since it hadn't actually been exercised by the first test.

          PHASE 2 - Connection registry (app/services/websocket_service.py):
          - ConnectionManager class holds active_connections: dict[UUID,
            list[WebSocket]], keyed by repo_id, so a future broadcast reaches only
            the viewers of one specific repo, not every connected client anywhere.
            A single module-level `manager` instance is shared by every WebSocket
            connection (each its own async task) - this shared singleton is the
            whole point, since without it each connection would have an isolated
            registry unable to see any other connection to broadcast to.
          - disconnect() removes the specific socket from its repo's list and
            deletes the list entirely once empty, so the dict doesn't accumulate
            dead entries for repos nobody's watching.
          - Noted scope limitation on purpose (not a bug): this registry is
            in-process memory, so it only works correctly for a single backend
            instance. That's fine here because the AWS plan is explicitly one
            EC2 instance with no load balancer (ELB was already ruled out in the
            cost-control rules) - multiple instances behind a load balancer would
            need Redis pub/sub instead, which is out of scope for this project's
            actual deployment shape.
          - ws.py simplified to stop echoing (the app doesn't need the client to
            send anything, only to receive pushes) - the receive_text() call is
            kept only to block on and detect WebSocketDisconnect.
          - Verification hit a real gotcha worth remembering: added temporary
            [DEBUG] print() statements inside connect/disconnect to observe the
            registry from within the running server process (a separate test
            script can't see another process's in-memory state). First run showed
            NO output despite the code definitely executing - root cause was
            Python's stdout block-buffering when redirected to a file (our
            `uvicorn ... > file.log` setup), not a code bug. Fixed by adding
            flush=True to the temporary prints, confirmed correct behavior (2
            clients connect -> registry shows 2 viewers; disconnect one at a time
            -> correctly drops to 1, then to 0 with the repo's entry deleted), then
            removed the debug prints since they weren't meant to be permanent
            logging. Re-verified the FINAL cleaned-up code still worked correctly
            after removing them, rather than assuming the removal was safe -
            explicitly asked "did you check it?" and caught that only a health-
            check/reload check had been done, not a full re-run of the actual
            connect/disconnect test against the final code.

          PHASE 3 - Wiring live updates (changes to app/routers/webhooks.py):
          - manager.broadcast(repo.id, {...}) called right after _store_workflow_run
            for EVERY workflow_run webhook delivery, not just failures - GitHub
            sends 3 lifecycle deliveries per run (requested/in_progress/completed),
            so a live viewer sees the run's status progress in real time rather
            than only getting one final update.
          - Discussed whether broadcasting needed a BackgroundTask like Batch 5's
            Claude/GitHub calls. Decision: no, await it directly in the request
            path. Why: the distinguishing factor for needing a BackgroundTask is
            "is this slow/external" (true for Batch 5's API calls), not "is this
            async" - broadcasting to already-open local WebSocket connections is
            fast in-process I/O, safe to await inline.
          - Had to manually build the broadcast payload as plain JSON-safe types
            (str(run.id) etc.) rather than passing the ORM object directly. Why:
            Starlette's WebSocket.send_json uses plain json.dumps, which does NOT
            know how to serialize a UUID or datetime automatically (unlike some of
            FastAPI's other response-encoding paths) - would have raised
            TypeError at broadcast time if passed through directly.
          - Tested end-to-end against a REAL webhook delivery, not simulated: ran
            two separate Python WebSocket clients (tab-A, tab-B) connected to the
            same repo_id as a stand-in for two browser tabs (macOS's Terminal
            doesn't have real tabs to test with here, and this is the equivalent
            proof), then pushed a real commit to the test repo. Also used this
            same push to revert .github/workflows/test.yml back to passing
            (removing the `exit 1` from Batch 5's failure test) - resolving that
            batch's deferred "should we revert the test workflow" loose end in the
            same action. Confirmed via real background-task output: BOTH clients
            received all 3 identical lifecycle messages live (queued ->
            in_progress -> completed/success), with correct run data and duration
            in the final message - proving the registry correctly broadcasts to
            every viewer of a repo, not just one.
          - DEFERRED (not built this batch): GET /runs/{id}/analysis and the other
            general read endpoints (GET /repos, GET /repos/{id}/runs, GET
            /runs/{id}) - same deferred-from-Batch-5 decision, still pending
            whichever future batch builds out the general REST read layer.
Batch 7:  Scaffolded frontend/ with `npm create vite@latest frontend -- --template
          react-ts` (React 19, TS 6, Vite 8). Removed the placeholder empty
          frontend/src/ dirs from Batch 1 first (create-vite refuses non-empty
          targets). Installed Tailwind CSS v4 via `@tailwindcss/vite` (v4 uses a
          Vite plugin + `@theme` block in CSS instead of tailwind.config.js +
          PostCSS). Installed react-router-dom (client-side routing) and axios
          (HTTP client, per stack decision).

          DESIGN: user explicitly required the frontend look portfolio-quality,
          not generic/AI-default styling, since it's the demo surface for
          interviews (saved as a memory: buildboard-frontend-design-bar). Proposed
          and confirmed via a live preview page: Inter (UI text) + JetBrains Mono
          (code/commit-sha/branch text) via self-hosted @fontsource packages (no
          Google Fonts CDN dependency), dark near-black theme (zinc-family, not
          pure black), cyan accent (deliberately not indigo/purple - avoiding the
          most common "AI-generated UI" tell), semantic status colors separate
          from the accent (green=success, red=failure, amber=flaky/warning,
          zinc=cancelled, pulsing cyan=running). All defined as Tailwind v4
          @theme tokens in src/index.css (bg/surface/border/text/accent/
          success/failure/warning/neutral + muted variants), not one-off hex
          values in components. User then said this is "good and basic" and
          explicitly said not to keep iterating on frontend visuals further -
          backend is the priority; get the bar met once, then move fast.

          BACKEND GAP FOUND: building the Dashboard required GET /repos (list
          repos), which had never been built - Batches 5 and 6 both explicitly
          deferred all general REST read endpoints (GET /repos, GET /repos/{id}/
          runs, GET /runs/{id}, GET /runs/{id}/analysis) to "whichever future
          batch needs them first." That's this batch. Added app/routers/repos.py
          with GET /repos only (list id/owner/name/full_name/created_at, newest
          first) - the minimum needed for the Dashboard; the other deferred
          endpoints (GET /repos/{id}/runs, GET /runs/{id}, GET /runs/{id}/
          analysis) remain deferred to Batch 8, which needs them for the repo
          detail/build detail/failure-analysis views. Also added CORSMiddleware
          to main.py (missing entirely before this batch) scoped specifically to
          allow_origins=["http://localhost:5173"] (not "*") - without it the
          browser blocks all frontend->backend requests since they're different
          origins (5173 vs 8000).

          FRONTEND STRUCTURE BUILT:
          - src/services/types.ts - Repo and RepoMetrics TS interfaces, hand-
            matched to the exact JSON shapes GET /repos and GET /repos/{id}/
            metrics return (health_score/pass_rate typed as `number | null`,
            matching Batch 4's decision that a repo with no data returns null,
            not 0).
          - src/services/api.ts - one axios instance (baseURL from
            import.meta.env.VITE_API_URL, Vite's client-exposed env convention -
            only VITE_-prefixed vars reach the browser bundle) + two thin typed
            wrapper functions (fetchRepos, fetchRepoMetrics), rather than calling
            axios directly from components.
          - src/components/HealthScore.tsx - circular score badge, color-coded
            by threshold (>=90 success/green, >=70 warning/amber, else failure/
            red), renders "—" (not "0") when score is null - keeping Batch 4's
            "no data yet" vs "unhealthy" distinction visible on screen.
          - src/components/RepoCard.tsx - clickable card (react-router Link to
            /repos/:id) showing name, full_name, HealthScore badge, pass rate,
            avg build duration, run count, and a flaky-count pill shown only
            when flaky_count > 0 - metrics prop is nullable so a card still
            renders (with "—" placeholders) if that repo's metrics fetch fails,
            rather than the whole dashboard breaking.
          - src/pages/Dashboard.tsx - fetches repos, then fetches every repo's
            metrics concurrently via Promise.all (not sequential awaits), with
            each individual metrics fetch independently caught (.catch(() =>
            null)) so one bad repo doesn't take down the page. Explicit 3-state
            UI: loading (pulsing skeleton cards), error (backend unreachable -
            red banner), empty (zero repos - "No repos yet" message), success
            (real cards) - per the design-bar decision to build real states, not
            just the happy path.
          - src/pages/RepoDetail.tsx, BuildDetail.tsx - stub pages (route +
            back-link only) so the router structure from CLAUDE_CONTEXT.md's
            folder layout exists now; real content (charts, live WebSocket
            updates, Claude failure analysis) is explicitly Batch 8's job.
          - src/App.tsx - BrowserRouter with 3 routes: "/" -> Dashboard,
            "/repos/:repoId" -> RepoDetail, "/runs/:runId" -> BuildDetail.

          Verified: `npx tsc -b` clean (0 errors - Vite's dev server itself only
          transpiles via esbuild and does NOT type-check, so this was a separate
          explicit check), `npx oxlint` clean (0 warnings), and end-to-end in a
          real browser (not just curl, since curl can't render JS) - user
          confirmed the Dashboard renders the header and a real card for
          buildboard-test-repo with actual health score/pass rate/avg build/runs
          numbers pulled live from Postgres through the new GET /repos + existing
          GET /repos/{id}/metrics endpoints.

          Frontend env: created frontend/.env + .env.example (VITE_API_URL,
          VITE_WS_URL per the vars already documented in this file) and added
          .env to frontend/.gitignore (mirrors the backend's pattern, even
          though these particular values aren't secret).
Batch 8:  Built out RepoDetail and BuildDetail (real content, replacing Batch 7's
          stubs) in 4 phases.

          PHASE 1 - Missing backend read endpoints (still deferred from Batches
          5/6, same pattern as Batch 7's GET /repos gap):
          - Added GET /repos/{repo_id}/runs to app/routers/repos.py - lists a
            repo's WorkflowRuns, newest-first, default limit=50 (a repo can
            accumulate many runs; charts/timeline don't need unlimited history
            per call). 404s if repo_id doesn't exist (same pattern as
            /metrics).
          - Added new app/routers/runs.py: GET /runs/{run_id} (single run) and
            GET /runs/{run_id}/analysis (that run's FailureAnalysis). The
            analysis endpoint has two distinct 404 reasons on purpose - "Run
            not found" (bad id, real error) vs "No analysis for this run" (run
            exists but succeeded, or Batch 5's background task hasn't finished
            yet - a normal/expected state, not an error) - so the frontend can
            tell these apart and not show an error banner on every successful
            build.
          - Verified all three directly against real data (a real
            success/failure/success trio of runs already in the DB): runs list
            correct, single-run fetch correct, analysis fetch returns the real
            [MOCK] analysis from Batch 5 for the failed run and correctly 404s
            "No analysis for this run" for a successful one.

          PHASE 2 - RepoDetail: build history + Recharts charts:
          - Installed recharts. Two charts, both fed by GET /repos/{id}/runs
            (which returns newest-first - reversed client-side to chronological
            for left-to-right chart reading):
            - Build duration: LineChart of duration_seconds per run (only runs
              with a non-null duration - in-progress/cancelled runs excluded).
            - Pass/fail by build: discussed a "rolling pass rate over time"
              line (closer to the literal batch-plan wording) vs. a per-run bar
              chart - decided bar chart, because with only 3 real runs in the
              data a smoothed rate line would show almost no visible trend and
              would look broken/placeholder-ish. Each bar colored green/red by
              that run's actual conclusion (Cell-level fill, not just bar
              height) - noted as a minor simplification that any non-"success"
              completed run (e.g. a future "cancelled") would render red/fail-
              colored too, acceptable given the "don't over-engineer, backend is
              the priority" instruction from Batch 7.
          - New src/components/BuildTimeline.tsx - clickable list of runs
            (commit sha, branch, status dot+label, duration), links each row to
            /runs/{id}. Handles the in-progress case (status != "completed",
            conclusion still null) with a distinct pulsing accent dot rather
            than crashing on an unmapped status.
          - Verified end-to-end in browser (not just curl): user clicked from
            Dashboard into the real repo and confirmed both charts + timeline
            render correctly with real data (3 builds, correct colors).

          PHASE 3 - WebSocket live updates on RepoDetail (wires into the
          WS /ws/{repo_id} endpoint already built in Batch 6):
          - New src/hooks/useWebSocket.ts. First version returned a
            `lastMessage` state value with a separate useEffect in RepoDetail
            reacting to it - oxlint's react(set-state-in-effect) rule flagged
            this as an unnecessary extra render cascade. Refactored to a
            callback-based API instead: useWebSocket(url, onMessage) calls
            onMessage directly from the socket's onmessage handler, so a
            message update is one render, not two. The callback itself is
            stored in a ref (updated via a no-dependency-array effect, not
            during render - a second oxlint rule, react(refs), flags writing
            ref.current directly in the render body) so the connect/reconnect
            effect only depends on `url`, not on a fresh inline function
            identity every render.
          - RepoDetail merges incoming { event: "run_update", run: {...} }
            messages into its `runs` state by upserting on id - existing runs
            get their status/conclusion/duration_seconds updated in place
            (preserving started_at/completed_at, which aren't part of the
            broadcast payload), brand-new run ids get prepended. Matches
            exactly what Batch 6's webhooks.py broadcasts (confirmed by
            reading that code directly rather than guessing the shape).
          - Small green/pulsing "Live" vs. gray "Offline" badge in the header,
            driven by the hook's `connected` state - makes the live connection
            visibly obvious during a demo, not just an invisible background
            behavior.
          - Verified with a REAL webhook round-trip, not simulated: pushed a
            real commit to SidR-13/buildboard-test-repo (a trivial test file,
            then removed it in a follow-up commit once verification was done)
            while the RepoDetail page was open in the browser. Confirmed via
            server log that all 3 real webhook lifecycle deliveries arrived
            through the ngrok tunnel, the new run appeared in the DB, and -
            confirmed by the user via screenshot, not just assumed from server
            logs - the new build appeared live in the timeline and both charts
            with zero manual page refresh.
          - Hit transient "Rendered more hooks than during the previous
            render" / ref-related console errors during active mid-edit HMR
            (React Fast Refresh getting confused while the hook's signature
            was being actively changed across saves) - did NOT assume this was
            fine on its own; restarted the Vite dev server for a clean state
            and had the user hard-refresh (not just rely on HMR) to confirm
            the final code has zero console errors before treating Phase 3 as
            verified.

          PHASE 4 - BuildDetail: run summary + Claude failure analysis:
          - Fetches GET /runs/{id}; only additionally fetches
            GET /runs/{id}/analysis when conclusion === "failure" (no wasted
            request/expected-404 noise for successful builds).
          - Three states for the analysis section, matching the backend's two-
            404-reasons design: not shown at all for non-failed runs, "Analysis
            not available yet" message when the run failed but no
            FailureAnalysis row exists yet (background task still running),
            and the full analysis (root cause / suggested fix / scrollable
            monospace log snippet) once present. The [MOCK] prefix from Batch
            5's mock response displays as-is with no special-casing needed -
            naturally makes it obvious this is placeholder dev data.
          - Verified end-to-end in browser against the real failed run
            (d5ca4da): user screenshot confirmed the run card, failure badge,
            and full [MOCK] root cause/suggested fix/log snippet all render
            correctly with real data from the database.

          Final check across the whole frontend: `npx tsc -b` clean (0 errors)
          and `npx oxlint` clean (0 warnings) - both actively used to catch and
          fix 2 real issues during this batch (the hooks/refs warnings above),
          not just run as a rubber-stamp at the end.
Batch 9:  Containerized the backend. Covered concepts first (images vs containers
          vs volumes, why Docker solves "works on my machine" for the eventual
          EC2 deploy), then built and extensively tested:

          - backend/Dockerfile: multi-stage build. Builder stage (python:3.11-
            slim, matches the exact pyenv interpreter version used locally)
            installs deps via `pip install --user` (so only ~/.local, not pip's
            build cache, gets copied to the final stage). Final stage copies
            only that installed-packages dir + app/ + alembic/ + alembic.ini
            (deliberately NOT venv/ or .env). PYTHONUNBUFFERED=1 set explicitly
            - directly ties back to a real Batch 6 bug (stdout block-buffering
            hid debug prints when output was redirected/piped, which is always
            true for a containerized process). CMD uses exec form (JSON array)
            not shell form, so uvicorn runs as PID 1 and receives real OS
            signals correctly (matters for Batch 11's zero-downtime deploys).
            --host 0.0.0.0 required in the CMD - 127.0.0.1 would make the
            container unreachable from outside itself. Every FROM line uses
            --platform=linux/amd64 per the standing Mac-ARM instruction - the
            concrete reason for THIS specific project: Batch 10's target EC2
            t2.micro is x86_64, not ARM, so an image built without this flag
            would run fine locally (Docker transparently emulates on Apple
            Silicon) but fail to run at all on the real deploy target.
          - Docker's own BuildKit linter flagged
            "FromPlatformFlagConstDisallowed" (suggests passing --platform via
            the build command instead of hardcoding in FROM, for portability
            across architectures). Deliberately kept as-is: unlike a
            general-purpose image, this one only ever needs to run in exactly
            one place (the amd64 EC2 instance), so "always amd64,
            unconditionally" is correct here, not a shortcut - documented so
            this isn't mistaken for an unnoticed warning later.
          - backend/.dockerignore: excludes venv/, .env, __pycache__/, .git/ -
            keeps secrets from ever reaching the build context/an image layer,
            and keeps the (large, irrelevant-to-the-container) local venv out
            of the build.
          - backend/docker-compose.yml: added a `backend` service alongside
            the existing `postgres` one (from Batch 2). Covered container
            networking explicitly: services on the same Compose network reach
            each other BY SERVICE NAME, not "localhost" - the existing
            .env's DATABASE_URL (localhost:5432, correct for host-run uvicorn
            talking to Postgres's published port) would NOT work from inside
            the backend container, since "localhost" there means the backend
            container itself, which has no Postgres listening on it. Fixed by
            overriding DATABASE_URL specifically in compose's `environment:`
            block (postgres:5432, the service name) - Compose applies
            `environment:` after `env_file:`, so this wins without needing to
            touch the actual .env file used for host-run dev.
          - Added a healthcheck to postgres (pg_isready) + depends_on:
            condition: service_healthy on backend - by default depends_on only
            waits for the postgres CONTAINER to start, not for Postgres itself
            to finish initializing and accept connections (a real, well-known
            race condition), which could otherwise crash the backend on first
            boot.
          - platform: linux/amd64 also added to the postgres service for
            consistency with the standing instruction, but noted honestly that
            it's not actually load-bearing for Postgres specifically - the
            stack decision already has production Postgres running as AWS RDS,
            not a Docker container, so this local postgres container never
            actually gets deployed anywhere.

          EXTENSIVE TESTING (user explicitly asked to test thoroughly, not just
          confirm it starts):
          - `docker build` succeeded cleanly (only the expected, understood
            BuildKit linter warning above - no real errors).
          - `docker compose up -d --build`: watched the actual startup
            sequence in the output and confirmed the healthcheck dependency
            worked for real - log showed postgres "Waiting" -> "Healthy" ->
            ONLY THEN backend "Starting", not both starting concurrently.
          - Proved container networking concretely rather than just trusting
            the config: docker compose exec'd into the running backend
            container and (1) printed the actual DATABASE_URL env var seen
            inside it, (2) resolved the "postgres" hostname via Python's own
            socket.gethostbyname to a real container IP, and (3) attempted a
            raw socket connection to localhost:5432 FROM INSIDE the backend
            container and confirmed it fails with Connection refused - proving
            the "localhost doesn't work in a container, service name does"
            explanation wasn't just theoretical.
          - Data persistence verified: GET /repos and GET /repos/{id}/metrics
            against the containerized backend returned the exact same real
            data (test repo, 5 runs, health_score 80.0) that existed before
            containerization - the named volume from Batch 2 survived a full
            `docker compose down` + rebuild + `up` cycle.
          - Full real-world round-trip test (not simulated): pushed a real
            commit to SidR-13/buildboard-test-repo while the RepoDetail page
            was open in the browser, with the backend running ENTIRELY inside
            Docker for the first time. Confirmed via container logs that all 3
            webhook lifecycle deliveries (through the same ngrok tunnel,
            unchanged) reached the containerized backend, the run landed in
            the DB, AND - confirmed by the user via screenshot, not assumed -
            the WebSocket live-update pipeline still worked identically
            through the container, updating both charts and the timeline with
            no manual refresh. Removed the trigger file with a follow-up
            commit afterward, same pattern as Batch 8.
          - Restart resilience: `docker compose restart` - noted this command
            does NOT re-enforce the depends_on/healthcheck ordering the way
            `up` does (both containers restarted concurrently) - confirmed the
            backend still recovered correctly anyway, since its DB connection
            is lazy/per-request via SQLAlchemy rather than a blocking startup
            check.
          - Proved the container does NOT hot-reload on code changes (unlike
            the host --reload workflow): temporarily added a test field to the
            /health response, confirmed the ALREADY-RUNNING container's
            response did NOT include it (code is a frozen copy from build
            time), then ran `docker compose up -d --build backend` and
            confirmed the new field DID appear. Reverted the test change and
            rebuilt again to leave the code clean.

          WORKFLOW DECISION for the rest of the project: asked the user
          whether to keep working against the Docker container day-to-day, or
          switch back to host-run `uvicorn --reload` for faster iteration and
          treat `docker compose up --build` as a periodic "does the packaged
          version still work" check. User chose the latter (recommended
          option) - switched back to host-run uvicorn for Batches 10+
          (Postgres stays running in Docker as before; only the backend
          service itself was stopped and uvicorn restarted on the host).
Batch 10: Deployed BuildBoard's backend to real AWS infrastructure. Full sequence:

          ACCOUNT SETUP: Created a new AWS account (had to choose the "Paid Plan"
          during signup over the newer "Free Plan" trial tier - Free Plan explicitly
          lacks "access to all AWS services" and auto-deletes after 6 months; Paid
          Plan is just AWS's standard non-trial account type, not an actual charge,
          and keeps the same 12-month free-tier hours as any AWS account). Enabled
          "Receive Billing Alerts" + "AWS Free Tier alerts" in Billing preferences,
          then created a CloudWatch billing alarm (buildboard-billing-alert,
          threshold >$5, us-east-1 - billing metrics only exist in that region
          regardless of deploy region) with an SNS email subscription. Hit a real
          snag: first subscription was created with the wrong email - fixed by
          creating a second (correct) subscription and confirming it, and left the
          original wrong-email one as permanently "Pending confirmation" (harmless,
          since SNS never delivers to an unconfirmed endpoint - console wouldn't
          allow deleting a pending subscription, not worth fighting).

          IAM: Created buildboard-cli IAM user (NOT root) with three AWS-managed
          policies attached directly: AmazonEC2FullAccess, AmazonRDSFullAccess,
          AmazonEC2ContainerRegistryFullAccess - deliberately narrower than
          AdministratorAccess. Generated a CLI access key pair, installed AWS CLI
          v2 via Homebrew, ran `aws configure` (user entered keys directly in their
          own terminal, never pasted into chat - same precaution as the Batch 5
          GitHub PAT). Verified via `aws sts get-caller-identity`.

          EC2: Created key pair (buildboard-key, private key at
          ~/.ssh/buildboard/buildboard-key.pem, chmod 400), security group
          (buildboard-sg: port 22 from the user's own IP only, ports 80/443 open
          publicly, port 8000 open publicly ONLY temporarily until Nginx was in
          place - closed at the end of this batch). Launched a t2.micro instance
          on the latest Amazon Linux 2023 AMI (looked up live via
          `ec2 describe-images`, not hardcoded, since AMI IDs change; had to use
          this instead of the simpler SSM parameter-store lookup because
          buildboard-cli's scoped permissions correctly don't include ssm:GetParameter
          - a good demonstration of least-privilege working as intended). Allocated
          and associated an Elastic IP (100.58.57.71) so the address survives
          restarts. Verified SSH access.

          RDS: Created a dedicated RDS security group (port 5432 inbound ONLY from
          the EC2 security group, not the public internet - mirrors the Batch 9
          "service-to-service trust, not public exposure" principle) and a DB
          subnet group spanning 3 AZs. Launched db.t3.micro PostgreSQL, 20GB
          storage, NOT publicly accessible, backup retention 0 (unnecessary for a
          portfolio project). Master password generated locally via `openssl rand`,
          never typed in chat. Verified connectivity with a raw Python socket test
          run FROM INSIDE the EC2 instance (proving the security-group scoping
          works, not just assumed).

          ECR + IMAGE DEPLOY: Created ECR repo buildboard-backend (scanOnPush
          enabled). Built the existing Batch 9 Dockerfile locally with
          --platform linux/amd64 (this is the actual concrete payoff of that
          Batch-9 flag - the image now runs correctly on the real x86_64 EC2
          target). Pushed to ECR.

          IAM ROLE FOR EC2 (rather than copying CLI keys onto the server):
          discussed and chose to create a separate IAM role (buildboard-ec2-role,
          AmazonEC2ContainerRegistryReadOnly policy only) and attach it to the
          instance via an instance profile, so the EC2 machine can pull from ECR
          with zero credential files stored on it. Hit two expected
          least-privilege walls in a row, both correct AWS behavior: (1)
          buildboard-cli couldn't create the IAM role/instance profile itself
          (a scoped-down user can't grant itself broader IAM powers - had to
          create the role via console, logged in as root/account owner); (2)
          even after the role existed, attaching it to the instance failed with
          a missing iam:PassRole permission (a deliberate separate AWS guardrail
          against privilege escalation via role-reuse) - fixed by adding one
          narrow inline policy to buildboard-cli granting iam:PassRole scoped to
          that ONE role's ARN, not IAM broadly.

          Pulled the image on EC2 via the instance role (no `docker login` keys),
          built a production .env by copying the local backend/.env and swapping
          only DATABASE_URL to point at the RDS endpoint (scp'd directly,
          contents never printed to chat/terminal output). Ran the container
          (--restart unless-stopped, port 8000). Ran `alembic upgrade head`
          against the fresh RDS database via `docker exec`. Verified
          GET /health returned {"status":"ok","database":"connected"} from a
          real external curl request, not just from inside EC2.

          DOMAIN + NGINX + SSL: Needed a real domain for Certbot (Let's Encrypt
          cannot issue certs for bare IPs, a protocol-level rule, not an AWS
          limitation). Chose DuckDNS (free, zero cost, no expiry) over buying a
          domain or skipping HTTPS, per explicit "don't want to spend anything"
          preference - buildboard-siddhesh.duckdns.org pointed at the Elastic IP.
          Installed Nginx on EC2, wrote a reverse-proxy config
          (/etc/nginx/conf.d/buildboard.conf) proxying port 80 -> 127.0.0.1:8000,
          INCLUDING explicit Upgrade/Connection headers for WebSocket support -
          called out specifically because BuildBoard has the Batch 6 WS
          endpoint, and a plain HTTP-only proxy config would have silently
          broken live updates without erroring anywhere obvious. Installed
          Certbot (dnf, not pip - available directly in AL2023's repos) with
          its Nginx plugin, ran `certbot --nginx` non-interactively, which
          auto-edited the Nginx config to add a real Let's Encrypt certificate
          (expires 2026-12-06, auto-renewal already scheduled) and an
          HTTP->HTTPS redirect. Verified both the HTTPS response and the 301
          redirect. Closed port 8000 in the security group afterward, verified
          via a real timeout (exit code 28) that it's now actually unreachable
          from outside, not just visually removed from the rule list - the
          public surface is now only Nginx on 80/443.

          FINAL STATE: https://buildboard-siddhesh.duckdns.org is BuildBoard's
          live production URL - real HTTPS, backend on EC2, database on RDS,
          image versioned in ECR, EC2/RDS left running continuously (both
          exactly the free-tier-covered instance types, so 24/7 uptime costs
          $0 for 12 months - no reason to stop them between sessions).

          QUICK-REFERENCE (for the LinkedIn post / diagram doc later, so these
          don't need to be re-dug-out of prose):
          ```
          Production URL:       https://buildboard-siddhesh.duckdns.org
          Elastic IP:            100.58.57.71
          EC2 instance ID:       i-0079fa054800c0e67 (t2.micro, Amazon Linux 2023)
          EC2 security group:    sg-07043a79b2e933b5b (buildboard-sg)
          RDS instance ID:       buildboard-db (db.t3.micro, Postgres)
          RDS endpoint:          buildboard-db.cy7cgymi6pku.us-east-1.rds.amazonaws.com:5432
          RDS security group:    sg-077550b8eccfba595 (buildboard-rds-sg)
          ECR repo:              834287106965.dkr.ecr.us-east-1.amazonaws.com/buildboard-backend
          IAM CLI user:          buildboard-cli (EC2/RDS/ECR full access only)
          IAM EC2 role:          buildboard-ec2-role (ECR read-only, attached via
                                  instance profile - no keys stored on the server)
          SSH key:               ~/.ssh/buildboard/buildboard-key.pem -> ec2-user
          Domain provider:       DuckDNS (free) -> buildboard-siddhesh.duckdns.org
          SSL:                   Let's Encrypt via Certbot, auto-renewing,
                                  expires 2026-12-06 (renews before then)
          Billing alarm:         buildboard-billing-alert, threshold >$5, us-east-1
          ```

          NOTE: user found full first-principles depth (per this file's own
          "explain everything" rule) too much to absorb batch-by-batch during
          this specific batch. Decision (saved to memory): keep remaining
          batches' explanations brief/practical; build one dedicated
          concepts+flowcharts learning document covering the whole project
          at the end (Batch 12 territory), rather than teaching deeply inline
          per batch.
Batch 11: [fill in after completing]
Batch 11: [fill in after completing]
Batch 12: [fill in after completing]
```

---

## What BuildBoard Does (User Flow)
```
1. User connects their GitHub repos to BuildBoard
2. GitHub sends a webhook event every time a
   workflow run starts, completes, or fails
3. BuildBoard receives the event and verifies
   it using HMAC-SHA256 signature
4. Stores the build data in PostgreSQL
5. Computes health metrics — pass rate,
   average duration, flaky test detection
6. If a build fails: fetches logs from GitHub API,
   sends to Claude, gets AI explanation + fix
7. Dashboard shows live updates via WebSockets
8. User sees which builds are healthy, which are
   broken, and exactly why they broke
```

---

## Project Folder Structure
```
buildboard/
├── CLAUDE_CONTEXT.md         ← This file
├── backend/
│   ├── app/
│   │   ├── main.py           ← FastAPI app entry point
│   │   ├── config.py         ← Environment variables
│   │   ├── database.py       ← PostgreSQL connection
│   │   ├── models/           ← Database table definitions
│   │   │   ├── __init__.py
│   │   │   ├── repo.py
│   │   │   ├── workflow_run.py
│   │   │   └── job.py
│   │   ├── schemas/          ← Request/Response shapes
│   │   │   ├── __init__.py
│   │   │   └── webhook.py
│   │   ├── routers/          ← API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── webhooks.py
│   │   │   ├── repos.py
│   │   │   ├── metrics.py
│   │   │   └── ws.py
│   │   ├── services/         ← Business logic
│   │   │   ├── __init__.py
│   │   │   ├── github_service.py
│   │   │   ├── metrics_service.py
│   │   │   ├── claude_service.py
│   │   │   └── websocket_service.py
│   │   └── core/
│   │       ├── __init__.py
│   │       └── security.py   ← HMAC webhook verification
│   ├── alembic/              ← Database migrations
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── requirements.txt
│   ├── .env
│   ├── .env.example
│   └── alembic.ini
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── RepoCard.tsx
│   │   │   ├── BuildTimeline.tsx
│   │   │   ├── HealthScore.tsx
│   │   │   ├── FailureAnalysis.tsx
│   │   │   └── LiveBadge.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── RepoDetail.tsx
│   │   │   └── BuildDetail.tsx
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts
│   │   │   └── useMetrics.ts
│   │   └── services/
│   │       └── api.ts
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── .github/
│   └── workflows/
│       └── deploy.yml
└── README.md
```

---

## Database Schema
```
repos
- id UUID PRIMARY KEY
- owner VARCHAR          ← GitHub username or org
- name VARCHAR           ← repo name
- full_name VARCHAR      ← owner/name
- webhook_secret VARCHAR ← for verifying events
- created_at TIMESTAMP

workflow_runs
- id UUID PRIMARY KEY
- repo_id UUID FK → repos
- github_run_id BIGINT   ← GitHub's own run ID
- workflow_name VARCHAR
- branch VARCHAR
- commit_sha VARCHAR
- status VARCHAR         ← queued/in_progress/completed
- conclusion VARCHAR     ← success/failure/cancelled
- started_at TIMESTAMP
- completed_at TIMESTAMP
- duration_seconds INT

jobs
- id UUID PRIMARY KEY
- run_id UUID FK → workflow_runs
- github_job_id BIGINT
- name VARCHAR
- status VARCHAR
- conclusion VARCHAR
- started_at TIMESTAMP
- completed_at TIMESTAMP

failure_analyses
- id UUID PRIMARY KEY
- run_id UUID FK → workflow_runs
- logs_snippet TEXT      ← last 50 lines of logs
- claude_analysis TEXT   ← AI explanation
- suggested_fix TEXT
- created_at TIMESTAMP
```

---

## API Endpoints
```
POST /webhooks/github        ← Receive GitHub events
GET  /repos                  ← List all monitored repos
GET  /repos/{id}/metrics     ← Health score, rates, trends
GET  /repos/{id}/runs        ← Build history
GET  /runs/{id}              ← Single build detail
GET  /runs/{id}/analysis     ← Claude failure analysis
WS   /ws/{repo_id}          ← WebSocket live updates
GET  /health                 ← Health check endpoint
```

---

## Environment Variables
```
# Backend .env (never commit this file)
ANTHROPIC_API_KEY=your-claude-api-key
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/buildboard
REDIS_URL=redis://localhost:6379
GITHUB_WEBHOOK_SECRET=generate-a-random-string
GITHUB_TOKEN=your-github-personal-access-token
JWT_SECRET=generate-a-random-string
AI_MOCK=true                 ← ALWAYS true during development

# Frontend .env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

---

## Cost Breakdown

### Development Phase — $0
```
Python + FastAPI       free
PostgreSQL (Docker)    free
Redis (Docker)         free
React + Vite           free
GitHub API             free (5000 req/hour)
ngrok free tier        free (1 tunnel, sessions)
Claude API (mock)      $0 — AI_MOCK=true during dev
All dev tools          free
```

### Claude API Cost
```
AI_MOCK=true (development):     $0.00
Haiku testing (50 analyses):    ~$0.50
Sonnet demo (20 analyses):      ~$1.00
Total Claude cost:              ~$1.50
Current budget remaining:       ~$3.18
Result: No top-up needed
```

### AWS Free Tier (First 12 Months)
```
EC2 t2.micro:      750 hrs/month free = 24/7 for free
RDS db.t3.micro:   750 hrs/month free = 24/7 for free
ECR storage:       500MB free (image is ~200-300MB)
Data transfer:     15GB outbound free
S3:                5GB free (if needed)

NOT free — do not use:
Elastic Load Balancer:  ~$16/month  ← skip
ElastiCache Redis:      ~$12/month  ← run Redis on EC2 instead
NAT Gateway:            ~$32/month  ← skip
Route 53:               $0.50/month ← optional, use EC2 IP instead
```

### After 12-Month Free Tier
```
EC2 t2.micro:      ~$8.50/month
RDS db.t3.micro:   ~$12.50/month
ECR:               ~$0.03/month
Total:             ~$21/month
```

### Total Expected Cost To Build BuildBoard
```
Development:    $0.00
Claude API:     ~$1.50
AWS:            $0.00 (free tier)
Domain/SSL:     $0.00 (Certbot = free SSL)
All tools:      $0.00
GRAND TOTAL:    ~$1.50
```

### Cost Control Rules
```
1. Set $5 AWS billing alert BEFORE anything else
2. Build everything locally first — zero AWS cost
3. Deploy to AWS only when project is complete
4. Stop RDS when not actively demoing
5. Delete everything after internship offers arrive
6. NEVER leave AI_MOCK=false during development
```

---

## Where Claude Will Struggle (Know These In Advance)

### Batch 9 — Docker on Mac ARM
Claude sometimes generates Dockerfiles that fail on
Apple Silicon (M1/M2/M3). When this happens tell Claude:
```
I am on Apple Silicon Mac.
Add --platform linux/amd64 to all Docker commands.
Use FROM --platform=linux/amd64 in the Dockerfile.
```

### Batch 10 — AWS Console Navigation
AWS UI changes frequently. Claude's button locations
may be outdated. Use AWS CLI instead:
```
Tell Claude: Use AWS CLI commands, not console UI steps.
```

### Batch 11 — SSH + CI/CD
Many moving parts — SSH keys, security groups, GitHub
secrets. Most debugging-heavy batch. Be patient.
Come back to claude.ai if stuck.

### Long Sessions — Context Loss
Claude forgets earlier decisions after long sessions.
Signs it is happening:
- Wrong port numbers
- Regenerating existing files
- Contradicting earlier decisions
Fix: Start a new session using the template above.

---

## Batch Plan

### BATCH 0 — Mac Setup
Install on fresh Mac:
- Homebrew — Mac package manager
- Git — version control
- Node.js + npm — for React frontend
- Docker Desktop — for PostgreSQL and Redis locally
- VS Code extensions — Python, Pylance, Docker
- ngrok — exposes local server for webhook testing
Verify: Every tool shows a version number

### BATCH 1 — Project Foundation
- Create folder structure
- Python virtual environment (understand why it exists)
- Install FastAPI, SQLAlchemy, Alembic, Pydantic, uvicorn
- main.py with one working health check endpoint
- Understand what FastAPI is and why we chose it
- Run server, verify in browser at localhost:8000/health

### BATCH 2 — Database Design
- Understand what SQLAlchemy is and why ORMs exist
- Start PostgreSQL via Docker (understand what Docker does)
- Create all database models
- Alembic migrations (understand why migrations exist)
- Connect FastAPI to PostgreSQL
- Verify connection works

### BATCH 3 — GitHub Webhooks
- Understand webhooks vs polling (why webhooks are better)
- Understand HMAC-SHA256 verification (why we need it)
- Set up ngrok for local testing
- Register webhook on a real GitHub repo
- Receive and verify first real event
- Store event in database and verify

### BATCH 4 — Metrics Engine
- Understand what metrics we need and why
- Build health score algorithm (explain the math)
- Calculate pass/fail rates over time windows
- Average build duration trending
- Flaky test detection algorithm
- Verify metrics with real data

### BATCH 5 — Claude AI Integration
- Understand GitHub API log fetching
- Understand why only last 50 lines (token limits)
- Build failure analysis prompt (explain engineering)
- Parse Claude structured response
- Store analysis in database
- Test with a real failed build

### BATCH 6 — WebSockets
- Understand WebSockets vs HTTP (why we need them)
- Understand the WebSocket handshake
- Implement WebSocket endpoint in FastAPI
- Connection registry (one socket per repo viewer)
- Push live build updates to connected clients
- Test with two browser tabs simultaneously

### BATCH 7 — React Frontend Foundation
- Set up React + TypeScript + Vite + Tailwind
- Understand why TypeScript over JavaScript
- API service layer with axios + typed responses
- Dashboard with repo list and health scores
- Understand every npm package installed

### BATCH 8 — Charts and Live Updates
- Recharts build time trend line
- Pass/fail rate over time chart
- WebSocket connection for live updates
- Build history timeline per repo
- Failure detail page with Claude analysis

### BATCH 9 — Docker
- Understand what Docker is and why it exists
- Understand images vs containers vs volumes
- Multi-stage Dockerfile for backend (every line explained)
- docker-compose.yml (every line explained)
- Run entire stack with docker-compose up
- Container networking (how containers talk to each other)
- IMPORTANT: Use --platform linux/amd64 for Mac ARM

### BATCH 10 — AWS Deployment
- Set $5 billing alert FIRST before anything else
- Understand EC2 — what it is and why we need it
- Understand RDS — managed vs self-hosted database
- Understand ECR — Docker image registry
- Launch EC2 t2.micro (free tier)
- Set up RDS PostgreSQL db.t3.micro (free tier)
- Push Docker image to ECR
- Deploy container on EC2
- Nginx reverse proxy (explain what a reverse proxy is)
- SSL via Certbot (free HTTPS)
- Use AWS CLI not console UI

### BATCH 11 — CI/CD Pipeline
- GitHub Actions workflow on push to main
- Build Docker image
- Push to ECR
- SSH into EC2 and deploy new image
- Zero-downtime rolling update (explain what this means)
- Verify full deployment end to end

### BATCH 12 — Polish + Resume
- README with architecture diagram
- Screenshots of live dashboard
- Resume bullet points (3 strong bullets)
- Make GitHub repo public
- Add to all resume versions in Overleaf

---

## Current Status
[x] Batch 0  — Mac Setup
[x] Batch 1  — Project Foundation
[x] Batch 2  — Database Design
[x] Batch 3  — GitHub Webhooks
[x] Batch 4  — Metrics Engine
[x] Batch 5  — Claude AI Integration
[x] Batch 6  — WebSockets
[x] Batch 7  — React Frontend Foundation
[x] Batch 8  — Charts and Live Updates
[x] Batch 9  — Docker
[x] Batch 10 — AWS Deployment
[ ] Batch 11 — CI/CD Pipeline
[ ] Batch 12 — Polish + Resume

---

## Probability Of Success Per Batch
```
Batch 0-2:   95% smooth — standard setup
Batch 3-6:   90% smooth — FastAPI/webhooks well known
Batch 7-8:   90% smooth — React well within knowledge
Batch 9:     75% smooth — Docker on Mac ARM tricky
Batch 10:    70% smooth — AWS has moving parts
Batch 11:    65% smooth — SSH + CI/CD most complex
Batch 12:    99% smooth — polish is easy
```
When something fails in Batch 9-11 — come back to
claude.ai for diagnosis. VS Code Claude builds,
claude.ai diagnoses.

---

## Interview Story (Memorize This)
```
"I built BuildBoard — a real-time CI/CD monitoring
platform I use on my own projects.

The core is event-driven. GitHub sends webhook events
signed with HMAC-SHA256 every time a workflow runs.
I verify the signature — same cryptographic pattern
I used in FinFlow for webhook delivery — then process
the event asynchronously and push live updates to
connected clients via WebSockets.

When a build fails I fetch the last 50 lines of logs
from the GitHub API and send them to Claude with the
commit context. It returns a structured root cause
analysis and suggested fix displayed inline in the
dashboard.

The whole thing runs in Docker containers on AWS EC2
with RDS PostgreSQL for the database. My GitHub
Actions pipeline builds a new Docker image on every
push, pushes to ECR, and does a rolling deploy to
EC2 with zero downtime."
```

---

## Resume Bullets (Add After Batch 12)
```
BuildBoard | Python, FastAPI, React, PostgreSQL,
Redis, Docker, AWS EC2/ECR/RDS, Claude API, WebSockets
github.com/SidR-13/buildboard | [live URL]

• Built a real-time CI/CD monitoring platform processing
  GitHub webhook events via HMAC-SHA256 verified endpoints,
  computing build health scores from PostgreSQL time-series
  data and pushing live updates to clients via WebSockets

• Containerized entire backend with multi-stage Docker builds,
  pushed images to AWS ECR, and deployed on EC2 with Nginx
  reverse proxy and zero-downtime rolling updates via
  GitHub Actions CI/CD pipeline

• Integrated Claude API to analyze build failure logs and
  generate structured root cause analysis with suggested
  fixes — reducing mean time to resolution for failing builds
```

---

## How To Use This File

### Starting First Session Ever:
```
Read CLAUDE_CONTEXT.md completely before doing anything.

We are building BuildBoard — a CI/CD pipeline monitor.
I am on a brand new Apple Silicon MacBook.
Only Python is installed. Start from scratch.

Rules:
- Explain everything before coding it
- Explain every single line of code
- Wait for confirmation between batches
- If I ask why — stop and explain fully

Start with BATCH 0 — Mac Setup.
For each tool: explain what it is, why we need it,
exact install command, how to verify it worked.
Begin now.
```

### Starting Any Subsequent Session:
```
Read CLAUDE_CONTEXT.md completely before doing anything.

We are building BuildBoard — a CI/CD pipeline monitor.
I am on Apple Silicon Mac — use --platform linux/amd64
for all Docker commands.

Completed batches: [list them]
Current batch: Batch [X] — [name]

Key decisions made so far:
[paste from Key Decisions Log above]

Rules:
- Explain everything before coding it
- Explain every single line
- Wait for my confirmation between batches

Continue with Batch [X] now.
```

### When Stuck On An Error:
Come to claude.ai and paste:
```
I am building BuildBoard — CI/CD monitor on AWS.
I am on Batch [X].
Here is the error I am getting:
[paste full error]
Here is the file causing the issue:
[paste the file]
What is wrong and why?
```
