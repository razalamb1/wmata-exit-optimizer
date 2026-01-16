"""Plan a trip."""

import pandas as pd
from collections import defaultdict
from src.stations import Station
from src.lines import Line
from src.load_data import key
import requests
from rapidfuzz import process, fuzz


def closest_string(target, candidates):
    match, score, _ = process.extractOne(target, candidates, scorer=fuzz.ratio)
    return match


class TripPlanner:
    def __init__(
        self,
        stations: dict[str:Station],
        lines: dict[str:Line],
        name_matching: dict[tuple[str], str],
        start_station: str,
        end_station: str,
    ):
        self.stations = stations
        self.lines = lines
        self.name_matching = name_matching
        self.name_matching_r = {v: k for k, v in name_matching.items()}

        self.start_station = stations[start_station]
        self.end_station = stations[end_station]

    def plan_trip(self) -> dict:
        """Plan a trip."""
        start_lines = self.start_station.lines
        end_lines = self.end_station.lines
        union_lines = start_lines.intersection(end_lines)
        trip_info = dict()
        if union_lines:
            trip = self.plan_single_line_trip(union_lines)
            trip_info["first_leg"] = trip
            trip_info["transfer"] = False
            train_arrivals = self.get_train_arrivals(
                trip["start_station"],
                trip["end_station"],
                list(trip["lines"].keys()),
            )
            trip_info["first_leg_arrivals"] = train_arrivals
            return trip_info
        else:
            trip = self.plan_two_line_trip(start_lines, end_lines)
            trip_info["first_leg"] = trip[0]
            trip_info["second_leg"] = trip[1]
            trip_info["transfer"] = True
            first_train_arrivals = self.get_train_arrivals(
                trip[0]["start_station"],
                trip[0]["end_station"],
                list(trip[0]["lines"].keys()),
            )
            second_train_arrivals = self.get_train_arrivals(
                trip[1]["start_station"],
                trip[1]["end_station"],
                list(trip[1]["lines"].keys()),
            )
            trip_info["first_leg_arrivals"] = first_train_arrivals
            trip_info["second_leg_arrivals"] = second_train_arrivals
            return trip_info

    def plan_two_line_trip(self, start_lines, end_lines):
        possible_trips = defaultdict(list)
        transfer_plans = self.get_transfer_plans(start_lines, end_lines)
        for i, t_plan in enumerate(transfer_plans):
            print("--------------------------------------")
            print(f"TRANSFER PLAN {i}")
            print(f"Start Line: {t_plan["start_line"]}")
            print(f"End Line: {t_plan["end_line"]}")
            print(f"Transfer Station: {t_plan["transfer_station"].name}")
            second_leg = self.lines[t_plan["end_line"]].plan_trip(
                t_plan["transfer_station"], self.end_station
            )
            first_leg = self.lines[t_plan["start_line"]].plan_trip(
                self.start_station,
                t_plan["transfer_station"],
                transfer=True,
                transfer_line=t_plan["end_line"],
                transfer_direction=list(second_leg["lines"].values())[0],
            )
            print(f"Num Stops: {second_leg["num_stops"] + first_leg["num_stops"]}")
            possible_trips[second_leg["num_stops"] + first_leg["num_stops"]].append(
                (first_leg, second_leg)
            )
        possible_trips = possible_trips[min(possible_trips)]
        for possible_trip in possible_trips:
            print(possible_trip)
        trip = self.combine_trips(possible_trips)
        if not trip[0]["egresses"]:
            if not self.check_directions(
                list(trip[0]["lines"].values())[0], list(trip[1]["lines"].values())[0]
            ):
                new_egresses = dict()
                for label, egresses in trip[1]["egresses"].items():
                    new_egresses[label] = []
                    for e in egresses:
                        new_egresses[label].append([e[0], 9 - e[1], 4 - e[2]])
                trip[0]["egresses"] = new_egresses
        return trip

    def check_directions(self, direction_1: str, direction_2: str) -> bool:
        """Check the directions of two lines."""
        one_direction = {
            "Downtown Largo",
            "New Carrolton",
            "Mount Vernon Square",
            "Greenbelt",
        }
        other_direction = {
            "Franconia-Springfield",
            "Ashburn",
            "Vienna",
            "Huntington",
            "Branch Avenue",
        }
        if direction_1 in one_direction and direction_2 in one_direction:
            return True
        if direction_1 in other_direction and direction_2 in other_direction:
            return True
        return False

    def get_transfer_plans(self, start_lines: str, end_lines: str) -> list[dict]:
        """Get transfer plans."""
        transfer_plans = []
        for s_line in start_lines:
            for e_line in end_lines:
                transfer_stations = self.lines[s_line].get_transfer_stations_for_line(
                    e_line
                )
                for ts in transfer_stations:
                    transfer_plan = dict()
                    transfer_plan["start_line"] = s_line
                    transfer_plan["end_line"] = e_line
                    transfer_plan["transfer_station"] = ts
                    transfer_plans.append(transfer_plan)
        return transfer_plans

    def combine_trips(self, trips: list[dict]) -> list[dict]:
        """Deal with many potential trips."""
        first_lines = dict()
        second_lines = dict()
        for trip in trips:
            first_lines.update(trip[0]["lines"])
            second_lines.update(trip[1]["lines"])
        first_leg = trips[0][0]
        second_leg = trips[0][1]
        if (len(first_lines) > 1) and ("RD" in first_lines.keys()):
            first_lines.pop("RD")
        if (len(second_lines) > 1) and ("RD" in second_lines.keys()):
            second_lines.pop("RD")
        first_leg["lines"] = first_lines
        second_leg["lines"] = second_lines

        return [first_leg, second_leg]

    def plan_single_line_trip(self, union_lines: set[str]) -> dict:
        """Plan a trip along one line."""
        trips = {}
        len_dict = defaultdict(list)
        for line in union_lines:
            trip = self.lines[line].plan_trip(self.start_station, self.end_station)
            trips[line] = trip
            len_dict[trip["num_stops"]].append(line)
        if len(trips) == 1:
            return list(trips.values())[0]
        if union_lines == {"RD", "GR"}:
            return trips["RD"]
        if len(len_dict) == 1:
            main_trip = list(trips.values())[0]
            trip_line_dict = main_trip["lines"]
            for trip in list(trips.values()):
                trip_line_dict.update(trip["lines"])
            return main_trip
        else:
            smallest_dist = min(len_dict)
            main_trip = trips[len_dict[smallest_dist][0]]
            trip_line_dict = main_trip["lines"]
            for trip in trips[len_dict[smallest_dist]]:
                trip_line_dict.update(trip["lines"])
            return main_trip

    def get_train_arrivals(
        self, start_station: str, end_station: str, lines_used: list
    ):
        try:
            station_code = self.name_matching[(start_station, lines_used[0])]
            url = f"https://api.wmata.com/StationPrediction.svc/json/GetPrediction/{station_code}"
            sesh = requests.Session()
            headers = {"api_key": key}
            req = sesh.get(url, headers=headers)
            train_data = req.json()["Trains"]
            trains_return = []
            for train in train_data:
                if train["Line"] in lines_used:
                    tmp_line = self.lines[train["Line"]]
                    if train["DestinationCode"]:
                        dest = self.name_matching_r[train["DestinationCode"]][0]
                    else:
                        dest = closest_string(
                            train["Destination"], tmp_line.station_names
                        )
                    if tmp_line.is_between(start_station, dest, end_station):
                        if train["Min"] in ["BRD", "ARR"]:
                            train["Min"] = 0
                        trains_return.append(
                            {
                                "color": train["Line"],
                                "minutes": train["Min"],
                                "cars": train["Car"],
                                "destination": train["Destination"],
                            }
                        )
        except:
            trains_return = []
        return trains_return
