"""A JSON file store with atomic writes."""

from __future__ import annotations

import json
import os
import tempfile
from typing import Any, Dict


class StoreError(Exception):
    pass


class JsonStore:
    def __init__(self, path: str):
        self.path = path

    def exists(self) -> bool:
        return os.path.isfile(self.path)

    def load(self) -> Dict[str, Any]:
        if not self.exists():
            return {}
        try:
            with open(self.path, encoding="utf-8") as handle:
                data = json.load(handle)
        except ValueError:
            return {}
        except OSError as error:
            raise StoreError(f"cannot read {self.path}: {error}") from error
        return data if isinstance(data, dict) else {}

    def save(self, data: Dict[str, Any]) -> None:
        directory = os.path.dirname(os.path.abspath(self.path))
        os.makedirs(directory, exist_ok=True)
        fd, temp_path = tempfile.mkstemp(prefix=".linkcrawl-", suffix=".json", dir=directory)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(data, handle, indent=2, sort_keys=True)
                handle.write("\n")
            os.replace(temp_path, self.path)
        except BaseException:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise

    def delete(self) -> bool:
        if not self.exists():
            return False
        os.unlink(self.path)
        return True


class MemoryStore(JsonStore):
    def __init__(self):
        super().__init__(path=":memory:")
        self.data: Dict[str, Any] = {}

    def exists(self) -> bool:
        return bool(self.data)

    def load(self) -> Dict[str, Any]:
        return json.loads(json.dumps(self.data))

    def save(self, data: Dict[str, Any]) -> None:
        self.data = json.loads(json.dumps(data))

    def delete(self) -> bool:
        had = bool(self.data)
        self.data = {}
        return had
