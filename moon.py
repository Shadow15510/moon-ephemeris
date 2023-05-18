#! /usr/bin/env python3
"""
Moon Ephemeris
==============

Licence
-------
The code is provided under GNU General Public Licence v3.0+.

Description
-----------
This little python app allow to get the ephemeris of the Moon for a given month. You just have to
request a month by it's index (between 1 and 12) and the ephemeris will be stored into a *.txt file.

Examples
--------
Assuming the module was imported as following:

>>> from moon import ephemeris

To have the ephemeris of the current month:

>>> emphemeris()

To have the ephemeris of March of the current year:

>>> ephemeris(3)

Notes
-----
You cannot requests the ephemeris for another year that the current, the website wich provide the
ephemeris doesn't handle this case for now.
"""
import time
import requests

from bs4 import BeautifulSoup

__version__ = "1.0.1"


# Function
def ephemeris(month: int=0):
    """
    Get the Moon's informatations for the given month and the current year
    These informations will be save into a file MONTH-YYYY.txt

    Parameters
    ----------
    month : int
        Index of the month (1-12).

    Raises
    ------
    ConnectionError
        If the connection failed, raise the HTTPS error's code.
    """
    current_time = [month, int(time.strftime("%Y", time.localtime()))]
    if not month:
        current_time[0] = int(time.strftime("%m", time.localtime()))
    current_time[0] -= 1

    months_name = [
            "JANVIER",
            "FÉVRIER",
            "MARS",
            "AVRIL",
            "MAI",
            "JUIN",
            "JUILLET",
            "AOUT",
            "SEPTEMBRE",
            "OCTOBRE",
            "NOVEMBRE",
            "DÉCEMBRE"
        ]

    # Get the website sourcecode
    sourcecode = requests.get(
            f"https://www.pleine-lune.org/calendrier-lunaire-{current_time[1]}",
            timeout=10
        )
    if sourcecode.status_code != 200:
        raise ConnectionError(
                f"an error occurs, HTTPS error's code: {sourcecode.status_code}"
            )
    soup = BeautifulSoup(sourcecode.text, features="html5lib")

    # Get the moon ephemeris for the current year
    months = soup.find("th", {"class": "month-cell p-3 h5", "rowspan": "9"}).parent.parent

    # Detection of the right month and convert raw data to human readable format
    raw_data = months.text.splitlines()
    raw_data = [i.strip().rstrip() for i in raw_data if i.split()]

    start = raw_data.index(f"{months_name[current_time[0]]} {current_time[1]}") + 1
    end = None
    if current_time[0] != 11:
        end = raw_data.index(f"{months_name[(current_time[0] + 1) % 12]} {current_time[1]}")
    raw_data = raw_data[start: end]

    info = f"{months_name[current_time[0]]} {current_time[1]}"
    info += "\n" + "-" * len(info) + "\n"
    for i in range(0, len(raw_data), 6):
        if not raw_data[i][2: ].startswith("Noeud"):
            if raw_data[i] == "Périgée":
                info += f"Le {raw_data[i + 1][: -5]}, la Lune passera au périgée, c'est-à-dire au"\
                        f"plus près de la Terre, avec une distance de {raw_data[i + 3]}.\n\n"
            elif raw_data[i] == "Apogée":
                info += f"Le {raw_data[i + 1][: -5]}, la Lune passera à l'apogée, c'est-à-dire à"\
                        f"une distance maximale de la Terre, avec {raw_data[i + 3]}.\n\n"
            else:
                constellation = "du"
                if raw_data[i + 5][: -2] in ("Balance", "Vierge"):
                    constellation = "de la"
                elif raw_data[i + 5][: -2] in ("Gémeaux", "Poissons"):
                    constellation = "des"
                eclipse = ('', ' à ' + raw_data[i + 2])['Eclipse' in raw_data[i]]
                info += f"{raw_data[i]} le {raw_data[i + 1][: -5]}{eclipse} dans la constellation"\
                        f"{constellation} {raw_data[i+5][: -2]} à {raw_data[i + 3]}.\n\n"

    info = info.replace("( ", "(").replace(" )", ")")

    with open(
            f"{months_name[current_time[0]]}-{current_time[1]}.txt",
            "w",
            encoding="utf-8"
        ) as file:
        file.write(info)
