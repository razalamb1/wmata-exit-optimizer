from flask import Flask, render_template, request

from src.plan_trip import TripPlanner
from src.load_data import egresses, stations, lines


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        start = request.form.get("start_station")
        end = request.form.get("end_station")
        tp = TripPlanner(stations, lines, start, end)
        result = tp.plan_trip()
        # Add station to return object
        result["start_station"] = start
        result["end_station"] = end
    return render_template(
        "index.html", stations=sorted(stations.keys()), trip_info=result
    )


if __name__ == "__main__":
    app.run()
