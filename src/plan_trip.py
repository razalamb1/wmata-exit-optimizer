"""Plan a trip."""

import pandas as pd
from collections import defaultdict
import copy


class TripPlanner:
    def __init__(self, stations, lines, start_station, end_station):
        self.stations = stations
        self.lines = lines
        self.start_station = stations[start_station]
        self.end_station = stations[end_station]

    def plan_trip(self):
        start_lines = self.start_station.lines
        end_lines = self.end_station.lines
        union_lines = start_lines.intersection(end_lines)
        trip_info = dict()
        if union_lines:
            trip = self.plan_single_line_trip(union_lines)
            trip_info["first_leg"] = trip
            trip_info["transfer"] = False
            return trip_info
        else:
            trip = self.plan_two_line_trip(start_lines, end_lines)
            trip_info["first_leg"] = trip[0]
            trip_info["second_leg"] = trip[1]
            trip_info["transfer"] = True
            return trip_info

    def plan_two_line_trip(self, start_lines, end_lines):
        possible_trips = defaultdict(list)
        transfer_plans = self.get_transfer_plans(start_lines, end_lines)
        for t_plan in transfer_plans:
            second_leg = self.lines[t_plan["end_line"]].plan_trip(
                t_plan["transfer_station"], self.end_station
            )
            first_leg = self.lines[t_plan["start_line"]].plan_trip(
                self.start_station,
                t_plan["transfer_station"],
                transfer=True,
                transfer_line=t_plan["end_line"],
                transfer_direction=second_leg["direction"],
            )
            possible_trips[second_leg["num_stops"] + first_leg["num_stops"]].append(
                (first_leg, second_leg)
            )
        possible_trips = possible_trips[min(possible_trips)]
        trip = self.combine_trips(possible_trips)
        if not trip[0]["egresses"]:
            if not self.check_directions(trip[0]["direction"], trip[1]["direction"]):
                new_egresses = dict()
                for label, egresses in trip[1]["egresses"].items():
                    new_egresses[label] = []
                    for e in egresses:
                        new_egresses[label].append([e[0], 9 - e[1], 4 - e[2]])
                trip[0]["egresses"] = new_egresses
        return trip

    def check_directions(self, direction_1, direction_2):
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
            "Hungington",
            "Branch Avenue",
        }
        if direction_1 in one_direction and direction_2 in other_direction:
            return True
        if direction_1 in one_direction and direction_2 in one_direction:
            return True
        return False

    def get_transfer_plans(self, start_lines, end_lines):
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

    def combine_trips(self, trips):
        first_lines = set()
        first_direction = set()
        second_lines = set()
        second_direction = set()
        for trip in trips:
            first_lines.add(trip[0]["lines"])
            first_direction.add(trip[0]["direction"])
            second_lines.add(trip[1]["lines"])
            second_direction.add(trip[1]["direction"])

        first_leg = trips[0][0]
        second_leg = trips[0][1]
        first_leg["lines"] = "/".join(first_lines)
        first_leg["direction"] = "/".join(first_direction)
        second_leg["lines"] = "/".join(second_lines)
        second_leg["direction"] = "/".join(second_direction)
        return [first_leg, second_leg]

    def plan_single_line_trip(self, union_lines):
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
            trip = list(trips.values())[0]
            line_names = "/".join(list(len_dict.values())[0])
            trip["lines"] = line_names
            direction = "/".join({t["direction"] for t in trips.values()})
            trip["direction"] = direction
            return trip
        else:
            smallest_dist = min(len_dict)
            line_names = "/".join(len_dict[smallest_dist])
            trip = trips[len_dict[smallest_dist][0]]
            trip["lines"] = line_names
            return trip
