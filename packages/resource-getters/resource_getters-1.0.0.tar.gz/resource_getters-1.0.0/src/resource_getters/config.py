from types import ModuleType

_resource_package: ModuleType | None = None


def configure(resource_package: ModuleType) -> None:
    global _resource_package

    _resource_package = resource_package
