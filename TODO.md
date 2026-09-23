# TODO

Improvements identified while repairing CI. Split by whether the item is visible to
someone who `pip install`s `airbyte-prefect` and writes flows against it, or only to
contributors working inside this repo.

Twelve of the fifteen items are user-facing, and six of those produce a hang, a crash,
or a wrong number. Items 1–7 are the focused first pass.

## User / developer-facing

### Breaks or hangs their flow

- [ ] **1. `incomplete` is missing from `terminal_job_statuses`** — `airbyte_prefect/connections.py:29` ([#2](https://github.com/haybankz/airbyte-prefect/issues/2))

  The set is `{cancelled, failed, succeeded}`, but the code's own comments at
  `connections.py:159` and `:237` list Airbyte's statuses as
  `pending┃running┃incomplete┃failed┃succeeded┃cancelled`. A job ending `incomplete`
  matches neither the terminal set nor the failure branch, so `wait_for_completion`
  polls forever. There is no overall deadline to break out of it either — add a
  `max_wait_seconds` alongside the fix.

- [ ] **2. `IndexError` on a job with no attempts yet** — `airbyte_prefect/connections.py:233` ([#3](https://github.com/haybankz/airbyte-prefect/issues/3))

  `job_info["attempts"][-1]["attempt"]` runs on the first poll, which fires immediately
  after the trigger, before Airbyte has necessarily recorded an attempt. The test
  fixtures always contain one attempt, so the suite never reaches this.

- [ ] **3. `export_configuration` swallows non-404 errors** — `airbyte_prefect/client.py:100` ([#4](https://github.com/haybankz/airbyte-prefect/issues/4))

  The handler only re-raises inside `if e.response.status_code == 404`. A 500 or 403
  falls off the end of the `except` block and the function returns `None` while
  annotated `-> bytes`.

- [ ] **4. `trigger_sync` falls through unrecognized connection statuses** — `airbyte_prefect/connections.py:143` ([#5](https://github.com/haybankz/airbyte-prefect/issues/5))

  An `if`/`elif`/`elif` over three known statuses with no `else`. Anything Airbyte adds
  causes the task to "succeed" returning nothing.

- [ ] **6. `AirbyteSyncResult.job_status` is too narrow** — `airbyte_prefect/connections.py:200` ([#7](https://github.com/haybankz/airbyte-prefect/issues/7))

  `Literal["succeeded", "failed", "pending", "cancelled"]`. The `JobRun` interface
  permits calling `fetch_result()` without `wait_for_completion()`, which can hand it
  `running` or `incomplete` and raise a `ValidationError`.

- [ ] **7. Three undeclared runtime dependencies** — `requirements.txt` ([#8](https://github.com/haybankz/airbyte-prefect/issues/8))

  Only `prefect>=3.2.1` is declared, but the code imports `httpx` directly
  (`client.py:7`), `pydantic` (`server.py:6`, `connections.py:12`) and
  `typing_extensions` (`connections.py:13`). These resolve today only because Prefect
  happens to pull them in. Declare them. While there, `typing_extensions.Literal` can
  become `typing.Literal` now that the floor is Python 3.10.

### Wrong data

- [ ] **5. `records_synced` under-reports retried syncs** — `airbyte_prefect/connections.py:233` ([#6](https://github.com/haybankz/airbyte-prefect/issues/6))

  Reads only `attempts[-1]`, so a sync that retried reports the final attempt's records
  rather than the total. That number is what users branch on downstream — the README
  example feeds it straight into a dbt trigger.

### Public API surface

- [ ] **11. Typo in a public exception name** — `airbyte_prefect/exceptions.py:37` ([#9](https://github.com/haybankz/airbyte-prefect/issues/9))

  `AirbyeConnectionDeprecatedException` is missing the `t`. Callers have to reproduce
  the typo in their `except` clauses. `connections.py:351` already documents the
  correctly spelled name, so code and docs disagree. Rename and keep an alias.

- [ ] **8. No `py.typed` marker** ([#10](https://github.com/haybankz/airbyte-prefect/issues/10))

  The package is fully annotated but ships no PEP 561 marker, so every consumer's type
  checker treats it as untyped.

- [ ] **14. Only the legacy Airbyte Configuration API is supported** ([#11](https://github.com/haybankz/airbyte-prefect/issues/11))

  Everything targets `/api/v1/connections/sync` and `/jobs/get` with basic auth. Newer
  Airbyte exposes a public API under `/api/public/v1` with different auth, and Airbyte
  Cloud needs client-credential OAuth, which this package cannot do at all. The largest
  piece of work here, and the one that decides whether the package works against current
  Airbyte.

### Reliability and load on their infrastructure

- [ ] **12. Three HTTP clients and three health checks per sync** — `airbyte_prefect/server.py:78` ([#12](https://github.com/haybankz/airbyte-prefect/issues/12))

  `get_client()` builds a fresh `AirbyteClient`, and therefore a fresh
  `httpx.AsyncClient` with its own connection pool, on every call; `__aenter__` runs a
  health check each time. `trigger()`, `wait_for_completion()` and `fetch_result()` each
  do this. Hold one client for the lifetime of the `AirbyteSync`.

- [ ] **13. No retry on transient failures** ([#13](https://github.com/haybankz/airbyte-prefect/issues/13))

  A single 502 or dropped connection during a multi-hour sync poll aborts the whole
  flow. Transport-level retries plus backoff on 5xx would make long syncs far more
  reliable.

### Both audiences

- [ ] **9. `CHANGELOG.md` does not exist** ([#14](https://github.com/haybankz/airbyte-prefect/issues/14))

  Users consult it on upgrade; contribution step 6 in both `README.md` and
  `MAINTAINERS.md` instructs contributors to add an entry to it.

## Non-dev-facing

Only visible inside this repo.

- [ ] **10. `CODEOWNERS` points at a team that does not exist here** — `.github/CODEOWNERS`

  `* @PrefectHQ/open-source`, left over from the port. Review auto-assignment silently
  does nothing.

- [ ] **15. `mypy` never runs**

  It sits in `requirements-dev.txt` but is wired into neither CI nor pre-commit. Either
  add it or drop the dependency.

- [ ] **16. Packaging predates `pyproject.toml`**

  `setup.py` plus `setup.cfg` plus 677 lines of vendored `versioneer.py`. Consumers
  never notice; contributors deal with it constantly.
