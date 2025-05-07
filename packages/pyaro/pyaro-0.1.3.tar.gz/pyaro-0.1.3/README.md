# pyaro - Airquality Reader-interface for Observations

![pyaro-logo](docs/pics/pyaro256.png "The library that solves the mystery of reading airquality measurement databases.")

The library that solves the mystery of reading airquality measurement databases. (Pronunciation as in French: Poirot)

## About

Pyaro is an interface which uses a simple access pattern to different air-pollution databases.
The goal of pyro was threefold.

1. A simple interface for different types of air-pollution databases
2. A programmatic interface to these databases easily usable by large applications like [PyAerocom](https://pyaerocom.readthedocs.io)
3. Easy extension for air-pollution database providers or programmers giving the users (1. or 2.) direct access
    their databases without the need of a new API.

A few existing implementations of pyaro can be found at [pyaro-readers](https://github.com/metno/pyaro-readers).


## Installation
`python -m pip install 'pyaro@git+https://github.com/metno/pyaro.git'`

This will install pyaro and all its dependencies (numpy).


## Usage

```python

import pyaro.timeseries
TEST_FILE = "csvReader_testdata.csv"
engines = pyaro.list_timeseries_engines()
# {'csv_timeseries': <pyaro.csvreader.CSVTimeseriesReader.CSVTimeseriesEngine object at 0x7fcbe67eab00>}
print(engines['csv_timeseries'].args)
# ('filename', 'columns', 'variable_units', 'csvreader_kwargs', 'filters')
print(pyaro.timeseries.filters.list)
# immutable dict of all filter-names to filter-classes
print(engines['csv_timeseries'].supported_filters())
# list of filter-classes supported by this reader
print(pyaro.timeseries.filters.list)

with engines['csv_timeseries'].open(
    filename=TEST_FILE,
    filters={'countries': {include=['NO']}}
    ) as ts:
    for var in ts.variables():
        # stations
        ts.data(var).stations
        # start_times
        ts.data(var).start_times
        # stop_times
        ts.data(var).end_times
        # latitudes
        ts.data(var).latitudes
        # longitudes
        ts.data(var).longitudes
        # altitudes
        ts.data(var).altitudes
        # values
        ts.data(var).values
        # flags
        ts.data(var).flags


        # if pandas is installed, data can be converted to a pandas Dataframe
        df = pyaro.timeseries_data_to_pd(data)

```


## Supported readers
* csv_timeseries
Reader for all tables readable with the python csv module.
The reader supports reading from a single local file, with csv-parameters added on the command-line.

## Usage - csv_timeseries
```python
import pyaro.timeseries
TEST_FILE = "csvReader_testdata.csv"
engine = pyaro.list_timeseries_engines()["csv_timeseries"]
ts = engine.open(TEST_FILE, filters=[], fill_country_flag=False)
print(ts.variables())
# stations
ts.data('SOx').stations
# start_times
ts.data('SOx').start_times
# stop_times
ts.data('SOx'.end_times
# latitudes
ts.data('SOx').latitudes
# longitudes
ts.data('SOx').longitudes
# altitudes
ts.data('SOx').altitudes
# values
ts.data('SOx').values

```



## COPYRIGHT

Copyright (C) 2023  Heiko Klein, Daniel Heinesen, Norwegian Meteorological Institute

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, see https://www.gnu.org/licenses/
