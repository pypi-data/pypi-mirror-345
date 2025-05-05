<h1 align="center">PythonRMV</h1>

<p align="center">
<a href="https://git.end-play.xyz/profitroll/PythonRMV/src/branch/master/LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-blue"></a>
<a href="https://git.end-play.xyz/profitroll/PythonRMV"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>  

Small module that makes your journey with RMV REST API somehow easier. Based fully on official RMV API reference and HAFAS documentation.

## Requirements

* RMV API key (Get it [here](https://opendata.rmv.de/site/start.html))
* Python 3.9+
* git (Only for installation from source)

## Installation

If you have everything listed in [requirements](#requirements), then let's begin.

### Variant 1

`python -m pip install pyrmv`

### Variant 2

`python -m pip install git+https://git.end-play.xyz/profitroll/PythonRMV.git`

## Usage

```py
import pyrmv

# Define a Client with API key
client = pyrmv.Client("AcessId")

# Get origin's and destination's location
origin = client.stop_by_name("Frankfurt Hauptbahnhof", max_number=3)[0]
destination = client.stop_by_coords(50.099613, 8.685449, max_number=3)[0]

# Find a trip by locations you got above
trip = client.trip_find(origin_id=origin.id, dest_id=destination.id)
```

## Frequently Asked Questions

* [Why are there raw versions and formatted ones?](#why-are-there-raw-versions-and-formatted-ones)
* [Some methods work slightly different](#some-methods-work-slightly-different)

### Why are there raw versions and formatted ones?

For the purposes of my projects I don't really need all the stuff RMV gives (even though it's not much).
I only need some specific things. However I do understand that in some cases other users may find
those methods quite useful so I implemented them as well.

### Some methods work slightly different

Can be. Not all function arguments written may work perfectly because I simply did not test each and
every request. Some of arguments may be irrelevant in my use-case and the others are used quite rare at all.
Just [make an issue](https://git.end-play.xyz/profitroll/PythonRMV/issues/new) and I'll implement it correct when I'll have some free time.

## To-Do

### General

* [ ] Docs in Wiki
* [ ] Tickets
