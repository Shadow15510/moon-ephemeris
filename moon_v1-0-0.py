#! /usr/bin/env python3
# Moon Ephemeris version 1.0.0
# provided under licence GNU General Public Licence v3.0

from bs4 import BeautifulSoup
import requests
import time

# Get current month and year
current_time = list(map(lambda x: int(x), time.strftime("%m,%Y", time.localtime()).split(",")))
if current_time[0] == 12:
    current_time[0] = 0
    current_time[1] += 1

months_name = ["JANVIER", "FÉVRIER", "MARS", "AVRIL", "MAI", "JUIN", "JUILLET", "AOUT", "SEPTEMBRE", "OCTOBRE", "NOVEMBRE", "DECEMBRE"]

class ConnectionError(Exception):
    pass

def get_moon_info():
    # Get the website sourcecode
    sourcecode = requests.get("https://www.pleine-lune.org/calendrier-lunaire-{}#calendrier".format(current_time[1]))
    if sourcecode.status_code != 200:
        raise ConnectionError("Une erreur de connection est survenue. Code : {}".format(sourcecode.status_code))
    soup = BeautifulSoup(sourcecode.text, features="html5lib")

    # Get the moon ephemeris for the current year
    months = soup.find("th", {"class": "align-middle", "rowspan": "9", "style": "transform: rotate(270deg);"}).parent.parent

    # Detection of the right month and convert raw data to human readable format 
    raw_data = months.text.splitlines()
    raw_data = [i.strip().rstrip() for i in raw_data if i.split()]
    
    start = raw_data.index("{} {}".format(months_name[current_time[0]], current_time[1])) + 1
    end = None
    if current_time[0] != 11:
        end = raw_data.index("{} {}".format(months_name[(current_time[0] + 1) % 12], current_time[1]))
    raw_data = raw_data[start: end]

    info = "En {} {}\n\n".format(months_name[current_time[0]], current_time[1])
    for i in range(0, len(raw_data), 6):
        if not raw_data[i].startswith("Noeud"):
            if raw_data[i] == "Périgée":
                info += "Le {}, la Lune passera au périgée, c'est-à-dire au plus près de la Terre, avec une distance de {}.\n\n".format(raw_data[i + 1][: -5], raw_data[i + 3])
            elif raw_data[i] == "Apogée": 
                info += "Le {}, la Lune passera à l'apogée, c'est-à-dire à une distance maximale de la Terre, avec {}.\n\n".format(raw_data[i + 1][: -5], raw_data[i + 3])
            else:
                constellation = "du"
                if raw_data[i + 5][: -2] in ("Balance", "Vierge"): constellation = "de la"
                elif raw_data[i + 5][: -2] in ("Gémeaux", "Poissons"): constellation = "des"
                info += "{} le {}{} dans la constellation {} {} à {}.\n\n".format(raw_data[i], raw_data[i + 1][: -5], ('', ' à ' + raw_data[i + 2])['Eclipse' in raw_data[i]], constellation, raw_data[i+5][: -2], raw_data[i + 3])
    
    return info

with open("{}_{}.txt".format(months_name[current_time[0]], current_time[1]), "w") as file:
   file.write(get_moon_info())
   file.close()
