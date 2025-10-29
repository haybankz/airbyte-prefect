from . import _version

from airbyte_prefect.connections import AirbyteConnection  # noqa F401
from airbyte_prefect.server import AirbyteServer  # noqa F401

__version__ = _version.get_versions()["version"]
