from src.egresses import get_egresses, Egress


class Station:
    def __init__(self, egresses: list[Egress], lines: list[str]):
        self.egresses = egresses
        self.lines = lines
        self.name = egresses[0].station


def load_all_stations(egresses: list[Egress]) -> dict[str:Station]:
    """Load all the stations given all egresses."""
    stations = dict()
    unique_station_names = set()
    for egress in egresses:
        unique_station_names.add(egress.station)
    for station_name in unique_station_names:
        egresses_for_station = []
        lines = set()
        for egress in egresses:
            if egress.station == station_name:
                egresses_for_station.append(egress)
                for l in egress.lines:
                    lines.add(l)
        stations[station_name] = Station(egresses_for_station, lines)
    return stations


if __name__ == "__main__":
    egresses = get_egresses()
    stations = load_all_stations(egresses)
    print(stations["Metro Center"].__dict__)
