"""The WMATA Lines as objects."""

from collections import defaultdict


class Line:
    def __init__(self, stations, name):
        self.name = name
        self.stations = stations
        self.transfer_stations = self.get_transfer_stations(stations)
        self.station_names = [s.name for s in stations]

    def get_transfer_stations(self, stations):
        transfers = defaultdict(list)
        for i in range(1, len(stations) - 1):
            potential_transfer = stations[i]
            previous = stations[i - 1]
            next = stations[i + 1]
            for line in potential_transfer.lines:
                if line not in next.lines or line not in previous.lines:
                    transfers[line].append(potential_transfer)
        return transfers

    def contains_station(self, station):
        for s in self.stations:
            if s.name == station:
                return True
        return False

    def reorganize_egresses(self, egress_list):
        names = set()
        reorganized_e = defaultdict(list)
        for egress in egress_list:
            names.add(egress["label"])
        for egress in egress_list:
            reorganized_e[egress["label"]].append(
                [egress["icon"], egress["car"], egress["door"]]
            )
        return reorganized_e

    def get_transfer_stations_for_line(self, line):
        return self.transfer_stations[line]

    def plan_trip(
        self,
        start_station,
        end_station,
        transfer=False,
        transfer_line=None,
        transfer_direction=None,
    ):
        trip = dict()
        direction, num_stops = self.get_direction_and_number(start_station, end_station)
        egresses = end_station.egresses
        egress_locations = []
        for egress in egresses:
            egress_info = egress.get_exit_info(direction, self.name)
            if egress_info:
                if transfer:
                    if egress.is_transfer(transfer_line, transfer_direction):
                        egress_locations.append(egress_info)
                else:
                    egress_locations.append(egress_info)
        egress_locations = self.reorganize_egresses(egress_locations)
        if direction == "eastbound":
            trip["direction"] = self.eastern_end
        else:
            trip["direction"] = self.western_end
        trip["num_stops"] = num_stops
        trip["egresses"] = egress_locations
        trip["start_station"] = start_station.name
        trip["end_station"] = end_station.name
        trip["lines"] = self.name
        return trip

    @property
    def eastern_end(self):
        return self.station_names[-1]

    @property
    def western_end(self):
        return self.station_names[0]

    def get_direction_and_number(self, start_station, end_station):
        start_index = self.station_names.index(start_station.name)
        end_index = self.station_names.index(end_station.name)
        num_stations = abs(start_index - end_index)
        if end_index > start_index:
            return "eastbound", num_stations
        else:
            return "westbound", num_stations


def define_all_lines(stations):
    red_stations = [
        "Shady Grove",
        "Rockville",
        "Twinbrook",
        "North Bethesda",
        "Grosvenor-Strathmore",
        "Medical Center",
        "Bethesda",
        "Friendship Heights",
        "Tenleytown-AU",
        "Van Ness-UDC",
        "Cleveland Park",
        "Woodley Park",
        "Dupont Circle",
        "Farragut North",
        "Metro Center",
        "Gallery Place",
        "Judiciary Square",
        "Union Station",
        "NoMa-Gallaudet U",
        "Rhode Island Avenue",
        "Brookland-CUA",
        "Fort Totten",
        "Takoma",
        "Silver Spring",
        "Forest Glen",
        "Wheaton",
        "Glenmont",
    ]
    green_stations = [
        "Greenbelt",
        "College Park-U of Md",
        "Hyattsville Crossing",
        "West Hyattsville",
        "Fort Totten",
        "Georgia Avenue-Petworth",
        "Columbia Heights",
        "U Street",
        "Shaw-Howard U",
        "Mount Vernon Square",
        "Gallery Place",
        "Archives",
        "L'Enfant Plaza",
        "Waterfront",
        "Navy Yard-Ballpark",
        "Anacostia",
        "Congress Heights",
        "Southern Avenue",
        "Naylor Road",
        "Suitland",
        "Branch Avenue",
    ]
    yellow_stations = [
        "Mount Vernon Square",
        "Gallery Place",
        "Archives",
        "L'Enfant Plaza",
        "Pentagon",
        "Pentagon City",
        "Crystal City",
        "Washington National Airport",
        "Potomac Yard",
        "Braddock Road",
        "King Street-Old Town",
        "Eisenhower Avenue",
        "Huntington",
    ]
    blue_stations = [
        "Franconia-Springfield",
        "Van Dorn Street",
        "King Street-Old Town",
        "Braddock Road",
        "Potomac Yard",
        "Washington National Airport",
        "Crystal City",
        "Pentagon City",
        "Pentagon",
        "Arlington Cemetery",
        "Rosslyn",
        "Foggy Bottom-GWU",
        "Farragut West",
        "McPherson Square",
        "Metro Center",
        "Federal Triangle",
        "Smithsonian",
        "L'Enfant Plaza",
        "Federal Center SW",
        "Capitol South",
        "Eastern Market",
        "Potomac Avenue",
        "Stadium-Armory",
        "Benning Road",
        "Capitol Heights",
        "Addison Road",
        "Morgan Boulevard",
        "Downtown Largo",
    ]

    silver_stations = [
        "Ashburn",
        "Loudoun Gateway",
        "Washington Dulles International Airport",
        "Innovation Center",
        "Herndon",
        "Reston Town Center",
        "Wiehle-Reston East",
        "Spring Hill",
        "Greensboro",
        "Tysons",
        "McLean",
        "East Falls Church",
        "Ballston-MU",
        "Virginia Square-GMU",
        "Clarendon",
        "Court House",
        "Rosslyn",
        "Foggy Bottom-GWU",
        "Farragut West",
        "McPherson Square",
        "Metro Center",
        "Federal Triangle",
        "Smithsonian",
        "L'Enfant Plaza",
        "Federal Center SW",
        "Capitol South",
        "Eastern Market",
        "Potomac Avenue",
        "Stadium-Armory",
        "Benning Road",
        "Capitol Heights",
        "Addison Road",
        "Morgan Boulevard",
        "Downtown Largo",
    ]
    orange_stations = [
        "Vienna",
        "Dunn Loring",
        "West Falls Church",
        "East Falls Church",
        "Ballston-MU",
        "Virginia Square-GMU",
        "Clarendon",
        "Court House",
        "Rosslyn",
        "Foggy Bottom-GWU",
        "Farragut West",
        "McPherson Square",
        "Metro Center",
        "Federal Triangle",
        "Smithsonian",
        "L'Enfant Plaza",
        "Federal Center SW",
        "Capitol South",
        "Eastern Market",
        "Potomac Avenue",
        "Stadium-Armory",
        "Minnesota Avenue",
        "Deanwood",
        "Cheverly",
        "Landover",
        "New Carrollton",
    ]
    red = Line([stations[s] for s in red_stations], "RD")
    green = Line([stations[s] for s in green_stations], "GR")
    yellow = Line([stations[s] for s in yellow_stations], "YL")
    blue = Line([stations[s] for s in blue_stations], "BL")
    silver = Line([stations[s] for s in silver_stations], "SV")
    orange = Line([stations[s] for s in orange_stations], "OR")
    return {
        "RD": red,
        "GR": green,
        "YL": yellow,
        "BL": blue,
        "OR": orange,
        "SV": silver,
    }
