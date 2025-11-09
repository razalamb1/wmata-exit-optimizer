from src.egresses import get_egresses
from src.stations import load_all_stations
from src.lines import define_all_lines

egresses = get_egresses()
stations = load_all_stations(egresses)
lines = define_all_lines(stations)


for name, station in stations.items():
    if name == "Pentagon":
        for egress in station.egresses:
            print(egress.__dict__)
