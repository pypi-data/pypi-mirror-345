from pathlib import Path
from types import ModuleType


def import_module_from(path: Path) -> ModuleType:
    """
    Import a Python module into runtime.

    :param path: a path or string that represents a Python module.

    >>> import_module_from(Path(""))
    Traceback (most recent call last):
    ...
    ModuleNotFoundError: Module 'None' not found.
    """
    import importlib.util

    if not path or not path.exists():
        raise ModuleNotFoundError(f"There is no module at '{path.resolve()}'.")

    name = path.name.replace(".py", "")  # get the module name (filename without extension)
    module_spec = importlib.util.spec_from_file_location(name, path)  # get the module specification

    if module_spec:
        module_instance = importlib.util.module_from_spec(module_spec)

        if module_instance:
            module_spec.loader.exec_module(module_instance)
        else:
            raise ModuleNotFoundError(f"Module spec '{module_spec}' not found.")
    else:
        raise ModuleNotFoundError(f"Module '{module_spec}' not found.")

    return module_instance


def import_package_from(path: Path) -> list[ModuleType]:
    """
    Manually load all Python modules inside a package.
    """
    return [import_module_from(Path(module_path)) for module_path in path.glob("*.py")]


def import_module(name: str) -> ModuleType:
    """
    Import/Load a python module.

    :param name: module name, e.g. `"package.module"`
    """
    import importlib
    return importlib.import_module(name)


def import_modules(modules: list[str]) -> list[ModuleType]:
    """
    Import/Load a list of python modules.

    :param modules: a list of module names, e.g. `["package.module"]`
    """
    return [import_module(module_name) for module_name in modules]
