# for dev
from collections import defaultdict, namedtuple
from dataclasses import dataclass
from decimal import Decimal
from functools import cached_property, reduce
from pathlib import Path
from typing import Any, Optional

PATH = "C:/Users/jlong/Downloads/rw52dat/19194AT230830.rw5"


@dataclass
class GPSReading:
    northing: Decimal
    easting: Decimal
    elevation: Decimal


class Coord:
    readings: list[GPSReading]

    @property
    def avg(self):
        return GPSReading(
            northing=reduce(lambda a, b: a + b.northing, self.readings, Decimal(0))
            / len(self.readings),
            easting=reduce(lambda a, b: a + b.easting, self.readings, Decimal(0))
            / len(self.readings),
            elevation=reduce(lambda a, b: a + b.elevation, self.readings, Decimal(0))
            / len(self.readings),
        )

    def __init__(self, readings: list[GPSReading]) -> None:
        self.readings = readings


class Instruction:
    lines: list[str]

    @cached_property
    def op(self):
        return self.lines[0].split(",")[0]

    @cached_property
    def comment(self):
        if self.lines[0].find("--") != -1:
            return self.lines[0][self.lines[0].find("--") + 2 :]
        return ""

    @cached_property
    def args(self):
        return {
            line.removeprefix("--").split(",", maxsplit=1)[0]: line.split(
                ",", maxsplit=1
            )[1]
            for line in self.lines
            if line.find(",") != -1
        }

    def __init__(self) -> None:
        self.lines = []

    def add_line(self, line: str):
        self.lines.append(line)

    @staticmethod
    def get_param(line: str, prefix: str, default: Any = None):
        if line.find(prefix) == -1:
            return default

        return line[line.find(prefix) + len(prefix) : line.find(",", line.find(prefix))]


class ConvertOperation:
    @dataclass
    class State:
        instrument_height: Decimal | None = None
        rod_height: Decimal | None = None
        backsight_angle: tuple[int, int, int] | None = None
        backsight_coord: str | None = None

    coord_manifest: defaultdict[str, Coord]
    sideshot_manifest: defaultdict[str, int]
    instructions: list[Instruction]

    output: list[str]

    def __init__(self, path: Path, output_path: Path) -> None:
        self.path = path
        self.output_path = output_path

        self.coord_manifest = defaultdict(lambda: Coord([]))
        self.sideshot_manifest = defaultdict(lambda: 0)
        self.instructions = list()

        self.output = []
        self.state = self.State()

    @staticmethod
    def str_to_DMS_str(string: str):
        (part1, partRest) = string.split(".", maxsplit=1)
        part2 = partRest[:2]
        part3 = partRest[2:4]
        part4 = partRest[4:6].rjust(2, "0")
        print(string)
        return f"{int(part1)}-{str(int(part2)).zfill(2)}-{str(int(part3)).zfill(2)}.{part4}"

    @staticmethod
    def str_to_DMS_tuple(string: str):
        (part1, partRest) = string.split(".", maxsplit=1)
        part2 = partRest[:2]
        part3 = partRest[2:4]
        return (
            int(part1),
            int(part2),
            int(part3),
        )

    @staticmethod
    def subtract_DMS(a: tuple[int, int, int], b: tuple[int, int, int]):
        a_degrees = Decimal(a[0]) + Decimal(a[1]) / 60 + Decimal(a[2]) / 3600
        b_degrees = Decimal(b[0]) + Decimal(b[1]) / 60 + Decimal(b[2]) / 3600
        diff = a_degrees - b_degrees
        if diff < 0:
            diff += 360
        m, s = divmod(abs(diff) * 3600, 60)
        d, m = divmod(m, 60)
        d, m, s = int(str(d)), int(str(m)), round(s, 2)

        return (d, m, s)

    def to_instructions(self):
        curr_instruct: Optional[Instruction] = None
        with open(self.path) as f:
            for line in f:
                match (line, curr_instruct):
                    case (l, ci) if not l.startswith("--") and ci is None:
                        curr_instruct = Instruction()
                        curr_instruct.add_line(l.strip())
                    case (l, ci) if l.startswith("--") and ci is not None:
                        ci.add_line(l)
                    case (l, ci) if not l.startswith("--") and ci is not None:
                        # * Substitute point names
                        if ci.comment.startswith("CP/"):
                            PN_name: str | None = None
                            match ci.op:
                                case "GPS":
                                    PN_name = ci.get_param(ci.lines[0], "PN")
                                case "SS":
                                    PN_name = ci.get_param(ci.lines[0], "FP")
                            if PN_name:
                                ci.lines = [
                                    line.replace(
                                        PN_name,
                                        ci.comment.removeprefix("CP/").split(" ")[0],
                                    )
                                    for line in ci.lines
                                ]

                        self.instructions.append(ci)
                        curr_instruct = Instruction()
                        curr_instruct.add_line(l.strip())
                    case _:
                        raise Exception(f"Bad line:\n\t{line}")
            if curr_instruct is not None:
                self.instructions.append(curr_instruct)

    def first_pass(self):
        for instruct in self.instructions:
            match instruct.op:
                case "GPS":
                    self.coord_manifest[
                        instruct.get_param(instruct.lines[0], "PN")
                    ].readings.append(
                        GPSReading(
                            northing=Decimal(
                                instruct.get_param(instruct.lines[1], "N ")
                            ),
                            easting=Decimal(
                                instruct.get_param(instruct.lines[1], "E ")
                            ),
                            elevation=Decimal(
                                instruct.get_param(instruct.lines[1], "EL")
                            ),
                        )
                    )
                    self.sideshot_manifest[
                        instruct.get_param(instruct.lines[0], "PN")
                    ] += 1
                case "SS":
                    self.sideshot_manifest[
                        instruct.get_param(instruct.lines[0], "FP")
                    ] += 1

    def second_pass(self):
        self.prelude_c()

        for instruct in self.instructions:
            match instruct.op:
                case "JB":
                    self.jb(instruct)
                case "LS":
                    self.ls(instruct)
                case "SP":
                    self.sp(instruct)
                case "BK":
                    self.bk(instruct)
                case "SS":
                    self.ss(instruct)
                case _:
                    pass

    def jb(self, instruct: Instruction):
        name = instruct.get_param(instruct.lines[0], "NM")
        date = instruct.get_param(instruct.lines[0], "DT")
        time = instruct.get_param(instruct.lines[0], "TM")

        self.output.extend(
            [f"# Job : {name}", f"# Date : {date}", f"# Time : {time}", ""]
        )

    def ls(self, instruct: Instruction):
        instrument_height = instruct.get_param(instruct.lines[0], "HI")
        rod_height = instruct.get_param(instruct.lines[0], "HR")

        if instrument_height:
            self.state.instrument_height = Decimal(instrument_height)
        if rod_height:
            self.state.rod_height = Decimal(rod_height)

    def sp(self, instruct: Instruction):
        assert (
            self.state.instrument_height is not None
            and self.state.rod_height is not None
        ), "Invalid state"

        resection_name = instruct.get_param(instruct.lines[0], "PN")

        self.output.extend(
            [
                f"DB {resection_name}"
                + (f" '{instruct.comment}" if instruct.comment else ""),
            ]
        )
        for line in instruct.lines:
            if line.find("--Reading") != -1:
                point_name = instruct.get_param(line, "FP")
                ar = self.str_to_DMS_str(instruct.get_param(line, "AR"))
                ze = self.str_to_DMS_str(instruct.get_param(line, "ZE"))
                sd = instruct.get_param(line, "SD")
                sd = sd[: sd.find("--")]
                self.output.append(
                    f"DM "
                    + f"{point_name}".ljust(15)
                    + f"{ar}".rjust(15)
                    + f"{sd}".rjust(12)
                    + f"{ze}".rjust(15)
                    + f"{round(self.state.instrument_height, 3)}/{round(self.state.rod_height, 3)}".rjust(
                        15
                    )
                )
                self.sideshot_manifest[point_name] += 1
        self.output.extend(["DE", ""])

    def bk(self, instruct: Instruction):
        self.state.backsight_coord = instruct.get_param(instruct.lines[0], "BP")
        self.state.backsight_angle = self.str_to_DMS_tuple(
            instruct.get_param(instruct.lines[0], "BS")
        )

        self.output.extend(
            [
                "",
                f"DBG {self.state.backsight_coord=} {self.state.backsight_angle=}",
                f"    {instruct.lines[0]}",
            ]
        )

    def ss(self, instruct: Instruction):
        assert (
            self.state.backsight_coord is not None
            and self.state.backsight_angle is not None
            and self.state.instrument_height is not None
            and self.state.rod_height is not None
        ), "Invalid state."
        at = instruct.get_param(instruct.lines[0], "OP")
        from_point = self.state.backsight_coord
        to_point = instruct.get_param(instruct.lines[0], "FP")

        ar = instruct.get_param(instruct.lines[0], "AR")
        sd = instruct.get_param(instruct.lines[0], "SD")
        ze = instruct.get_param(instruct.lines[0], "ZE")

        op_code = "SS"
        if from_point == to_point:
            op_code = "DV"
        elif self.sideshot_manifest[to_point] > 1:
            op_code = "M "

        if op_code != "DV":
            dms = self.str_to_DMS_tuple(ar)
            diff = self.subtract_DMS(dms, self.state.backsight_angle)
            print(f"{ar=} {dms=} {diff=}")
            angle = self.str_to_DMS_str(
                f"{diff[0]}.{str(diff[1]).zfill(2)}{str(diff[2]).replace('.', '').zfill(2)}"
            )

            self.output.append(
                f"{op_code} {at}-{from_point}-{to_point}".ljust(18)
                + f"{angle}".rjust(15)
                + f"{round(Decimal(sd), 4)}".rjust(12)
                + f"{self.str_to_DMS_str(ze)}".rjust(15)
                + f"{round(self.state.instrument_height, 3)}/{round(self.state.rod_height, 3)}".rjust(
                    15
                )
                + f" '{instruct.comment}"
                if instruct.comment
                else ""
            )
        else:
            self.output.append(
                f"{op_code} {at}-{from_point}".ljust(18)
                + "".rjust(15)
                + f"{round(Decimal(sd), 4)}".rjust(12)
                + f"{self.str_to_DMS_str(ze)}".rjust(15)
                + f"{round(self.state.instrument_height, 3)}/{round(self.state.rod_height, 3)}".rjust(
                    15
                )
                + f" '{instruct.comment}"
                if instruct.comment
                else ""
            )

    def prelude_c(self):
        for name, coord in self.coord_manifest.items():
            c_avg = coord.avg
            self.output.append(
                f"C  {name}".ljust(8)
                + f"{round(c_avg.easting, 3)}".rjust(15)
                + f"{round(c_avg.northing, 3)}".rjust(15)
                + f"{round(c_avg.elevation, 3)}".rjust(10)
            )
        self.output.append("")

    def start(self):
        self.to_instructions()
        self.first_pass()
        self.second_pass()
        
    def save(self):
        with open(self.output_path, 'w') as output_file:
            output_file.write('\n'.join( self.output))
