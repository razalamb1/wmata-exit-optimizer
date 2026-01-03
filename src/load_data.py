from src.egresses import get_egresses
from src.stations import load_all_stations
from src.lines import define_all_lines
import requests
from dotenv import load_dotenv
import os

egresses = get_egresses()
stations = load_all_stations(egresses)
lines = define_all_lines(stations)


load_dotenv()

name_matching = dict()

name_fix = {
    "Woodley Park-Zoo/Adams Morgan": "Woodley Park",
    "Gallery Pl-Chinatown": "Gallery Place",
    "Rhode Island Ave-Brentwood": "Rhode Island Avenue",
    "Ronald Reagan Washington National Airport": "Washington National Airport",
    "King St-Old Town": "King Street-Old Town",
    "Potomac Ave": "Potomac Avenue",
    "Minnesota Ave": "Minnesota Avenue",
    "Mt Vernon Sq 7th St-Convention Center": "Mount Vernon Square",
    "U Street/African-Amer Civil War Memorial/Cardozo": "U Street",
    "Georgia Ave-Petworth": "Georgia Avenue-Petworth",
    "Archives-Navy Memorial-Penn Quarter": "Archives",
    "Branch Ave": "Branch Avenue",
    "Addison Road-Seat Pleasant": "Addison Road",
    "Dunn Loring-Merrifield": "Dunn Loring",
    "Vienna/Fairfax-GMU": "Vienna",
}

key = os.environ["WMATA_KEY"]
sesh = requests.Session()
headers = {"api_key": key}
validate_url = "https://api.wmata.com/Rail.svc/json/jStations"

req = sesh.get(validate_url, headers=headers)
stations_wmata = req.json()["Stations"]
station_names = list(stations.keys())

for station in stations_wmata:
    name = station["Name"]
    if name not in station_names:
        name = name_fix[name]
    assert name in station_names
    for linecode in ["LineCode1", "LineCode2", "LineCode3", "LineCode4"]:
        if station[linecode]:
            name_matching[(name, station[linecode])] = station["Code"]
