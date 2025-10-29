"""Flows for interacting with Airbyte."""

from prefect import flow, task

from airbyte_prefect.connections import AirbyteConnection, AirbyteSyncResult


@flow
async def run_connection_sync(
    airbyte_connection: AirbyteConnection,
) -> AirbyteSyncResult:
    """A flow that triggers a sync of an Airbyte connection and waits for it to complete.

    Args:
        airbyte_connection: `AirbyteConnection` representing the Airbyte connection to
            trigger and wait for completion of.

    Returns:
        `AirbyteSyncResult`: Model containing metadata for the `AirbyteSync`.

    Example:
        Define a flow that runs an Airbyte connection sync:
        ```python
        from prefect import flow
        from airbyte_prefect.server import AirbyteServer
        from airbyte_prefect.connections import AirbyteConnection
        from airbyte_prefect.flows import run_connection_sync

        airbyte_server = AirbyteServer(
            server_host="localhost",
            server_port=8000
        )

        connection = AirbyteConnection(
            airbyte_server=airbyte_server,
            connection_id="<YOUR-AIRBYTE-CONNECTION-UUID>"
        )

        @flow
        def airbyte_sync_flow():
            # do some things

            airbyte_sync_result = run_connection_sync(
                airbyte_connection=connection
            )
            print(airbyte_sync_result.records_synced)

            # do some other things, like trigger DBT based on number of new raw records
        ```
    """

    # In Prefect 3, we can directly await sync_compatible methods in async contexts
    airbyte_sync = await airbyte_connection.trigger()

    await airbyte_sync.wait_for_completion()

    return await airbyte_sync.fetch_result()
