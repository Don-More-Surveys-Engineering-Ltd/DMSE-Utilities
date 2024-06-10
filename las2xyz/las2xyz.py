from __future__ import annotations

import logging
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, cast

import laspy

logger = logging.getLogger(__name__)


class Las2XYZOperation:
    """LAS2XYZ converts las data to XYZ data."""

    tile_list: list[tuple[float, float]]
    output_tile_filenames: list[str]

    min_x: float | None
    min_y: float | None
    max_x: float | None
    max_y: float | None

    tile_size: int | None

    input_path: Path | None
    output_dir_path: Path | None

    parallel_count: int

    def __init__(self) -> None:  # noqa: D107
        self.working_path = Path.cwd()
        self.output_tile_filenames = []
        self.parallel_count = 15
        self.min_x, self.min_y, self.max_x, self.max_y = None, None, None, None
        self.input_path = None
        self.output_dir_path = None
        self.tile_size = None

    def init_data(self) -> None:
        """Initialize data from las files."""
        if self.input_path:
            self.min_x, self.min_y, _, self.max_x, self.max_y, _ = self.get_extent()

            if self.tile_size:
                self.tile_list = self.build_tile_list()

    def set_tile_size(self, tile_size: int):
        self.tile_size = tile_size

        self.init_data()

    def set_input(self, path: Path):
        self.input_path = path

        self.init_data()

    def set_output_dir(self, path: Path):
        assert path.is_dir

        self.output_dir_path = path

    def start(
        self,
        progress_callback: Callable[[str], Any],
        complete_callback: Callable[[Path], Any],
    ):
        """Begin operation."""
        if not self.input_path or not self.output_dir_path or not self.tile_size:
            return False

        with tempfile.TemporaryDirectory() as temp_dir:
            num_tiles = len(self.tile_list)
            n = self.parallel_count
            for index in range(0, num_tiles, n):

                def create_process(tile, temp_dir) -> list[str]:
                    """Spawn las2txt process.

                    Return command used.
                    """
                    cmd, tile_file_name = self.build_las2txt_cmd_for_tile(
                        tile,
                        Path(temp_dir),
                    )
                    logger.info(f"Spawning process from {cmd=}.")
                    progress_callback(str(tile_file_name))
                    return cmd

                processes = [
                    subprocess.Popen(create_process(tile, temp_dir))
                    for tile in self.tile_list[index : min(index + n, num_tiles)]
                ]

                for p in processes:
                    logger.info(f"Waiting for process {p}")
                    p.wait()

            logger.info("Creating archive of output files.")
            out = shutil.make_archive(
                str(self.output_dir_path / f"{self.input_path.stem}_tiles"),
                "zip",
                Path(temp_dir).parent,
                Path(temp_dir).name,
            )
            logger.info(f"Archive created at {out}")

            complete_callback(Path(out))

        return True

    def get_extent(self):
        """Get extents from las file header."""
        las_file_reader = laspy.open(self.input_path)
        file_header = las_file_reader.header

        # h.min: [min_x, min_y, min_z] - h.max: [max_x, max_y, max_z]
        extent = (
            *file_header.min,
            *file_header.max,
        )  # extent: [min_x, min_y, min_z, max_x, max_y, max_z]
        logger.info(f"Got extent {extent=}")
        return cast(tuple[float, float, float, float, float, float], extent)

    def build_tile_list(self):
        """Build a list of tiles with size "tile_size" from within the file extent."""
        assert self.min_x  # noqa: S101
        assert self.min_y  # noqa: S101
        assert self.max_x  # noqa: S101
        assert self.max_y  # noqa: S101
        assert self.tile_size  # noqa: S101
        tile_list: list[tuple[float, float]] = []

        # round down to nearest increment of tile size
        # e.g. 2568759 -> 2568700 (tile_size=100m)
        start_x = self.min_x - (self.min_x % self.tile_size)
        start_y = self.min_y - (self.min_y % self.tile_size)

        curr_y = start_y

        while curr_y <= self.max_y:
            curr_x = start_x
            while curr_x <= self.max_x:
                tile_list.append((curr_x, curr_y))
                curr_x += self.tile_size
            curr_y += self.tile_size

        return tile_list

    def build_las2txt_cmd_for_tile(
        self,
        tile: tuple[float, float],
        destination_folder: Path,
    ):
        """Create command for las2txt.exe."""
        assert self.input_path  # noqa: S101
        assert self.tile_size  # noqa: S101
        tile_file_name = Path(
            f"{self.input_path.stem}-{int(tile[0])}_{int(tile[1])}.XYZ",
        )

        self.output_tile_filenames.append(tile_file_name.name)

        cmd = [
            "helpers/las2txt.exe",
            *("-i", str(self.input_path)),
            *("keep_class", "2", "8"),
            *("-o", str(destination_folder / tile_file_name)),
            *("-oparse", "xyz"),
            *("-osep", "comma"),
            *("-keep_xy",),
            # min_x, min_y, max_x, max_y for tile
            *(
                str(tile[0]),
                str(tile[1]),
                str(tile[0] + self.tile_size),
                str(tile[1] + self.tile_size),
            ),
        ]

        return (cmd, tile_file_name)


if __name__ == "__main__":
    cmd_input_path = Path(sys.argv[1])
    op = Las2XYZOperation()
    op.set_input(cmd_input_path)
    op.set_output_dir(cmd_input_path.parent)
    op.set_tile_size(100)

    op.start(lambda _: None, lambda _: None)
