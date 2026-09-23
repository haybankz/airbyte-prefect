# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

`airbyte-prefect` is a port of [`prefect-airbyte`](https://github.com/PrefectHQ/prefect-airbyte).
Releases below cover this package only; for changes before the port, see the upstream
project's history.

## Unreleased

### Added

### Changed

### Fixed

### Removed

## 1.2.0

Released on September 23, 2026.

### Added

- `JobStatus`, an enum of the statuses Airbyte reports for a sync job. The
  `JOB_STATUS_*` names remain as aliases - [#18](https://github.com/haybankz/airbyte-prefect/pull/18)
- Published API reference at <https://haybankz.github.io/airbyte-prefect>, built from the
  docstrings in this repository, linked from the README - [#19](https://github.com/haybankz/airbyte-prefect/pull/19)

### Changed

- `AirbyteSyncResult.job_status` is typed `JobStatus` rather than a `Literal` listing
  four of Airbyte's six statuses. It still compares equal to, and serialises as, the
  plain status string - [#18](https://github.com/haybankz/airbyte-prefect/pull/18)

### Fixed

- `AirbyteSync.fetch_result()` no longer raises a `ValidationError` for a job that is
  `running` or that finished `incomplete`. `JobRun` permits calling it without
  `wait_for_completion()` first, and both statuses were missing from the result model - [#18](https://github.com/haybankz/airbyte-prefect/pull/18)
- `AirbyteSync.wait_for_completion()` no longer raises `IndexError` when Airbyte has not
  recorded an attempt for the job yet. The first poll fires immediately after the
  trigger, when `attempts` can still be empty - [#18](https://github.com/haybankz/airbyte-prefect/pull/18)
- `AirbyteSync.fetch_result()` reports the record count from the job payload it fetches,
  rather than from state that only `wait_for_completion()` populates. Called on its own
  it previously reported `0` regardless of what the job had moved - [#18](https://github.com/haybankz/airbyte-prefect/pull/18)

## 1.1.0

Released on September 23, 2026.

### Added

- `max_wait_seconds` on `AirbyteConnection` and on the `trigger_sync` task, bounding how
  long a sync is polled before `AirbyteSyncJobTimeout` is raised. Defaults to `None`,
  which waits indefinitely as before - [#16](https://github.com/haybankz/airbyte-prefect/pull/16)

### Fixed

- Syncs no longer poll forever when an Airbyte job ends `incomplete`. That status is
  terminal but was absent from `terminal_job_statuses`, so the poll loop never exited.
  It is now treated as an unsuccessful terminal status and raises
  `AirbyteSyncJobFailed`, alongside `cancelled` and `failed` - [#16](https://github.com/haybankz/airbyte-prefect/pull/16)
- Block logos in the Prefect UI. Both `AirbyteServer` and `AirbyteConnection` pointed
  `_logo_url` at an image on Prefect's CDN that now returns `402 Payment Required`, so
  the blocks rendered without a logo - [#1](https://github.com/haybankz/airbyte-prefect/pull/1)
- Documentation build. Every page under `docs/` referenced the pre-rename
  `prefect_airbyte` module, and the Blocks Catalog filtered the Block registry on the
  same stale prefix, so it generated an empty catalog - [#1](https://github.com/haybankz/airbyte-prefect/pull/1)

### Changed

- Release workflow now publishes to PyPI through trusted publishing (OIDC) rather than a
  stored API token - [#1](https://github.com/haybankz/airbyte-prefect/pull/1)
- Test matrix moved to Python 3.10, 3.11 and 3.12, matching the declared classifiers - [#1](https://github.com/haybankz/airbyte-prefect/pull/1)

### Removed

- Workflows inherited from the upstream collection template that depended on PrefectHQ
  organisation secrets (`add-to-project`, `template-sync`) - [#1](https://github.com/haybankz/airbyte-prefect/pull/1)
- Google Analytics property from the docs configuration; it belonged to PrefectHQ - [#1](https://github.com/haybankz/airbyte-prefect/pull/1)

## 1.0.1

Released on October 29, 2025.

### Changed

- Lowered the minimum supported Python from 3.11 to 3.10.

## 1.0.0

Released on October 29, 2025.

First release of `airbyte-prefect`, a port of `prefect-airbyte` to Prefect 3.

### Changed

- **Breaking:** the distribution is now `airbyte-prefect` and the import package is
  `airbyte_prefect`. Replace `from prefect_airbyte...` with `from airbyte_prefect...`.
- **Breaking:** requires Prefect 3.2.1 or later, up from Prefect 2.13.5.
- Blocks use Pydantic v2 directly. The `pydantic.v1` compatibility shim that selected an
  import path based on the installed Pydantic version is gone, and `AirbyteServer` field
  metadata moved from `Field(example=...)` to `Field(examples=[...])`.
- `run_connection_sync` awaits `AirbyteConnection.trigger` and the `AirbyteSync` methods
  directly. The `.aio` workaround for the Prefect 2 deadlock between sync tasks and async
  flows is no longer needed.

### Removed

- Support for Prefect 2 and Pydantic v1.
