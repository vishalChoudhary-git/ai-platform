from app.core.connectors.base import BaseConnector
from app.core.registry.base import Registry

connector_registry = Registry[BaseConnector]("Connector Registry")
