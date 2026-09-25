from typing import Dict, Optional

from ..models.version import AlgorithmVersion


class AlgorithmRegistry:

    def __init__(self):
        self._versions: Dict[str, AlgorithmVersion] = {}
        self._active_version: Optional[str] = None

    def register(self, version: AlgorithmVersion) -> str:

        version_id = version.version_id()
        self._versions[version_id] = version

        return version_id

    def get(self, version_id: str) -> Optional[AlgorithmVersion]:
        return self._versions.get(version_id)

    def approve(self, version_id: str) -> bool:

        version = self.get(version_id)

        if version is None:
            return False

        version.approve()
        self._active_version = version_id

        return True

    def reject(self, version_id: str) -> bool:

        version = self.get(version_id)

        if version is None:
            return False

        version.reject()

        return True

    def active(self) -> Optional[AlgorithmVersion]:

        if self._active_version is None:
            return None

        return self._versions.get(self._active_version)

    def all_versions(self):
        return list(self._versions.values())