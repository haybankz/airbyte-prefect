"""Exceptions to raise indicating issues throughout airbyte_prefect"""


class ConnectionNotFoundException(Exception):
    """
    Raises when a requested Airbyte connection cannot be found.
    """


class AirbyteServerNotHealthyException(Exception):
    """
    Raises when a specified Airbyte instance returns an unhealthy response.
    """


class JobNotFoundException(Exception):
    """
    Raises when a requested Airbyte job cannot be found.
    """


class AirbyteSyncJobFailed(Exception):
    """
    Raises when a specified Airbyte Sync Job fails.
    """


class AirbyteSyncJobTimeout(Exception):
    """
    Raises when an Airbyte Sync Job does not reach a terminal status in time.
    """


class AirbyteExportConfigurationFailed(Exception):
    """
    Raises when an Airbyte configuration export fails.
    """


class AirbyteConnectionInactiveException(Exception):
    """
    Raises when a specified Airbyte connection is inactive.
    """


class AirbyteConnectionDeprecatedException(Exception):
    """
    Raises when a specified Airbyte connection is deprecated.
    """


# Retained so `except` clauses written against the misspelled name keep working.
AirbyeConnectionDeprecatedException = AirbyteConnectionDeprecatedException


class AirbyteConnectionUnknownStatusException(Exception):
    """
    Raises when Airbyte reports a connection status this version does not know.
    """
