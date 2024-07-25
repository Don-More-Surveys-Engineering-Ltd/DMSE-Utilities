from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


XYZ_LINE_COMPONENTS = "X", "Y", "Z"


def _crop_lidar_file(
    input_file: Path,
    east_min: float,
    east_max: float,
    north_min: float,
    north_max: float,
) -> list[str]:
    output: list[str] = []
    with input_file.open("r") as fp:
        for line in fp:
            instr = line.split(" ")
            if len(instr) < len(XYZ_LINE_COMPONENTS):
                instr = line.split(",")
            east_in = float(instr[0])
            if east_in > east_min and east_in < east_max:
                north_in = float(instr[1])
                if north_in > north_min and north_in < north_max:
                    output.append(line)
    return output


def crop_lidar_files(  # noqa: PLR0913
    input_files: list[Path],
    east_min: float,
    east_max: float,
    north_min: float,
    north_max: float,
    output_file: Path,
):
    """Crop files down to extents, include all coords in single output file."""
    output: list[str] = []
    for i_file in input_files:
        output.extend(
            _crop_lidar_file(i_file, east_min, east_max, north_min, north_max),
        )

    with output_file.open("w") as fp:
        fp.write("\n".join(output))
