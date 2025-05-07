import os
import setuptools
from typing import List
import io

def _read_reqs(rel_path: str) -> List[str]:
    full_path = os.path.join(os.path.dirname(__file__), rel_path)
    with io.open(full_path) as f:
        return [s.strip() for s in f.readlines() if (s.strip() and not s.startswith("#"))]



_REQUIRE = _read_reqs("requirements.txt")

_SETUP_COMMON_ARGS = {
    "data_files": [(".", ["requirements.txt"])],
    "packages": setuptools.find_packages(),
    "include_package_data": True,
}

setuptools.setup(
    name="sku_unification",
    version="0.0.2",
    install_requires=_REQUIRE,
    dependency_links=[],
    **_SETUP_COMMON_ARGS
)
