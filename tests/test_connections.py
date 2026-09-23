import pytest
from prefect.logging import disable_run_logger

from airbyte_prefect import exceptions as err
from airbyte_prefect.connections import (
    AirbyteConnection,
    AirbyteSyncResult,
    JobStatus,
    trigger_sync,
)


async def example_trigger_sync_flow(connection_id, airbyte_server=None, **kwargs):
    with disable_run_logger():
        return await trigger_sync.fn(
            airbyte_server=airbyte_server, connection_id=connection_id, **kwargs
        )


async def test_successful_trigger_sync(
    mock_successful_connection_sync_calls, airbyte_server, connection_id
):
    trigger_sync_result = await example_trigger_sync_flow(
        airbyte_server=airbyte_server, connection_id=connection_id
    )

    assert type(trigger_sync_result) is dict

    assert trigger_sync_result == {
        "connection_id": "e1b2078f-882a-4f50-9942-cfe34b2d825b",
        "status": "active",
        "job_status": "succeeded",
        "job_created_at": 1650644844,
        "job_updated_at": 1650644844,
    }


async def test_cancelled_trigger_manual_sync(
    mock_cancelled_connection_sync_calls, airbyte_server, connection_id
):
    with pytest.raises(err.AirbyteSyncJobFailed):
        await example_trigger_sync_flow(
            airbyte_server=airbyte_server, connection_id=connection_id
        )


async def test_connection_sync_inactive(
    mock_inactive_sync_calls, airbyte_server, connection_id
):
    with pytest.raises(err.AirbyteConnectionInactiveException):
        await example_trigger_sync_flow(
            airbyte_server=airbyte_server, connection_id=connection_id
        )


async def test_failed_trigger_sync(
    mock_failed_connection_sync_calls, airbyte_server, connection_id
):
    with pytest.raises(err.AirbyteSyncJobFailed):
        await example_trigger_sync_flow(
            airbyte_server=airbyte_server, connection_id=connection_id
        )


async def test_bad_connection_id(
    mock_bad_connection_id_calls, airbyte_server, connection_id
):
    with pytest.raises(err.ConnectionNotFoundException):
        await example_trigger_sync_flow(
            airbyte_server=airbyte_server, connection_id=connection_id
        )


async def test_failed_health_check(
    mock_failed_health_check_calls, airbyte_server, connection_id
):
    with pytest.raises(err.AirbyteServerNotHealthyException):
        await example_trigger_sync_flow(
            airbyte_server=airbyte_server, connection_id=connection_id
        )


async def test_get_job_status_not_found(
    mock_invalid_job_status_calls, airbyte_server, connection_id
):
    with pytest.raises(err.JobNotFoundException):
        await example_trigger_sync_flow(
            airbyte_server=airbyte_server, connection_id=connection_id
        )


async def test_trigger_sync_with_kwargs(
    mock_successful_connection_sync_calls, connection_id
):
    trigger_sync_result = await example_trigger_sync_flow(
        airbyte_server_host="localhost",
        airbyte_server_port=8000,
        connection_id=connection_id,
    )

    assert type(trigger_sync_result) is dict

    assert trigger_sync_result == {
        "connection_id": "e1b2078f-882a-4f50-9942-cfe34b2d825b",
        "status": "active",
        "job_status": "succeeded",
        "job_created_at": 1650644844,
        "job_updated_at": 1650644844,
    }


async def test_airbyte_connection_instantiation(airbyte_server, connection_id):
    connection = AirbyteConnection(
        airbyte_server=airbyte_server,
        connection_id=connection_id,
    )

    assert isinstance(connection, AirbyteConnection)
    assert connection.airbyte_server == airbyte_server
    assert str(connection.connection_id) == connection_id


async def test_incomplete_trigger_sync(
    mock_incomplete_connection_sync_calls, airbyte_server, connection_id
):
    """An `incomplete` job is terminal and unsuccessful, not something to poll on."""
    with pytest.raises(err.AirbyteSyncJobFailed, match="incomplete"):
        await example_trigger_sync_flow(
            airbyte_server=airbyte_server, connection_id=connection_id
        )


async def test_trigger_sync_times_out_on_never_finishing_job(
    mock_never_finishing_connection_sync_calls, airbyte_server, connection_id
):
    """`max_wait_seconds` bounds a job that never reaches a terminal status."""
    with pytest.raises(
        err.AirbyteSyncJobTimeout, match="did not reach a terminal status"
    ):
        await example_trigger_sync_flow(
            airbyte_server=airbyte_server,
            connection_id=connection_id,
            poll_interval_s=1,
            max_wait_seconds=1,
        )


async def test_fetch_result_on_a_running_job(
    mock_running_connection_sync_calls, airbyte_server, connection_id
):
    """`JobRun` allows fetch_result() before wait_for_completion().

    A job that is still `running` is a valid status for the result model.
    """
    connection = AirbyteConnection(
        airbyte_server=airbyte_server, connection_id=connection_id
    )

    sync = await connection.trigger()
    result = await sync.fetch_result()

    assert result.job_status == JobStatus.RUNNING


async def test_fetch_result_on_an_incomplete_job(
    mock_incomplete_connection_sync_calls, airbyte_server, connection_id
):
    connection = AirbyteConnection(
        airbyte_server=airbyte_server, connection_id=connection_id
    )

    sync = await connection.trigger()
    result = await sync.fetch_result()

    assert result.job_status == JobStatus.INCOMPLETE


async def test_fetch_result_reports_records_without_waiting(
    mock_running_connection_sync_calls, airbyte_server, connection_id
):
    """Records come from the fetched payload.

    Not from the state that only `wait_for_completion()` populates.
    """
    connection = AirbyteConnection(
        airbyte_server=airbyte_server, connection_id=connection_id
    )

    sync = await connection.trigger()
    result = await sync.fetch_result()

    assert result.records_synced == 17


async def test_fetch_result_on_a_job_with_no_attempts(
    mock_sync_calls_without_attempts, airbyte_server, connection_id
):
    """Airbyte may not have recorded an attempt yet; that is 0 records, not a crash."""
    connection = AirbyteConnection(
        airbyte_server=airbyte_server, connection_id=connection_id
    )

    sync = await connection.trigger()
    result = await sync.fetch_result()

    assert result.records_synced == 0


@pytest.mark.parametrize("status", list(JobStatus))
def test_airbyte_sync_result_accepts_every_job_status(status):
    result = AirbyteSyncResult(
        created_at=1650644844,
        job_status=status.value,
        job_id=45,
        records_synced=0,
        updated_at=1650644844,
    )

    assert result.job_status is status


def test_job_status_renders_as_a_plain_string():
    """Guards the __str__ override; without it logs read "JobStatus.SUCCEEDED"."""
    result = AirbyteSyncResult(
        created_at=1650644844,
        job_status="succeeded",
        job_id=45,
        records_synced=0,
        updated_at=1650644844,
    )

    assert f"{result.job_status}" == "succeeded"
    assert str(result.job_status) == "succeeded"
    assert result.job_status == "succeeded"
    assert result.model_dump(mode="json")["job_status"] == "succeeded"
