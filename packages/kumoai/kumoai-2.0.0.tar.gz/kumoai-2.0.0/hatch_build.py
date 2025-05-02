import sys
from distutils.core import run_setup
from pathlib import Path
from typing import Any, Dict

from hatchling.metadata.plugin.interface import MetadataHookInterface

sys.path.append(str(Path(__file__).parent))


class MetadataHook(MetadataHookInterface):
    def update(self, metadata: Dict[str, Any]) -> None:
        out = run_setup("./setup.py", stop_after="init")
        if "dependencies" not in metadata:
            metadata["dependencies"] = []

        # NOTE the wheels that are built with this process for internal
        # development currently include the Github token embedded in PKG-INFO.
        # As a result, the wheels should never be shared with any third-party
        # vendors. The token is limited to read-only SDK and API access.
        metadata["dependencies"].extend(out.install_requires)
