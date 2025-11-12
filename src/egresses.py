"""Defining Exits."""

from src.wmata_data import doors, egresses, exits, stations
import pandas as pd
import numpy as np
import re

LINES = ["RD", "GR", "YL", "BL", "SV", "OR"]

label_stations = set()


def get_lines_at_station(station_name: str) -> list[str]:
    """Find all the lines that exist at a given station."""
    lines_at_station = set()
    for l in LINES:
        station = stations.loc[stations["nameStd"] == station_name, f"has{l}"].item()
        if pd.notna(station):
            lines_at_station.add(l)
    return lines_at_station


direction = {1: "eastbound", 2: "westbound"}


class Egress:
    """A single Egress at a metro station. This could be an exit, escalator, elevator, or stairs."""

    def __init__(
        self,
        station: str,
        icon: str,
        x: float,
        dir: str,
        label: str,
        lines: list[str],
        preferred: str,
        transfer: bool,
        transfer_lines: str,
        transfer_direction: str,
    ):
        self.station = re.sub(r" \((Lower|Upper) Level\)$", "", station)
        self.icon = icon
        # Define car/door position
        self.get_door(x)
        self.dir = dir
        self.label = label
        self.lines = lines
        self.preferred = preferred
        self.get_transfer_information(transfer, transfer_lines, transfer_direction)

    def get_transfer_information(
        self, transfer: bool, transfer_lines: str, transfer_direction: str
    ):
        """Store transfer information."""
        if pd.isna(transfer):
            self.transfer = None
            self.transfer_lines = None
            self.transfer_direction = None
        elif pd.isna(transfer_lines):
            self.transfer = transfer
            self.transfer_lines = None
            self.transfer_direction = None
        elif pd.isna(transfer_direction):
            self.transfer = transfer
            self.transfer_lines = re.findall(r"\b[A-Z]{2}\b", transfer_lines)
            self.transfer_direction = None
        else:
            self.transfer = transfer
            self.transfer_lines = re.findall(r"\b[A-Z]{2}\b", transfer_lines)
            if transfer_direction == "both":
                self.transfer_direction = transfer_direction
            else:
                self.transfer_direction = [
                    x.strip()
                    for x in re.search(r"\[([^\]]+)\]", transfer_direction)
                    .group(1)
                    .split(",")
                ]

    def get_door(self, x: float):
        """Get car and door # from x position."""
        differences = np.abs(doors["x"] - x)
        nearest_index = differences.argsort()[0]
        row = doors.iloc[nearest_index]
        car = row["Car"]
        position = doors[doors["Car"] == car].index.get_loc(row.name) + 1
        self.car = int(car.item())
        self.door = position

    def is_transfer(self, transfer_line: str, direction: str) -> bool:
        """Returns whether this egress is a transfer point for given line and direction."""
        if self.transfer_lines:
            if transfer_line in self.transfer_lines:
                if (self.transfer_direction == "both") or (
                    direction in self.transfer_direction
                ):
                    return True
        return False

    def get_exit_info(self, direction: str, line: str) -> dict:
        """Returns information for this egress in ditionary format"""
        if self.dir:
            if direction != self.dir:
                return None
        if line not in self.lines:
            return None
        exit_info = dict()
        exit_info["preferred"] = self.preferred
        exit_info["label"] = self.label
        exit_info["icon"] = self.icon
        if direction == "eastbound":
            exit_info["car"] = 9 - self.car
            exit_info["door"] = 4 - self.door
        else:
            exit_info["car"] = self.car
            exit_info["door"] = self.door
        return exit_info


def get_egresses() -> list[Egress]:
    """Get all egresses from Pandas dataframe of egresses."""
    result = egresses.apply(get_one_egress, axis=1)
    return result.to_list()


def get_one_egress(row: pd.Series) -> Egress:
    """Create an Egress object from one row of egress (pandas)."""
    station = row["nameStd"]
    station_row = stations[stations["nameStd"] == station]
    if station_row["platformType"].item() in ["Gap Island", "Side"]:
        dir = direction[row["y"]]
    else:
        dir = None
    icon = row["icon"]
    x = row["x"]
    label = exits.loc[
        (exits["nameStd"] == station) & (exits["exitLabel"] == row["exitLabel"]),
        "description",
    ]

    if len(label) > 0:
        label = label.item()
        label_stations.add(station)
    else:
        label = "Main Exit"
    lines = get_lines_at_station(station)
    preferred = False
    if row["pref"] == True:
        preferred = True
    transfer = row["transfer"]
    transfer_lines = row["lines"]
    transfer_direction = row["direction"]
    if pd.notna(transfer_lines):
        transfer_lines = (
            transfer_lines.replace("[", "['").replace("]", "']").replace(", ", "', '")
        )
    one_egress = Egress(
        station,
        icon,
        x,
        dir,
        label,
        lines,
        preferred,
        transfer,
        transfer_lines,
        transfer_direction,
    )
    return one_egress


if __name__ == "__main__":
    result = get_egresses()
