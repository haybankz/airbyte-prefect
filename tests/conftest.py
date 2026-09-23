from copy import deepcopy

import pytest
from httpx import Response
from prefect.testing.utilities import prefect_test_harness

from airbyte_prefect.connections import AirbyteConnection
from airbyte_prefect.server import AirbyteServer


@pytest.fixture(scope="session", autouse=True)
def prefect_db():
    """
    Sets up test harness for temporary DB during test runs.
    """
    with prefect_test_harness():
        yield


@pytest.fixture
def respx_mock(respx_mock):
    """
    Let calls to Prefect's ephemeral API through.

    respx intercepts every httpx request, including the ones the Prefect
    client makes to the temporary server started by `prefect_test_harness`.
    Airbyte is mocked on `localhost`, so passing `127.0.0.1` through leaves
    those routes untouched.
    """
    respx_mock.route(host="127.0.0.1").pass_through()
    return respx_mock


@pytest.fixture
def airbyte_server():
    return AirbyteServer()


@pytest.fixture
def connection_id():
    return "e1b2078f-882a-4f50-9942-cfe34b2d825b"


@pytest.fixture
def airbyte_connection(airbyte_server, connection_id):
    return AirbyteConnection(airbyte_server=airbyte_server, connection_id=connection_id)


@pytest.fixture
def airbyte_trigger_sync_response(connection_id) -> dict:
    return {
        "connectionId": connection_id,
        "status": "active",
        "job": {"id": 45, "createdAt": 1650311569, "updatedAt": 1650311585},
    }


@pytest.fixture
def airbyte_good_health_check_response() -> dict:
    return {"available": True}


@pytest.fixture
def airbyte_bad_health_check_response() -> dict:
    return {"available": False}


@pytest.fixture
def airbyte_get_connection_response_json(connection_id) -> dict:
    return {
        "connectionId": connection_id,
        "name": "File <> Snowflake Demo",
        "namespaceDefinition": "destination",
        "namespaceFormat": "${SOURCE_NAMESPACE}",
        "prefix": "",
        "sourceId": "6054b03b-a9bd-4090-96a7-08076f066975",
        "destinationId": "c5ad053e-5741-4774-a60c-f976fe95c4dd",
        "operationIds": [],
        "syncCatalog": {
            "streams": [
                {
                    "stream": {
                        "name": "epidemic_stats",
                        "jsonSchema": {
                            "type": "object",
                            "$schema": "http://json-schema.org/draft-07/schema#",
                            "properties": {
                                "key": {"type": ["string", "null"]},
                                "date": {"type": ["string", "null"]},
                                "new_tested": {"type": ["number", "null"]},
                                "new_deceased": {"type": ["number", "null"]},
                                "total_tested": {"type": ["number", "null"]},
                                "new_confirmed": {"type": ["number", "null"]},
                                "new_recovered": {"type": ["number", "null"]},
                                "total_deceased": {"type": ["number", "null"]},
                                "total_confirmed": {"type": ["number", "null"]},
                                "total_recovered": {"type": ["number", "null"]},
                            },
                        },
                        "supportedSyncModes": ["full_refresh"],
                        "sourceDefinedCursor": None,
                        "defaultCursorField": [],
                        "sourceDefinedPrimaryKey": [],
                        "namespace": None,
                    },
                    "config": {
                        "syncMode": "full_refresh",
                        "cursorField": [],
                        "destinationSyncMode": "overwrite",
                        "primaryKey": [],
                        "aliasName": "epidemic_stats",
                        "selected": True,
                    },
                }
            ]
        },
        "schedule": None,
        "status": "active",
        "resourceRequirements": None,
    }


@pytest.fixture
def airbyte_get_inactive_connection_response(
    airbyte_get_connection_response_json,
) -> dict:
    airbyte_get_connection_response_json["status"] = "inactive"
    return airbyte_get_connection_response_json


@pytest.fixture
def airbyte_get_connection_not_found():
    return {
        "id": "string",
        "message": "string",
        "exceptionClassName": "string",
        "exceptionStack": ["string"],
        "rootCauseExceptionClassName": "string",
        "rootCauseExceptionStack": ["string"],
    }


@pytest.fixture
def airbyte_base_job_status_response(connection_id) -> dict:
    return {
        "job": {
            "id": 45,
            "configType": "sync",
            "configId": connection_id,
            "createdAt": 1650644844,
            "updatedAt": 1650644844,
            "status": None,
        },
        "attempts": [],
    }


@pytest.fixture
def airbyte_get_good_job_status_response(airbyte_base_job_status_response) -> dict:
    airbyte_base_job_status_response["job"]["status"] = "succeeded"
    airbyte_base_job_status_response["attempts"].append(
        {
            "attempt": {
                "id": 0,
                "status": "succeeded",
                "createdAt": 0,
                "updatedAt": 0,
                "endedAt": 0,
                "bytesSynced": 0,
                "recordsSynced": 0,
            }
        }
    )
    return airbyte_base_job_status_response


@pytest.fixture
def airbyte_get_pending_job_status_response(airbyte_base_job_status_response) -> dict:
    airbyte_base_job_status_response["job"]["status"] = "pending"
    airbyte_base_job_status_response["attempts"].append(
        {
            "attempt": {
                "id": 0,
                "status": "pending",
                "createdAt": 0,
                "updatedAt": 0,
                "endedAt": 0,
                "bytesSynced": 0,
                "recordsSynced": 0,
            }
        }
    )
    return airbyte_base_job_status_response


@pytest.fixture
def airbyte_get_failed_job_status_response(airbyte_base_job_status_response) -> dict:
    airbyte_base_job_status_response["job"]["status"] = "failed"
    airbyte_base_job_status_response["attempts"].append(
        {
            "attempt": {
                "id": 0,
                "status": "failed",
                "createdAt": 0,
                "updatedAt": 0,
                "endedAt": 0,
                "bytesSynced": 0,
                "recordsSynced": 0,
            }
        }
    )
    return airbyte_base_job_status_response


@pytest.fixture
def airbyte_get_incomplete_job_status_response(
    airbyte_base_job_status_response,
) -> dict:
    airbyte_base_job_status_response["job"]["status"] = "incomplete"
    airbyte_base_job_status_response["attempts"].append(
        {
            "attempt": {
                "id": 0,
                "status": "failed",
                "createdAt": 0,
                "updatedAt": 0,
                "endedAt": 0,
                "bytesSynced": 0,
                "recordsSynced": 0,
            }
        }
    )
    return airbyte_base_job_status_response


@pytest.fixture
def airbyte_get_running_job_status_response(airbyte_base_job_status_response) -> dict:
    airbyte_base_job_status_response["job"]["status"] = "running"
    airbyte_base_job_status_response["attempts"].append(
        {
            "attempt": {
                "id": 0,
                "status": "running",
                "createdAt": 0,
                "updatedAt": 0,
                "endedAt": 0,
                "bytesSynced": 0,
                "recordsSynced": 17,
            }
        }
    )
    return airbyte_base_job_status_response


@pytest.fixture
def airbyte_get_job_status_response_without_attempts(
    airbyte_base_job_status_response,
) -> dict:
    """A job Airbyte has accepted but not yet recorded an attempt for."""
    airbyte_base_job_status_response["job"]["status"] = "running"
    return airbyte_base_job_status_response


@pytest.fixture
def airbyte_job_status_not_found_response():
    return {
        "id": "string",
        "message": "string",
        "exceptionClassName": "string",
        "exceptionStack": ["string"],
        "rootCauseExceptionClassName": "string",
        "rootCauseExceptionStack": ["string"],
    }


@pytest.fixture
def base_airbyte_url():
    return "http://localhost:8000/api/v1"


@pytest.fixture
def mock_successful_connection_sync_calls(
    respx_mock,
    base_airbyte_url,
    airbyte_good_health_check_response,
    airbyte_get_connection_response_json,
    airbyte_trigger_sync_response,
    airbyte_get_good_job_status_response,
):
    # health check: successful case
    respx_mock.get(url=f"{base_airbyte_url}/health/").mock(
        return_value=Response(200, json=airbyte_good_health_check_response)
    )

    # get existing connection by ID: successful case
    respx_mock.post(
        url=f"{base_airbyte_url}/connections/get/",
        json={"connectionId": airbyte_get_connection_response_json["connectionId"]},
    ).mock(return_value=Response(200, json=airbyte_get_connection_response_json))

    # trigger sync of existing connection: successful case
    respx_mock.post(
        url=f"{base_airbyte_url}/connections/sync/",
        json={"connectionId": airbyte_trigger_sync_response["connectionId"]},
    ).mock(return_value=Response(200, json=airbyte_trigger_sync_response))

    # get job status: successful case
    respx_mock.post(
        url=f"{base_airbyte_url}/jobs/get/",
        json={"id": airbyte_get_good_job_status_response["job"]["id"]},
    ).mock(return_value=Response(200, json=airbyte_get_good_job_status_response))


@pytest.fixture
def mock_failed_connection_sync_calls(
    respx_mock,
    base_airbyte_url,
    airbyte_good_health_check_response,
    airbyte_get_connection_response_json,
    airbyte_trigger_sync_response,
    airbyte_get_failed_job_status_response,
):
    respx_mock.get(url=f"{base_airbyte_url}/health/").mock(
        return_value=Response(200, json=airbyte_good_health_check_response)
    )

    respx_mock.post(
        url=f"{base_airbyte_url}/connections/get/",
        json={"connectionId": airbyte_get_connection_response_json["connectionId"]},
    ).mock(return_value=Response(200, json=airbyte_get_connection_response_json))

    respx_mock.post(
        url=f"{base_airbyte_url}/connections/sync/",
        json={"connectionId": airbyte_trigger_sync_response["connectionId"]},
    ).mock(return_value=Response(200, json=airbyte_trigger_sync_response))

    respx_mock.post(
        url=f"{base_airbyte_url}/jobs/get/",
        json={"id": airbyte_get_failed_job_status_response["job"]["id"]},
    ).mock(return_value=Response(200, json=airbyte_get_failed_job_status_response))


@pytest.fixture
def mock_failed_health_check_calls(
    respx_mock, base_airbyte_url, airbyte_bad_health_check_response
):
    respx_mock.get(url=f"{base_airbyte_url}/health/").mock(
        return_value=Response(200, json=airbyte_bad_health_check_response)
    )


@pytest.fixture
def mock_bad_connection_id_calls(
    respx_mock,
    base_airbyte_url,
    airbyte_get_connection_response_json,
    airbyte_get_connection_not_found,
    airbyte_good_health_check_response,
):
    respx_mock.get(url=f"{base_airbyte_url}/health/").mock(
        return_value=Response(200, json=airbyte_good_health_check_response)
    )

    respx_mock.post(
        url=f"{base_airbyte_url}/connections/get/",
        json={"connectionId": airbyte_get_connection_response_json["connectionId"]},
    ).mock(return_value=Response(404, json=airbyte_get_connection_not_found))


@pytest.fixture
def mock_invalid_job_status_calls(
    respx_mock,
    base_airbyte_url,
    airbyte_good_health_check_response,
    airbyte_get_good_job_status_response,
    airbyte_trigger_sync_response,
    airbyte_get_connection_response_json,
    airbyte_job_status_not_found_response,
):
    respx_mock.get(url=f"{base_airbyte_url}/health/").mock(
        return_value=Response(200, json=airbyte_good_health_check_response)
    )

    respx_mock.post(
        url=f"{base_airbyte_url}/connections/get/",
        json={"connectionId": airbyte_get_connection_response_json["connectionId"]},
    ).mock(return_value=Response(200, json=airbyte_get_connection_response_json))

    respx_mock.post(
        url=f"{base_airbyte_url}/connections/sync/",
        json={"connectionId": airbyte_trigger_sync_response["connectionId"]},
    ).mock(return_value=Response(200, json=airbyte_trigger_sync_response))

    respx_mock.post(
        url=f"{base_airbyte_url}/jobs/get/",
        json={"id": airbyte_get_good_job_status_response["job"]["id"]},
    ).mock(return_value=Response(404, json=airbyte_job_status_not_found_response))


@pytest.fixture
def mock_cancelled_connection_sync_calls(
    respx_mock,
    base_airbyte_url,
    airbyte_good_health_check_response,
    airbyte_trigger_sync_response,
    airbyte_get_connection_response_json,
    airbyte_get_pending_job_status_response,
    airbyte_get_failed_job_status_response,
):
    respx_mock.get(url=f"{base_airbyte_url}/health/").mock(
        return_value=Response(200, json=airbyte_good_health_check_response)
    )

    respx_mock.post(
        url=f"{base_airbyte_url}/connections/get/",
        json={"connectionId": airbyte_get_connection_response_json["connectionId"]},
    ).mock(return_value=Response(200, json=airbyte_get_connection_response_json))

    respx_mock.post(
        url=f"{base_airbyte_url}/connections/sync/",
        json={"connectionId": airbyte_trigger_sync_response["connectionId"]},
    ).mock(return_value=Response(200, json=airbyte_trigger_sync_response))

    respx_mock.post(
        url=f"{base_airbyte_url}/jobs/get/",
        json={"id": airbyte_get_pending_job_status_response["job"]["id"]},
    ).mock(return_value=Response(200, json=airbyte_get_pending_job_status_response))

    respx_mock.post(
        url=f"{base_airbyte_url}/jobs/get/",
        json={"id": airbyte_get_failed_job_status_response["job"]["id"]},
    ).mock(return_value=Response(200, json=airbyte_get_failed_job_status_response))


@pytest.fixture
def mock_incomplete_connection_sync_calls(
    respx_mock,
    base_airbyte_url,
    airbyte_good_health_check_response,
    airbyte_get_connection_response_json,
    airbyte_trigger_sync_response,
    airbyte_get_incomplete_job_status_response,
):
    respx_mock.get(url=f"{base_airbyte_url}/health/").mock(
        return_value=Response(200, json=airbyte_good_health_check_response)
    )

    respx_mock.post(
        url=f"{base_airbyte_url}/connections/get/",
        json={"connectionId": airbyte_get_connection_response_json["connectionId"]},
    ).mock(return_value=Response(200, json=airbyte_get_connection_response_json))

    respx_mock.post(
        url=f"{base_airbyte_url}/connections/sync/",
        json={"connectionId": airbyte_trigger_sync_response["connectionId"]},
    ).mock(return_value=Response(200, json=airbyte_trigger_sync_response))

    respx_mock.post(
        url=f"{base_airbyte_url}/jobs/get/",
        json={"id": airbyte_get_incomplete_job_status_response["job"]["id"]},
    ).mock(return_value=Response(200, json=airbyte_get_incomplete_job_status_response))


@pytest.fixture
def mock_never_finishing_connection_sync_calls(
    respx_mock,
    base_airbyte_url,
    airbyte_good_health_check_response,
    airbyte_get_connection_response_json,
    airbyte_trigger_sync_response,
    airbyte_get_pending_job_status_response,
):
    """Mocks a sync whose job never leaves a non-terminal status."""
    respx_mock.get(url=f"{base_airbyte_url}/health/").mock(
        return_value=Response(200, json=airbyte_good_health_check_response)
    )

    respx_mock.post(
        url=f"{base_airbyte_url}/connections/get/",
        json={"connectionId": airbyte_get_connection_response_json["connectionId"]},
    ).mock(return_value=Response(200, json=airbyte_get_connection_response_json))

    respx_mock.post(
        url=f"{base_airbyte_url}/connections/sync/",
        json={"connectionId": airbyte_trigger_sync_response["connectionId"]},
    ).mock(return_value=Response(200, json=airbyte_trigger_sync_response))

    respx_mock.post(
        url=f"{base_airbyte_url}/jobs/get/",
        json={"id": airbyte_get_pending_job_status_response["job"]["id"]},
    ).mock(return_value=Response(200, json=airbyte_get_pending_job_status_response))


def _mock_trigger_calls(
    respx_mock,
    base_airbyte_url,
    health_response,
    connection_response,
    trigger_response,
):
    """Mocks everything a sync needs up to and including `connections/sync`."""
    respx_mock.get(url=f"{base_airbyte_url}/health/").mock(
        return_value=Response(200, json=health_response)
    )

    respx_mock.post(
        url=f"{base_airbyte_url}/connections/get/",
        json={"connectionId": connection_response["connectionId"]},
    ).mock(return_value=Response(200, json=connection_response))

    respx_mock.post(
        url=f"{base_airbyte_url}/connections/sync/",
        json={"connectionId": trigger_response["connectionId"]},
    ).mock(return_value=Response(200, json=trigger_response))


def _mock_sync_calls_returning(
    respx_mock,
    base_airbyte_url,
    health_response,
    connection_response,
    trigger_response,
    job_status_response,
):
    """Mocks a whole sync, with `jobs/get` answering with `job_status_response`."""
    _mock_trigger_calls(
        respx_mock,
        base_airbyte_url,
        health_response,
        connection_response,
        trigger_response,
    )

    respx_mock.post(
        url=f"{base_airbyte_url}/jobs/get/",
        json={"id": job_status_response["job"]["id"]},
    ).mock(return_value=Response(200, json=job_status_response))


@pytest.fixture
def mock_running_connection_sync_calls(
    respx_mock,
    base_airbyte_url,
    airbyte_good_health_check_response,
    airbyte_get_connection_response_json,
    airbyte_trigger_sync_response,
    airbyte_get_running_job_status_response,
):
    _mock_sync_calls_returning(
        respx_mock,
        base_airbyte_url,
        airbyte_good_health_check_response,
        airbyte_get_connection_response_json,
        airbyte_trigger_sync_response,
        airbyte_get_running_job_status_response,
    )


@pytest.fixture
def mock_sync_calls_without_attempts(
    respx_mock,
    base_airbyte_url,
    airbyte_good_health_check_response,
    airbyte_get_connection_response_json,
    airbyte_trigger_sync_response,
    airbyte_get_job_status_response_without_attempts,
):
    _mock_sync_calls_returning(
        respx_mock,
        base_airbyte_url,
        airbyte_good_health_check_response,
        airbyte_get_connection_response_json,
        airbyte_trigger_sync_response,
        airbyte_get_job_status_response_without_attempts,
    )


@pytest.fixture
def mock_sync_calls_with_attempts_appearing_late(
    respx_mock,
    base_airbyte_url,
    airbyte_good_health_check_response,
    airbyte_get_connection_response_json,
    airbyte_trigger_sync_response,
    airbyte_base_job_status_response,
):
    """Airbyte answers the first poll before recording an attempt, then completes.

    `airbyte_base_job_status_response` is function scoped, so both payloads are
    deep copied rather than derived from the shared dict.
    """
    no_attempt_yet = deepcopy(airbyte_base_job_status_response)
    no_attempt_yet["job"]["status"] = "running"

    finished = deepcopy(airbyte_base_job_status_response)
    finished["job"]["status"] = "succeeded"
    finished["attempts"] = [
        {
            "attempt": {
                "id": 0,
                "status": "succeeded",
                "createdAt": 0,
                "updatedAt": 0,
                "endedAt": 0,
                "bytesSynced": 0,
                "recordsSynced": 17,
            }
        }
    ]

    _mock_trigger_calls(
        respx_mock,
        base_airbyte_url,
        airbyte_good_health_check_response,
        airbyte_get_connection_response_json,
        airbyte_trigger_sync_response,
    )

    respx_mock.post(
        url=f"{base_airbyte_url}/jobs/get/",
        json={"id": airbyte_base_job_status_response["job"]["id"]},
    ).mock(
        side_effect=[
            Response(200, json=no_attempt_yet),
            Response(200, json=finished),
        ]
    )


@pytest.fixture
def mock_inactive_sync_calls(
    respx_mock,
    base_airbyte_url,
    airbyte_good_health_check_response,
    airbyte_get_connection_response_json,
):
    respx_mock.get(url=f"{base_airbyte_url}/health/").mock(
        return_value=Response(200, json=airbyte_good_health_check_response)
    )

    airbyte_get_connection_response_json["status"] = "inactive"

    respx_mock.post(
        url=f"{base_airbyte_url}/connections/get/",
        json={"connectionId": airbyte_get_connection_response_json["connectionId"]},
    ).mock(return_value=Response(200, json=airbyte_get_connection_response_json))


def _mock_connection_status_calls(
    respx_mock, base_airbyte_url, health_response, connection_response, status
):
    """Mocks health plus `connections/get` answering with `status`."""
    respx_mock.get(url=f"{base_airbyte_url}/health/").mock(
        return_value=Response(200, json=health_response)
    )

    connection_response["status"] = status

    respx_mock.post(
        url=f"{base_airbyte_url}/connections/get/",
        json={"connectionId": connection_response["connectionId"]},
    ).mock(return_value=Response(200, json=connection_response))


@pytest.fixture
def mock_deprecated_sync_calls(
    respx_mock,
    base_airbyte_url,
    airbyte_good_health_check_response,
    airbyte_get_connection_response_json,
):
    _mock_connection_status_calls(
        respx_mock,
        base_airbyte_url,
        airbyte_good_health_check_response,
        airbyte_get_connection_response_json,
        "deprecated",
    )


@pytest.fixture
def unknown_connection_status() -> str:
    """A status Airbyte does not report today, standing in for one it adds later."""
    return "archived"


@pytest.fixture
def mock_unknown_status_sync_calls(
    respx_mock,
    base_airbyte_url,
    airbyte_good_health_check_response,
    airbyte_get_connection_response_json,
    unknown_connection_status,
):
    _mock_connection_status_calls(
        respx_mock,
        base_airbyte_url,
        airbyte_good_health_check_response,
        airbyte_get_connection_response_json,
        unknown_connection_status,
    )


@pytest.fixture
def airbyte_good_export_configuration_response() -> bytes:
    return b""


@pytest.fixture
def mock_successful_config_export_calls(
    respx_mock,
    base_airbyte_url,
    airbyte_good_health_check_response,
    airbyte_good_export_configuration_response,
):
    respx_mock.get(url=f"{base_airbyte_url}/health/").mock(
        return_value=Response(200, json=airbyte_good_health_check_response)
    )

    respx_mock.post(url=f"{base_airbyte_url}/deployment/export/").mock(
        return_value=Response(200, content=airbyte_good_export_configuration_response)
    )


@pytest.fixture
def mock_config_endpoint_not_found(
    respx_mock,
    base_airbyte_url,
    airbyte_good_health_check_response,
    airbyte_good_export_configuration_response,
):
    respx_mock.get(url=f"{base_airbyte_url}/health/").mock(
        return_value=Response(200, json=airbyte_good_health_check_response)
    )

    respx_mock.post(url=f"{base_airbyte_url}/deployment/export/").mock(
        return_value=Response(404)
    )
