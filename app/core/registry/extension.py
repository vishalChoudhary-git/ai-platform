from app.core.extensions.base import BaseExtension
from app.core.registry.base import Registry

extension_registry = Registry[BaseExtension]("Extension Registry")
