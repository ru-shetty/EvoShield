from typing import Dict, Optional


class PreprocessingRegistry:

    def __init__(self):
        self.preprocessing: Dict[str, Dict] = {}

    def register(
        self,
        version: str,
        metadata: Optional[Dict] = None,
    ) -> None:

        self.preprocessing[version] = metadata or {}

    def get(self, version: str) -> Optional[Dict]:

        return self.preprocessing.get(version)

    def exists(self, version: str) -> bool:

        return version in self.preprocessing