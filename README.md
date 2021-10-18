## busyboulder 🧗

Check climbing gym occupancy using the command line.

Currently supported gym chains:
 - Seattle Bouldering Project
 - Edgeworks (Stone Gardens)
 - Vertical World

## Installation

The easiest way to install this package is to use Python's `pip`.
```
$ pip install busyboulder
```

Alternatively, clone this package and install manually:
```
$ git clone https://github.com/chillel/busyboulder
$ cd busyboulder && pip install .
```

## Usage

Check out the user guide by typing the following:
```
$ busyboulder --help
```

To get occupancy info for "Seattle Bouldering Project", try the following:
<pre>
$ busyboulder --gym "sbp"

<b>Seattle Bouldering Project Poplar (POP)</b>
Visitors: 115, Capacity 880, 13% full.
Last updated: Last updated: now  (9:13 PM)
<b>Seattle Bouldering Project Upper Walls (UPW)</b>
Visitors: 11, Capacity 160, 7% full.
Last updated: Last updated: 3 mins ago (9:10 PM)
<b>Seattle Bouldering Project Fremont (FRE)</b>
Visitors: 62, Capacity 441, 14% full.
Last updated: Last updated: now  (9:13 PM)
</pre>

## Supporting New Gyms

Please refer to the README in the data directory, [here.](./src/busyboulder/data/README.md)