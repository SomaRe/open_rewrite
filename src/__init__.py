import re
from pathlib import Path

def get_version():
    # Find the pyproject.toml file by walking up from the current file
    current_file = Path(__file__).resolve()
    package_root = current_file.parent
    
    # Keep going up directories until we find pyproject.toml or hit the filesystem root
    while package_root != package_root.parent:
        pyproject_path = package_root / "pyproject.toml"
        if pyproject_path.exists():
            break
        package_root = package_root.parent
    else:
        raise FileNotFoundError("Could not find pyproject.toml")
    
    # Read and parse the version
    with open(pyproject_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # This regex handles both poetry and standard project formats
    version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Version not found in pyproject.toml")

__version__ = get_version()