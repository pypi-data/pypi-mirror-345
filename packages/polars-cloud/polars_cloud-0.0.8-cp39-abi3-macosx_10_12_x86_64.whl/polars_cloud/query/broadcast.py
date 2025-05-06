from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path


class Broadcast:
    # over
    #     Run this queries in parallel over the given source paths.
    #
    #     Levels from outer to inner:
    #     1 -> partition paths
    #     2 -> src in DSL
    #     3 -> paths (plural) in a single DSL source.
    over: list[list[list[str]]]

    def __init__(self) -> None:
        self.over = [[[]]]

    def _get_current_partition(self) -> list[list[str]]:
        return self.over[len(self.over) - 1]

    def _get_current_sources(self) -> list[str]:
        part = self._get_current_partition()
        return part[len(part) - 1]

    def new_scan(self) -> Broadcast:
        """Go a new scan in the same query."""
        part = self._get_current_partition()
        part.append([])
        return self

    def new_partition(self) -> Broadcast:
        self.over.append([[]])
        return self

    def add_file(self, src: Path | str) -> Broadcast:
        self._get_current_sources().append(str(src))
        return self

    def add_files(self, src: Iterable[str | Path]) -> Broadcast:
        self._get_current_sources().extend([str(x) for x in src])
        return self

    def finish(self) -> list[list[list[str]]]:
        return self.over


PLACEHOLDER: str = "_POLARS_<>"
