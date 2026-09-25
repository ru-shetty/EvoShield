from typing import Dict, Optional


class ModelRegistry:

    def __init__(self):
        self.models: Dict[str, Dict] = {}

    def register(
        self,
        version: str,
        metadata: Optional[Dict] = None,
    ) -> None:

        self.models[version] = metadata or {}

    def get(self, version: str) -> Optional[Dict]:

        return self.models.get(version)

    def exists(self, version: str) -> bool:

        return version in self.models