#/usr/bin/env python3

import requests
import re
import json
from datetime import datetime
from collections import defaultdict
import time

def datetime_from_utc_timestamp_to_local(utc_timestamp_millis):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return datetime.utcfromtimestamp(utc_timestamp_millis / 1000) + offset


def get_list_of_cinemas():
    body = requests.get("https://zagreb.cinestarcinemas.hr/").text
    # find the json data in the html response
    json_str = re.findall("var pmkinoFrontVars = (.*);", body)[0]
    json_data = json.loads(json_str)

    json_cinemas = json_data["apiData"]["cinemas"]["items"]
    return [{"name": c["nameDisplay"], "url": c["website"]} for c in json_cinemas.values()]


def get_performances_from_movie(movie: dict):
    performances = movie["performances"]
    mapped_performances = []
    for performance in performances:
        attributes = " ".join(sorted(attribute["name"] for attribute in performance["attributes"]))
        performance_time = performance["timeUtc"]
        performance_datetime = datetime_from_utc_timestamp_to_local(performance_time)
        performance_datetime_string = performance_datetime.strftime('%Y-%m-%d %H:%M:%S (%a)')

        mapped_performances.append({"datetime": performance_datetime_string, "attributes": attributes})

    return sorted(mapped_performances, key=lambda d: d['datetime'])


def get_movies_schedules_by_cinema(cinema_name_filter: str = None):
    cinemas = get_list_of_cinemas()

    if cinema_name_filter:
        cinemas = [cinema for cinema in cinemas if cinema_name_filter.lower() in cinema["name"].lower()]

    movies_dict = defaultdict(lambda: defaultdict(dict))
    for cinema in cinemas:
        body = requests.get(cinema["url"]).text
        json_str = re.findall("var pmkinoFrontVars = (.*);", body)[0]
        json_data = json.loads(json_str)
        movies = json_data["apiData"]["movies"]["items"].items()
        for _, movie in movies:
            mapped_performances = get_performances_from_movie(movie)
            movies_dict[movie["title"]][cinema["name"]] = mapped_performances

    return movies_dict


print(json.dumps(get_movies_schedules_by_cinema("Zagreb"), ensure_ascii= False))
