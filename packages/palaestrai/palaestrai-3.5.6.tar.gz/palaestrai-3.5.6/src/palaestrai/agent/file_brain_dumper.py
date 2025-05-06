from __future__ import annotations

import io
from pathlib import Path
from typing import BinaryIO, Optional

from palaestrai.core import RuntimeConfig
from .brain_dumper import BrainDumper, BrainLocation


class FileBrainDumper(BrainDumper):
    """Dumps (and loads) a ::`~Brain` to/from the local file system."""

    @staticmethod
    def _make_path(locator: BrainLocation, tag: Optional[str] = None) -> Path:
        path = (
            Path(RuntimeConfig().data_path).resolve()
            / "brains"
            / locator.experiment_run_uid
            / str(locator.experiment_run_phase)
        )
        if tag:
            path /= f"{locator.agent_name}-{tag}.bin"
        else:
            path /= f"{locator.agent_name}.bin"
        return path

    def save(self, brain_state: BinaryIO, tag: Optional[str] = None):
        path = self._make_path(self._brain_destination, tag)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(str(path), "wb") as fp:
            fp.write(brain_state.read())

    def _load(
        self, source_locator: BrainLocation, tag: Optional[str] = None
    ) -> BinaryIO:
        path = self._make_path(source_locator, tag)
        with open(str(path), "rb") as fp:
            bio = io.BytesIO()
            bio.write(fp.read())
        return bio

    def __str__(self):
        return (
            f"<{self.__class__}(data_path={RuntimeConfig().data_path}, "
            f"dump_to={self._brain_destination}, load_from="
            f"{self._brain_source})>"
        )
