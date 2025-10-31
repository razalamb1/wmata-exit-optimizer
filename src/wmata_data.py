"""Import data for application."""

import pandas as pd

doors = pd.read_csv("data/Doors.csv")

egresses = pd.read_csv("data/Egresses.csv")

exits = pd.read_csv("data/Exits.csv")

stations = pd.read_csv("data/Stations.csv")
