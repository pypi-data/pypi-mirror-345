# src/agent_tooling/tool_discovery.py

import importlib
import pkgutil
import sys
from typing import Optional, List
import os

def import_submodules(package_name: str) -> None:
    """Import all submodules of a package recursively."""
    package = importlib.import_module(package_name)
    for _, full_name, is_pkg in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
        if is_pkg:
            import_submodules(full_name)
        else:
            importlib.import_module(full_name)

def discover_tools(folders: Optional[List[str]] = None) -> None:
    if not folders:
        return

    for pkg_name in folders:
        # 🛠 Always ensure package is imported
        if pkg_name not in sys.modules:
            try:
                importlib.import_module(pkg_name)
            except ModuleNotFoundError:
                print(f"Warning: package '{pkg_name}' not found on sys.path")
                continue
            except Exception as e:
                print(f"Warning: could not import '{pkg_name}': {e}")
                continue

        pkg = sys.modules.get(pkg_name)
        if not pkg:
            continue

        pkg_paths = getattr(pkg, '__path__', None)
        if not pkg_paths:
            continue

        for pkg_path in pkg_paths:
            if not os.path.isdir(pkg_path):
                continue
            for root, dirs, files in os.walk(pkg_path):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for file in files:
                    if not file.endswith('.py') or file == '__init__.py':
                        continue
                    rel_path = os.path.relpath(root, pkg_path)
                    mod_name = file[:-3] if rel_path == '.' else f"{rel_path.replace(os.sep, '.')}.{file[:-3]}"
                    full_mod = f"{pkg_name}.{mod_name}"
                    try:
                        importlib.import_module(full_mod)
                    except Exception as e:
                        print(f"Warning: failed to import '{full_mod}': {e}")
