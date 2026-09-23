# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

`airbyte-prefect` is a port of [`prefect-airbyte`](https://github.com/PrefectHQ/prefect-airbyte).
Releases below cover this package only; for changes before the port, see the upstream
project's history.

## Unreleased

### Fixed

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
