import pytest
from prefect import flow

from airbyte_prefect.connections import AirbyteConnection, AirbyteSyncResult
from airbyte_prefect.exceptions import (
    AirbyteConnectionUnknownStatusException,
    AirbyteSyncJobFailed,
    AirbyteSyncJobTimeout,
)
from airbyte_prefect.flows import run_connection_sync

expected_airbyte_sync_result = AirbyteSyncResult(
    created_at=1650644844,
    job_status="succeeded",
    job_id=45,
    records_synced=0,
    updated_at=1650644844,
)


async def test_run_connection_sync_standalone_success(
    airbyte_server, airbyte_connection, mock_successful_connection_sync_calls
):

    result = await run_connection_sync(airbyte_connection=airbyte_connection)

    assert result == expected_airbyte_sync_result


async def test_run_connection_sync_standalone_fail(
    airbyte_server, airbyte_connection, mock_failed_connection_sync_calls, caplog
):

    with pytest.raises(AirbyteSyncJobFailed):
        await run_connection_sync(airbyte_connection=airbyte_connection)


async def test_run_connection_sync_standalone_cancel(
    airbyte_server, airbyte_connection, mock_cancelled_connection_sync_calls
):

    with pytest.raises(AirbyteSyncJobFailed):
        await run_connection_sync(airbyte_connection=airbyte_connection)


async def test_run_connection_sync_standalone_status_updates(
    airbyte_server, airbyte_connection, mock_successful_connection_sync_calls, caplog
):
    airbyte_connection.status_updates = True
    await run_connection_sync(airbyte_connection=airbyte_connection)

    assert "Job 45 succeeded" in caplog.text


async def test_run_connection_sync_subflow_synchronously(
    airbyte_server, airbyte_connection, mock_successful_connection_sync_calls
):
    @flow
    def airbyte_sync_sync_flow():
        return run_connection_sync(airbyte_connection=airbyte_connection)

    result = airbyte_sync_sync_flow()

    assert result == expected_airbyte_sync_result


async def test_run_connection_sync_subflow_asynchronously(
    airbyte_server, airbyte_connection, mock_successful_connection_sync_calls
):
    @flow
    async def airbyte_sync_sync_flow():
        return await run_connection_sync(airbyte_connection=airbyte_connection)

    result = await airbyte_sync_sync_flow()

    assert result == expected_airbyte_sync_result


async def test_run_connection_sync_raises_on_incomplete_job(
    airbyte_server, airbyte_connection, mock_incomplete_connection_sync_calls
):
    """An `incomplete` job is terminal and unsuccessful, not something to poll on."""
    with pytest.raises(AirbyteSyncJobFailed, match="incomplete"):
        await run_connection_sync(airbyte_connection=airbyte_connection)


async def test_run_connection_sync_times_out_on_never_finishing_job(
    airbyte_server,
    connection_id,
    mock_never_finishing_connection_sync_calls,
):
    """`max_wait_seconds` bounds a job that never reaches a terminal status."""
    connection = AirbyteConnection(
        airbyte_server=airbyte_server,
        connection_id=connection_id,
        poll_interval_s=1,
        max_wait_seconds=1,
    )

    with pytest.raises(AirbyteSyncJobTimeout, match="did not reach a terminal status"):
        await run_connection_sync(airbyte_connection=connection)


async def test_run_connection_sync_waits_indefinitely_by_default(
    airbyte_connection,
):
    """The bound is opt-in, so existing connections keep their old behaviour."""
    assert airbyte_connection.max_wait_seconds is None


async def test_run_connection_sync_on_an_unknown_connection_status(
    airbyte_server, connection_id, mock_unknown_status_sync_calls
):
    """The flow must surface the status error, not an AttributeError.

    `trigger()` previously fell through every branch and returned `None`, so the
    next line raised `'NoneType' object has no attribute 'wait_for_completion'`.
    """
    connection = AirbyteConnection(
        airbyte_server=airbyte_server, connection_id=connection_id
    )

    with pytest.raises(AirbyteConnectionUnknownStatusException):
        await run_connection_sync(airbyte_connection=connection)
