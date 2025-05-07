from functools import cache
import json
import logging
import math
import abc
from collections import defaultdict
import csv
from datetime import datetime
import inspect
import pathlib
import re
import sys
import types
from typing import Any

import numpy as np
import numpy.typing as npt

from .Data import Data, Flag
from .Station import Station

from ..mathutils import haversine


try:
    # Optional dependencies required for relative altitude filter.
    import xarray as xr
    from cf_units import Unit
except ImportError:
    pass

logger = logging.getLogger(__name__)


class Filter(abc.ABC):
    """Base-class for all filters used from pyaro-Readers"""

    time_format = "%Y-%m-%d %H:%M:%S"

    def __init__(self, **kwargs):
        """constructor of Filters. All filters must have a default constructor without kwargs
        for an empty filter object"""
        return

    def args(self) -> dict[str, Any]:
        """retrieve the kwargs possible to retrieve a new object of this filter with filter restrictions

        :return: a dictionary possible to use as kwargs for the new method
        """
        ba = inspect.signature(self.__class__.__init__).bind(0)
        ba.apply_defaults()
        args = ba.arguments
        args.pop("self")
        return args

    @abc.abstractmethod
    def init_kwargs(self) -> dict:
        """return the init kwargs"""

    @abc.abstractmethod
    def name(self) -> str:
        """Return a unique name for this filter

        :return: a string to be used by FilterFactory
        """

    def filter_data(
        self, data: Data, stations: dict[str, Station], variables: list[str]
    ) -> Data:
        """Filtering of data

        :param data: Data of e.g. a Reader.data(varname) call
        :param stations: List of stations, e.g. from a Reader.stations() call
        :param variables: variables, i.e. from a Reader.variables() call
        :return: a updated Data-object with this filter applied
        """
        return data

    def filter_stations(self, stations: dict[str, Station]) -> dict[str, Station]:
        """Filtering of stations list

        :param stations: List of stations, e.g. from a Reader.stations() call
        :return: dict of filtered stations
        """
        return stations

    def filter_variables(self, variables: list[str]) -> list[str]:
        """Filtering of variables

        :param variables: List of variables, e.g. from a Reader.variables() call
        :return: List of filtered variables.
        """
        return variables

    def __repr__(self):
        return f"{type(self).__name__}(**{self.init_kwargs()})"


class DataIndexFilter(Filter):
    """A abstract baseclass implementing filter_data by an abstract method
    filter_data_idx"""

    @abc.abstractmethod
    def filter_data_idx(
        self, data: Data, stations: dict[str, Station], variables: list[str]
    ):
        """Filter data to an index which can be applied to Data.slice(idx) later

        :return: a index for Data.slice(idx)
        """
        pass

    def filter_data(
        self, data: Data, stations: dict[str, Station], variables: list[str]
    ) -> Data:
        idx = self.filter_data_idx(data, stations, variables)
        return data.slice(idx)


class FilterFactoryException(Exception):
    pass


class FilterException(Exception):
    pass


class FilterFactory:
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(FilterFactory, cls).__new__(cls)
            cls.instance._filters = {}
        return cls.instance

    def register(self, filter: Filter):
        """Register a new filter to the factory
        with a filter object (might be empty)

        :param filter: a filter implementation
        """
        if filter.name() in self._filters:
            raise FilterFactoryException(
                f"Cannot use {filter}: {filter.name()} already in use by {self.get(filter.name())}"
            )
        self._filters[filter.name()] = filter

    def get(self, name, **kwargs):
        """Get a filter by name. If kwargs are given, they will be send to the
        filters new method

        :param name: a filter-name
        :return: a filter, optionally initialized
        """
        filter = self._filters[name]
        return filter.__class__(**kwargs)

    def list(self) -> dict[str, Filter]:
        """List all available filter-names and their initializations"""
        return types.MappingProxyType(self._filters)


filters = FilterFactory()


def registered_filter(filter_class):
    """Simple decorator to register a FilterClass to the FilterFactory on construction

    :param filter_class: class to register
    """
    filters.register(filter_class())
    return filter_class


class FilterCollectionException(Exception):
    pass


class FilterCollection:
    """A collection of DataIndexFilters which can be applied together.

    :param filterlist: _description_, defaults to []
    :return: _description_
    """

    def __init__(self, filterlist=[]):
        self._filters = []
        tmp_filterlist = []
        if isinstance(filterlist, dict):
            for name, kwargs in filterlist.items():
                tmp_filterlist.append(filters.get(name, **kwargs))
        else:
            tmp_filterlist = filterlist
        for f in tmp_filterlist:
            self.add(f)

    def add(self, difilter: DataIndexFilter):
        if not isinstance(difilter, DataIndexFilter):
            raise FilterCollectionException(
                f"filter not a DataIndexFilter, so can't add to collection"
            )
        else:
            self._filters.append(difilter)

    def filter_data(
        self, data: Data, stations: dict[str, Station], variables: str
    ) -> Data:
        """Filter data with all filters in this collection.

        :param data: Data from a timeseries-reader, i.e. retrieved by ts.data(varname)
        :param stations: stations-dict of a reader, i.e. retrieved by ts.stations()
        :param variables: variables of a reader, i.e. retrieved by ts.variables()
        :return: _description_
        """
        for fi in self._filters:
            data = fi.filter_data(data, stations, variables)
        return data

    def filter(self, ts_reader, variable: str) -> Data:
        """Filter the data for a variable of a reader with all filters in this collection.

        :param ts_reader: a timeseries-reader instance
        :param variable: a valid variable-name
        :return: filtered data
        """
        stations = ts_reader.stations()
        variables = ts_reader.variables()
        data = ts_reader.data(variable)
        return self.filter_data(data, stations, variables)

    def __iter__(self):
        return self._filters.__iter__()


@registered_filter
class VariableNameFilter(Filter):
    """Filter to change variable-names and/or include/exclude variables

    :param reader_to_new: dictionary from readers-variable names to new variable-names,
        e.g. used in your project, defaults to {}
    :param include: list of variables to include only (new names if changed), defaults to []
        meaning keep all variables unless excluded.
    :param exclude: list of variables to exclude (new names if changed), defaults to []
    """

    def __init__(
        self,
        reader_to_new: dict[str, str] = {},
        include: list[str] = [],
        exclude: list[str] = [],
    ):
        self._reader_to_new = reader_to_new
        self._new_to_reader = {v: k for k, v in reader_to_new.items()}
        self._include = set(include)
        self._exclude = set(exclude)
        return

    def init_kwargs(self):
        return {
            "reader_to_new": self._reader_to_new,
            "include": list(self._include),
            "exclude": list(self._exclude),
        }

    def name(self):
        return "variables"

    def reader_varname(self, new_variable: str) -> str:
        """convert a new variable name to a reader-variable name

        :param new_variable: variable name after translation
        :return: variable name in the original reader
        """
        return self._new_to_reader.get(new_variable, new_variable)

    def new_varname(self, reader_variable: str) -> str:
        """convert a reader-variable to a new variable name

        :param reader_variable: variable as used in the reader
        :return: variable name after translation
        """
        return self._reader_to_new.get(reader_variable, reader_variable)

    def filter_data(self, data, stations, variables) -> Data:
        """Translate data's variable"""
        data._set_variable(self._reader_to_new.get(data.variable, data.variable))
        return data

    def filter_variables(self, variables: list[str]) -> list[str]:
        """change variable name and reduce variables applying include and exclude parameters

        :param variables: variable names as in the reader
        :return: valid variable names in translated nomenclature
        """
        newlist = []
        for x in variables:
            newvar = self.new_varname(x)
            if self.has_variable(newvar):
                newlist.append(newvar)
        return newlist

    def has_variable(self, variable) -> bool:
        """check if a variable-name is in the list of variables applying include and exclude

        :param variable: variable name in translated, i.e. new scheme
        :return: True or False
        """
        if len(self._include) > 0:
            if not variable in self._include:
                return False
        if variable in self._exclude:
            return False
        return True

    def has_reader_variable(self, variable) -> bool:
        """Check if variable-name is in the list of variables applying include and exclude

        :param variable: variable as returned from the reader
        :return: True or False
        """
        new_var = self.new_varname(variable)
        return self.has_variable(new_var)


class StationReductionFilter(DataIndexFilter):
    """Abstract method for all filters, which work on reducing the number of stations only.

    The filtering of stations has to be implemented by subclasses, while filtering of data
    is already implemented.
    """

    @abc.abstractmethod
    def filter_stations(self, stations: dict[str, Station]) -> dict[str, Station]:
        pass

    def filter_data_idx(
        self, data: Data, stations: dict[str, Station], variables: list[str]
    ):
        stat_names = self.filter_stations(stations).keys()
        dstations = data.stations
        stat_names = np.fromiter(stat_names, dtype=dstations.dtype)
        index = np.isin(dstations, stat_names)
        return index


@registered_filter
class StationFilter(StationReductionFilter):
    def __init__(self, include: list[str] = [], exclude: list[str] = []):
        self._include = set(include)
        self._exclude = set(exclude)
        return

    def init_kwargs(self):
        return {"include": list(self._include), "exclude": list(self._exclude)}

    def name(self):
        return "stations"

    def has_station(self, station) -> bool:
        if len(self._include) > 0:
            if station not in self._include:
                return False
        if station in self._exclude:
            return False
        return True

    def filter_stations(self, stations: dict[str, Station]) -> dict[str, Station]:
        return {s: v for s, v in stations.items() if self.has_station(s)}


@registered_filter
class CountryFilter(StationReductionFilter):
    """Filter countries by ISO2 names (capitals!)

    :param include: countries to include, defaults to [], meaning all countries
    :param exclude: countries to exclude, defaults to [], meaning none
    """

    def __init__(self, include: list[str] = [], exclude: list[str] = []):
        self._include = set(include)
        self._exclude = set(exclude)
        return

    def init_kwargs(self):
        return {"include": list(self._include), "exclude": list(self._exclude)}

    def name(self):
        return "countries"

    def has_country(self, country) -> bool:
        if len(self._include) > 0:
            if country not in self._include:
                return False
        if country in self._exclude:
            return False
        return True

    def filter_stations(self, stations: dict[str, Station]) -> dict[str, Station]:
        return {s: v for s, v in stations.items() if self.has_country(v.country)}


class BoundingBoxException(Exception):
    pass


@registered_filter
class BoundingBoxFilter(StationReductionFilter):
    """Filter using geographical bounding-boxes. Coordinates should be given in the range
    [-180,180] (degrees_east) for longitude and [-90,90] (degrees_north) for latitude.
    Order of coordinates is clockwise starting with north, i.e.: (north, east, south, west) = NESW

    :param include: bounding boxes to include. Each bounding box is a tuple of four float for
        (NESW),  defaults to [] meaning no restrictions
    :param exclude: bounding boxes to exclude. Defaults to []
    :raises BoundingBoxException: on any errors of the bounding boxes
    """

    def __init__(
        self,
        include: list[tuple[float, float, float, float]] = [],
        exclude: list[tuple[float, float, float, float]] = [],
    ):
        for tup in include:
            self._test_bounding_box(tup)
        for tup in exclude:
            self._test_bounding_box(tup)

        self._include = set(include)
        self._exclude = set(exclude)
        return

    def _test_bounding_box(self, tup):
        """_summary_

        :param tup: A bounding-box tuple of form (north, east, south, west)
        :raises BoundingBoxException: on any errors of the bounding box
        """
        if len(tup) != 4:
            raise BoundingBoxException(f"({tup}) has not four NESW elements")
        if not (-90 <= tup[0] <= 90):
            raise BoundingBoxException(f"north={tup[0]} not within [-90,90] in {tup}")
        if not (-90 <= tup[2] <= 90):
            raise BoundingBoxException(f"south={tup[2]} not within [-90,90] in {tup}")
        if not (-180 <= tup[1] <= 180):
            raise BoundingBoxException(f"east={tup[1]} not within [-180,180] in {tup}")
        if not (-180 <= tup[3] <= 180):
            raise BoundingBoxException(f"west={tup[3]} not within [-180,180] in {tup}")
        if tup[0] < tup[2]:
            raise BoundingBoxException(f"north={tup[0]} < south={tup[2]} in {tup}")
        if tup[1] < tup[3]:
            raise BoundingBoxException(f"east={tup[1]} < west={tup[3]} in {tup}")
        return True

    def init_kwargs(self):
        return {"include": list(self._include), "exclude": list(self._exclude)}

    def name(self):
        return "bounding_boxes"

    def has_location(self, latitude, longitude):
        """Test if the locations coordinates are part of this filter.

        :param latitude: latitude coordinate in degree_north [-90, 90]
        :param longitude: longitude coordinate in degree_east [-180, 180]
        """
        if len(self._include) == 0:
            inside_include = True
        else:
            inside_include = False
            for n, e, s, w in self._include:
                if not inside_include:  # one inside test is enough
                    if s <= latitude <= n:
                        if w <= longitude <= e:
                            inside_include = True

        if not inside_include:
            return False  # no more tests required

        outside_exclude = True
        for n, e, s, w in self._exclude:
            if (
                outside_exclude
            ):  # if known to be inside of any other exclude BB, no more tests
                if s <= latitude <= n:
                    if w <= longitude <= e:
                        outside_exclude = False

        return inside_include & outside_exclude

    def filter_stations(self, stations: dict[str, Station]) -> dict[str, Station]:
        return {
            s: v
            for s, v in stations.items()
            if self.has_location(v.latitude, v.longitude)
        }


@registered_filter
class FlagFilter(DataIndexFilter):
    """Filter data by Flags

    :param include: flags to include, defaults to [], meaning all flags
    :param exclude: flags to exclude, defaults to [], meaning none
    """

    def __init__(self, include: list[Flag] = [], exclude: list[Flag] = []):
        self._include = set(include)
        if len(include) == 0:
            all_include = set([f for f in Flag])
        else:
            all_include = self._include
        self._exclude = set(exclude)
        self._valid = all_include.difference(self._exclude)
        return

    def name(self):
        return "flags"

    def init_kwargs(self):
        return {"include": list(self._include), "exclude": list(self._exclude)}

    def usable_flags(self):
        return self._valid

    def filter_data_idx(
        self, data: Data, stations: dict[str, Station], variables: list[str]
    ):
        validflags = np.fromiter(self._valid, dtype=data.flags.dtype)
        index = np.isin(data.flags, validflags)
        return index


# Upper and lower bound inclusive
TimeBound = tuple[str | np.datetime64 | datetime, str | np.datetime64 | datetime]
# Internal representation
_TimeBound = tuple[np.datetime64, np.datetime64]


class TimeBoundsException(Exception):
    pass


@registered_filter
class TimeBoundsFilter(DataIndexFilter):
    """Filter data by start and/or end-times of the measurements. Each timebound consists
    of a bound-start and bound-end (both included). Timestamps are given as YYYY-MM-DD HH:MM:SS in UTC

    :param start_include: list of tuples of start-times, defaults to [], meaning all
    :param start_exclude: list of tuples of start-times, defaults to []
    :param startend_include: list of tuples of start and end-times, defaults to [], meaning all
    :param startend_exclude: list of tuples of start and end-times, defaults to []
    :param end_include: list of tuples of end-times, defaults to [], meaning all
    :param end_exclude: list of tuples of end-times, defaults to []
    :raises TimeBoundsException: on any errors with the time-bounds

    Examples:

    end_include: `[("2023-01-01 10:00:00", "2024-01-01 07:00:00")]`
    will only include observations where the end time of each observation
    is within the interval specified
    (i.e. "end" >= 2023-01-01 10:00:00 and "end" <= "2024-01-01 07:00:00")

    Including multiple bounds will act as an OR, allowing multiple selections.
    If we want every observation in January for 2021, 2022, 2023, and 2024 this
    could be made as the following filter::

        startend_include: [
            ("2021-01-01 00:00:00", "2021-02-01 00:00:00"),
            ("2022-01-01 00:00:00", "2022-02-01 00:00:00"),
            ("2023-01-01 00:00:00", "2023-02-01 00:00:00"),
            ("2024-01-01 00:00:00", "2024-02-01 00:00:00"),
        ]

    """

    def __init__(
        self,
        start_include: list[TimeBound] = [],
        start_exclude: list[TimeBound] = [],
        startend_include: list[TimeBound] = [],
        startend_exclude: list[TimeBound] = [],
        end_include: list[TimeBound] = [],
        end_exclude: list[TimeBound] = [],
    ):
        self._start_include = self._timebounds_canonicalise(start_include)
        self._start_exclude = self._timebounds_canonicalise(start_exclude)
        self._startend_include = self._timebounds_canonicalise(startend_include)
        self._startend_exclude = self._timebounds_canonicalise(startend_exclude)
        self._end_include = self._timebounds_canonicalise(end_include)
        self._end_exclude = self._timebounds_canonicalise(end_exclude)

    def name(self):
        return "time_bounds"

    def _timebounds_canonicalise(self, tuple_list: list[TimeBound]) -> list[_TimeBound]:
        retlist = []
        for start, end in tuple_list:
            if isinstance(start, str):
                start_dt = np.datetime64(datetime.strptime(start, self.time_format))
            else:
                start_dt = np.datetime64(start)
            if isinstance(end, str):
                end_dt = np.datetime64(datetime.strptime(end, self.time_format))
            else:
                end_dt = np.datetime64(end)

            if start_dt > end_dt:
                raise TimeBoundsException(
                    f"(start later than end) for (f{start} > f{end})"
                )
            retlist.append((start_dt, end_dt))
        return retlist

    def _datetime_list_to_str_list(self, tuple_list) -> list[tuple[str, str]]:
        retlist = []
        for start_dt, end_dt in tuple_list:
            retlist.append(
                (
                    start_dt.astype(datetime).strftime(self.time_format),
                    end_dt.astype(datetime).strftime(self.time_format),
                )
            )
        return retlist

    def init_kwargs(self) -> dict[str, list[tuple[str, str]]]:
        return {
            "start_include": self._datetime_list_to_str_list(self._start_include),
            "start_exclude": self._datetime_list_to_str_list(self._start_exclude),
            "startend_include": self._datetime_list_to_str_list(self._startend_include),
            "startend_exclude": self._datetime_list_to_str_list(self._startend_exclude),
            "end_include": self._datetime_list_to_str_list(self._startend_include),
            "end_exclude": self._datetime_list_to_str_list(self._startend_exclude),
        }

    def _index_from_include_exclude(
        self,
        times1: npt.NDArray[np.datetime64],
        times2: npt.NDArray[np.datetime64],
        includes: list[_TimeBound],
        excludes: list[_TimeBound],
    ):
        if len(includes) == 0:
            idx = np.repeat(True, len(times1))
        else:
            idx = np.repeat(False, len(times1))
            for start, end in includes:
                idx |= (start <= times1) & (times2 <= end)

        for start, end in excludes:
            idx &= (times1 < start) | (end < times2)

        return idx

    def has_envelope(self) -> bool:
        """Check if this filter has an envelope, i.e. a earliest and latest time"""
        return bool(
            len(self._start_include)
            or len(self._startend_include)
            or len(self._end_include)
        )

    def envelope(self) -> tuple[datetime, datetime]:
        """Get the earliest and latest time possible for this filter.

        :return: earliest start and end-time (approximately)
        :raises TimeBoundsException: if has_envelope() is False, or internal errors
        """
        if not self.has_envelope():
            raise TimeBoundsException(
                "TimeBounds-envelope called but no envelope exists"
            )
        start = np.datetime64(datetime.max)
        end = np.datetime64(datetime.min)
        for s, e in self._start_include + self._startend_include + self._end_include:
            start = min(start, s)
            end = max(end, e)
        if end < start:
            raise TimeBoundsException(
                f"TimeBoundsEnvelope end < start: {end} < {start}"
            )
        return (start.astype(datetime), end.astype(datetime))

    def contains(
        self, dt_start: npt.NDArray[np.datetime64], dt_end: npt.NDArray[np.datetime64]
    ) -> npt.NDArray[np.bool_]:
        """Test if datetimes in dt_start, dt_end belong to this filter

        :param dt_start: start of each observation as a numpy array of datetimes
        :param dt_end: end of each observation as a numpy array of datetimes
        :return: numpy boolean array with True/False values
        """
        idx = self._index_from_include_exclude(
            dt_start, dt_start, self._start_include, self._start_exclude
        )
        idx &= self._index_from_include_exclude(
            dt_start, dt_end, self._startend_include, self._startend_exclude
        )
        idx &= self._index_from_include_exclude(
            dt_end, dt_end, self._end_include, self._end_exclude
        )
        return idx

    def filter_data_idx(
        self, data: Data, stations: dict[str, Station], variables: list[str]
    ) -> npt.NDArray[np.bool_]:
        return self.contains(data.start_times, data.end_times)


@registered_filter
class TimeVariableStationFilter(DataIndexFilter):
    """Exclude combinations of variable station and time from the data

    This filter is really a cleanup of the database, but sometimes it is not possible to
    modify the original database and the cleanup needs to be done on a filter basis.

    :param exclude: tuple of 4 elements: start-time, end-time, variable, station
    :param exclude_from_csvfile: this is a helper option to enable a large list of excludes
        to be read from a "\t" separated file with columns
            start \t end \t variable \t station

        where start and end are timestamps of format YYYY-MM-DD HH:MM:SS in UTC, e.g.
        the year 2020 is:
            2020-01-01 00:00:00 \t 2020-12-31 23:59:59 \t ...

    """

    def __init__(self, exclude=[], exclude_from_csvfile=""):
        csvexclude = self._excludes_from_csv(exclude_from_csvfile)
        self._exclude = self._order_exclude(exclude + csvexclude)

    def _excludes_from_csv(self, file):
        csvexcludes = []
        if file:
            with open(file, "rt", newline="") as fh:
                crd = csv.reader(fh, delimiter="\t")
                for row in crd:
                    try:
                        if len(row) == 0:
                            continue
                        if row[0].startswith("#"):
                            continue
                        if len(row) < 4:
                            raise Exception(f"need 4 elements in row, got {len(row)}")
                        datetime.strptime(row[0], self.time_format)
                        datetime.strptime(row[1], self.time_format)
                        csvexcludes.append((row[0], row[1], row[2], row[3]))
                    except Exception as ex:
                        raise Exception(
                            f"malformated TimeVariableStationFilter exclude file, row: {row}",
                            ex,
                        )
        return csvexcludes

    def _order_exclude(self, exclude):
        """Order excludes to a dict of: [variable][start_time][end_time] -> list[stations]

        :param excludes: tuples of start-time, end-time, variable, station
        """
        retval = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))
        for start_time, end_time, variable, station in exclude:
            # make sure start and end_time can be parsed
            datetime.strptime(start_time, self.time_format)
            datetime.strptime(end_time, self.time_format)
            retval[variable][start_time][end_time].append(station)
        return retval

    def init_kwargs(self):
        retval = []
        for var, start_times in sorted(self._exclude.items()):
            for start_time, end_times in sorted(start_times.items()):
                for end_time, stations in sorted(end_times.items()):
                    for station in sorted(stations):
                        retval.append((start_time, end_time, var, station))
        # sort by start_time
        retval.sort(key=lambda x: x[1])
        return {"exclude": retval}

    def name(self):
        return "time_variable_station"

    def filter_data_idx(
        self, data: Data, stations: dict[str, Station], variables: list[str]
    ):
        idx = data.start_times.astype(bool)
        idx |= True
        if data.variable in self._exclude:
            for start_time, end_times in self._exclude[data.variable].items():
                start_time_dt = datetime.strptime(start_time, self.time_format)
                for end_time, stations in end_times.items():
                    end_time_dt = datetime.strptime(end_time, self.time_format)
                    dstations = data.stations
                    stat_names = np.fromiter(stations, dtype=dstations.dtype)
                    exclude_idx = np.isin(dstations, stat_names)
                    exclude_idx &= (start_time_dt <= data.start_times) & (
                        end_time_dt > data.start_times
                    )
                    idx &= np.logical_not(exclude_idx)
        return idx


@registered_filter
class DuplicateFilter(DataIndexFilter):
    """remove duplicates from the data. By default, data with common
    station, start_time, end_time are consider duplicates. Only one of the duplicates
    is kept.

    :param duplicate_keys: list of data-fields/columns, defaults to None, being the same
        as ["stations", "start_times", "end_times"]
    """

    default_keys = ["stations", "start_times", "end_times"]

    def __init__(self, duplicate_keys: list[str] | None = None):
        self._keys = duplicate_keys

    def init_kwargs(self):
        if self._keys is None:
            return {}
        else:
            return {"duplicate_keys": self._keys}

    def name(self):
        return "duplicates"

    def filter_data_idx(
        self, data: Data, stations: dict[str, Station], variables: list[str]
    ):
        if self._keys is None:
            xkeys = self.default_keys
        else:
            xkeys = self._keys
        return np.unique(data[xkeys], return_index=True)[1]


@registered_filter
class TimeResolutionFilter(DataIndexFilter):
    """The timeresolution filter allows to restrict the observation data to
    certain time-resolutions. Time-resolutions are not exact, and might be interpreted
    slightly differently by different observation networks.

    Default named time-resolutions are
        * minute: 59 to 61 s (+-1sec)
        * hour: 59*60 s to 61*60 s (+-1min)
        * day: 22:59:00 to 25:01:00 to allow for leap-days and a extra min
        * week: 6 to 8 days (+-1 day)
        * month: 27-33 days (30 +- 3 days)
        * year: 360-370 days (+- 5days)

    :param resolutions: a list of wanted time resolutions. A resolution consists of a integer
    number and a time-resolution name, e.g. 3 hour (no plural).
    """

    pattern = re.compile(r"\s*(\d+)\s*(\w+)\s*")
    named_resolutions = dict(
        minute=(59, 61),
        hour=(59 * 60, 61 * 60),
        day=(60 * (59 + (60 * 22)), 60 * (1 + (60 * 25))),
        week=(6 * 24 * 60 * 60, 8 * 24 * 60 * 60),
        month=(27 * 24 * 60 * 60, 33 * 24 * 60 * 60),
        year=(360 * 24 * 60 * 60, 370 * 24 * 60 * 60),
    )

    def __init__(self, resolutions: list[str] = []):
        self._resolutions = resolutions
        self._minmax = self._resolve_resolutions()

    def _resolve_resolutions(self):
        minmax_list = []
        for res in self._resolutions:
            minmax = None
            if m := self.pattern.match(res):
                count = int(m[1])
                name = m[2]
                if name in self.named_resolutions:
                    minmax = tuple(count * x for x in self.named_resolutions[name])
            if minmax is None:
                raise FilterException(f"Cannot parse time-resolution of {res}")
            else:
                minmax_list.append(minmax)
        return minmax_list

    def init_kwargs(self):
        if len(self._resolutions) == 0:
            return {}
        else:
            return {"resolutions": self._resolutions}

    def name(self):
        return "time_resolution"

    def filter_data_idx(
        self, data: Data, stations: dict[str, Station], variables: list[str]
    ):
        idx = data.start_times.astype(bool)
        idx[:] = True
        if len(self._minmax) > 0:
            idx[:] = False
            data_resolution = (data.end_times - data.start_times) / np.timedelta64(
                1, "s"
            )
            for minmax in self._minmax:
                idx |= (minmax[0] <= data_resolution) & (data_resolution <= minmax[1])
        return idx


@registered_filter
class AltitudeFilter(StationReductionFilter):
    """
    Filter which filters stations based on their altitude. Can be used to filter for a
    minimum and/or maximum altitude.

    :param min_altitude : float of minimum altitude in meters required to keep the station (inclusive).
    :param max_altitude : float of maximum altitude in meters required to keep the station (inclusive).

    If station elevation is nan, it is always excluded.
    """

    def __init__(
        self, min_altitude: float | None = None, max_altitude: float | None = None
    ):
        if min_altitude is not None and max_altitude is not None:
            if min_altitude > max_altitude:
                raise ValueError(
                    f"min_altitude ({min_altitude}) > max_altitude ({max_altitude})."
                )

        self._min_altitude = min_altitude
        self._max_altitude = max_altitude

    def init_kwargs(self):
        return {"min_altitude": self._min_altitude, "max_altitude": self._max_altitude}

    def name(self):
        return "altitude"

    def filter_stations(self, stations: dict[str, Station]) -> dict[str, Station]:
        if self._min_altitude is not None:
            stations = {
                n: s
                for n, s in stations.items()
                if (
                    not math.isnan(s["altitude"])
                    and s["altitude"] >= self._min_altitude
                )
            }

        if self._max_altitude is not None:
            stations = {
                n: s
                for n, s in stations.items()
                if (
                    not math.isnan(s["altitude"])
                    and s["altitude"] <= self._max_altitude
                )
            }

        return stations


@registered_filter
class RelativeAltitudeFilter(StationFilter):
    """
    Filter class which filters stations based on the relative difference between
    the station altitude, and the gridded topography altitude.

    :param topo_file: A .nc file from which to read gridded topography data.
    :param topo_var: Name of variable that stores altitude.
    :param rdiff: Relative difference (in meters).

    Note:
    -----
    - Stations will be kept if abs(altobs-altmod) <= rdiff.
    - Stations will not be kept if station altitude is NaN.

    Note:
    -----
    This filter requires additional dependencies (xarray, netcdf4, cf-units) to function. These can be installed
    with `pip install .[optional]
    """

    # https://cfconventions.org/Data/cf-conventions/cf-conventions-1.11/cf-conventions.html#latitude-coordinate
    _UNITS_LAT = set(
        [
            "degrees_north",
            "degree_north",
            "degree_N",
            "degrees_N",
            "degreeN",
            "degreesN",
        ]
    )

    # https://cfconventions.org/Data/cf-conventions/cf-conventions-1.11/cf-conventions.html#longitude-coordinate
    _UNITS_LON = set(
        ["degrees_east", "degree_east", "degree_E", "degrees_E", "degreeE", "degreesE"]
    )

    def __init__(
        self,
        topo_file: str | None = None,
        topo_var: str = "topography",
        rdiff: float = 0,
    ):
        if "cf_units" not in sys.modules:
            logger.info(
                "relaltitude filter is missing dependency 'cf-units'. Please install to use."
            )
        if "xarray" not in sys.modules:
            logger.info(
                "relaltitude filter is missing dependency 'xarray'. Please install to use."
            )

        self._topo_file = topo_file
        self._topo_var = topo_var
        self._rdiff = rdiff
        # topography and unit-m property initialization
        self._topography = None
        self._UNITS_METER = None

    @property
    def UNITS_METER(self):
        """internal representation of units, don't use

        :return: m-unit in internal representation

        :meta private:
        """
        if self._UNITS_METER is None:
            self._UNITS_METER = Unit("m")
        return self._UNITS_METER

    @property
    def topography(self):
        """Internal property, don't use.

        :raises ModuleNotFoundError: if cf-units or xarray is not installed
        :raises FilterException: if topograpy file is not provided
        :return: topography as internal representation

        :meta private:
        """
        if "cf_units" not in sys.modules:
            raise ModuleNotFoundError(
                "relaltitude filter is missing required dependency 'cf-units'. Please install to use this filter."
            )
        if "xarray" not in sys.modules:
            raise ModuleNotFoundError(
                "relaltitude filter is missing required dependency 'xarray'. Please install to use this filter."
            )

        if self._topography is None:
            if self._topo_file is None:
                raise FilterException(
                    f"No topography data provided (topo_file='{self._topo_file}'). Relative elevation filtering will not be applied."
                )
            else:
                try:
                    with xr.open_dataset(self._topo_file) as topo:
                        self._topography = self._convert_altitude_to_meters(topo)
                        lat, lon = self._find_lat_lon_variables(topo)
                        self._extract_bounding_box(lat, lon)
                except Exception as ex:
                    raise FilterException(
                        f"Cannot read topography from '{self._topo_file}:{self._topo_var}' : {ex}"
                    )
        return self._topography

    def _convert_altitude_to_meters(self, topo_xr):
        """
        Method which attempts to convert the altitude variable in the gridded topography data
        to meters.

        :param topo_xr xarray dataset containing topo
        :raises TypeError
            If conversion isn't possible.
        :return xr.DataArray
        """
        # Convert altitude to meters
        units = Unit(topo_xr[self._topo_var].units)
        if units.is_convertible(self.UNITS_METER):
            topography = topo_xr[self._topo_var]
            topography.values = self.UNITS_METER.convert(
                topography.values, self.UNITS_METER
            )
            topography["units"] = str(self.UNITS_METER)
        else:
            raise TypeError(
                f"Expected altitude units to be convertible to 'm', got '{units}'"
            )
        return topography

    def _find_lat_lon_variables(self, topo_xr):
        """
        Find and load DataArrays from topo which represent the latitude and longitude
        dimensions in the topography data.

        These are assigned to self._lat, self._lon, respectively for later use.

        :param topo_xr: xr.Dataset of topography
        :return: lat, lon DataArrays
        """
        for var_name in self._topography.coords:
            unit_str = self._topography[var_name].attrs.get("units", None)
            if unit_str in self._UNITS_LAT:
                lat = topo_xr[var_name]
                continue
            if unit_str in self._UNITS_LON:
                lon = topo_xr[var_name]
                continue

        if any(x is None for x in [lat, lon]):
            raise ValueError(
                f"Required variable names for lat, lon dimensions could not be found in file '{self._topo_file}"
            )
        return lat, lon

    def _extract_bounding_box(self, lat, lon):
        """
        Extract the bounding box of the grid, sets self._boundary_(north|east|south|west)
        :param lat: latitude (DataArray)
        :param lon: longitude (DataArray)
        """
        self._boundary_west = float(lon.min())
        self._boundary_east = float(lon.max())
        self._boundary_south = float(lat.min())
        self._boundary_north = float(lat.max())
        logger.info(
            "Bounding box (NESW) of topography: %.2f, %.2f, %.2f, %.2f",
            self._boundary_north,
            self._boundary_east,
            self._boundary_south,
            self._boundary_west,
        )

    def _gridded_altitude_from_lat_lon(
        self, lat: np.ndarray, lon: np.ndarray
    ) -> np.ndarray:
        altitude = self.topography.sel(
            {
                "lat": xr.DataArray(lat, dims="latlon"),
                "lon": xr.DataArray(lon, dims="latlon"),
            },
            method="nearest",
        )

        return altitude.values[0]

    def _is_close(
        self, alt_gridded: np.ndarray, alt_station: np.ndarray
    ) -> npt.NDArray[np.bool_]:
        """
        Function to check if two altitudes are within a relative tolerance of each
        other.

        :param alt_gridded : Gridded altitude (in meters).
        :param alt_station : Observation / station altitude (in meters).

        :returns :
            True if the absolute difference between alt_gridded and alt_station is
            <= self._rdiff
        """
        return np.abs(alt_gridded - alt_station) <= self._rdiff

    def init_kwargs(self):
        return {
            "topo_file": self._topo_file,
            "topo_var": self._topo_var,
            "rdiff": self._rdiff,
        }

    def name(self):
        return "relaltitude"

    def filter_stations(self, stations: dict[str, Station]) -> dict[str, Station]:
        if self.topography is None:
            return stations

        names = np.ndarray(len(stations), dtype=np.dtypes.StrDType)
        lats = np.ndarray(len(stations), dtype=np.float64)
        lons = np.ndarray(len(stations), dtype=np.float64)
        alts = np.ndarray(len(stations), dtype=np.float64)

        for i, name in enumerate(stations):
            station = stations[name]
            names[i] = name
            lats[i] = station["latitude"]
            lons[i] = station["longitude"]
            alts[i] = station["altitude"]

        out_of_bounds_mask = np.logical_or(
            np.logical_or(lons < self._boundary_west, lons > self._boundary_east),
            np.logical_or(lats < self._boundary_south, lats > self._boundary_north),
        )
        if np.sum(out_of_bounds_mask) > 0:
            logger.warning(
                "Some stations were removed due to being out of bounds of the gridded topography"
            )

        topo = self._gridded_altitude_from_lat_lon(lats, lons)

        within_rdiff_mask = self._is_close(topo, alts)

        mask = np.logical_and(~out_of_bounds_mask, within_rdiff_mask)

        selected_names = names[mask]

        return {name: stations[name] for name in selected_names}


@registered_filter
class ValleyFloorRelativeAltitudeFilter(StationFilter):
    """
    Filter for filtering stations based on the difference between the station altitude and valley
    floor altitude (defined as the lowest altitude within a radius around the station). This ensures
    that plateau sites are treated like "surface" sites, while sites in hilly or mountaineous areas
    (eg. Schauinsland) are considered mountain sites. This approach has been used by several papers
    (eg. Fowler et al., Lloibl et al. 1994).

    :param topo: Topography file path (either a file or a directory). Must be a dataset openable by
        xarray, with latitude and longitude stored as "lat" and "lon" respectively. The variable
        that contains elevation data is assumed to be in meters. If `topo` is a directory, a
        metadata.json file containing the geographic bounds of each file must be present (see below
        for example).
    :param radius: Radius (in meters)
    :param topo_var: Variable name to use in topography dataset
    :param lower: Optional lower bound needed for relative altitude for station to be kept (in meters)
    :param upper: Optional upper bound needed for relative altitude for station to be kept (in meters)
    :param keep_nan: Whether to keep values where relative altitude is calculated as nan. Defaults to True.
        Note: Since the topography does not contain values for oceans this may happen for small islands and
        coastal stations.
    :raises ModuleNotFoundError: If necessary required additional dependencies (cf_units, xarray) are
        not available.

    Note
    ----
    This implementation is only tested with GTOPO30 dataset to far.

    Available versions of gtopo30 can be found here:
    `/lustre/storeB/project/aerocom/aerocom1/AEROCOM_OBSDATA/GTOPO30/`

    Note
    ----
    metadata.json should contain a mapping from each nc file, to it's geographic latitude/longitude
    bounds.

    For example:

    ```
    {
        "N.nc": {
            "w": -180,
            "e": 180,
            "n": 90,
            "s": -10
        },
        "S.nc": {
            "w": -180,
            "e": 180,
            "n": -10,
            "s": -90
        }
    }
    ```
    """

    def __init__(
        self,
        topo: str | None = None,
        *,
        radius: float = 5000,
        topo_var: str = "Band1",
        lower: float | None = None,
        upper: float | None = None,
        keep_nan: bool = True,
    ):
        if "cf_units" not in sys.modules:
            logger.info(
                "valleyfloor_relaltitude filter is missing required dependency 'cf-units'. Please install to use this filter."
            )
        if "xarray" not in sys.modules:
            logger.info(
                "valleyfloor_relaltitude filter is missing required dependency 'xarray'. Please install to use this filter."
            )

        self._topo = None
        if topo is not None:
            try:
                self._topo = pathlib.Path(topo)
            except TypeError as e:
                raise TypeError(
                    f"Topo needs to be an instance of str. Got {type(topo)}."
                ) from e

            if not self._topo.exists():
                logger.warning(
                    f"Provided location for topography data ({self._topo}) does not exist. It should be either a .nc file, or a folder with several .nc files and a metadata.json file."
                )

        self._topo_var = topo_var
        self._radius = radius
        self._lower = lower
        self._upper = upper
        self._keep_nan = keep_nan

    @property
    @cache
    def _metadata(self) -> dict:
        if not self._topo.is_dir():
            raise RuntimeError("Should be impossible...")

        metadata_file = self._topo / "metadata.json"
        try:
            with open(metadata_file) as f:
                return json.load(f)
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"No 'metadata.json' file found in directory."
            ) from e

    def init_kwargs(self):
        return {
            # Converting to string for serialization purposes.
            "topo": None if self._topo is None else str(self._topo),
            "topo_var": self._topo_var,
            "radius": self._radius,
            "lower": self._lower,
            "upper": self._upper,
            "keep_nan": self._keep_nan,
        }

    def name(self):
        return "valleyfloor_relaltitude"

    def _get_topo_file_path(self, lat: float, lon: float) -> pathlib.Path:
        """Returns the path of the topofile that needs to be read for the lat / lon pair.

        :param lat: Latitude
        :param lon: Longitude
        :raises FileNotFoundError: If self._topo does not exist.
        :raises FileNotFoundError: If self._topo is a directory and 'metadata.json' does not exist.
        :return: Boolean indicating whether _topo_file changed.
        """
        file_path = None
        if self._topo.is_file():
            file_path = self._topo
        if self._topo.is_dir():
            metadata = self._metadata

            file = None
            for file in metadata:
                if lat < metadata[file]["s"] or lat > metadata[file]["n"]:
                    continue
                if lon < metadata[file]["w"] or lon > metadata[file]["e"]:
                    continue

                file_path = self._topo / file
                break
            else:
                raise FileNotFoundError(
                    f"No matching topography file found for coordinate pair (lat={lat:.6f}; lon={lon:.6f})"
                )

        if file_path is None:
            raise FileNotFoundError

        return file_path

    def _batch_stations(
        self, stations: dict[str, Station]
    ) -> dict[pathlib.Path, dict[str, Station]]:
        """Batches a stations dict according to the topography file that needs to be read in order
        to calculate relative altitude.

        :param stations: Dict mapping of str id to Station (as passed to .filter_stations()).

        :return: A dict mapping the topography file path to a Stations dict.
        """
        result = {}
        for k, v in stations.items():
            topo_file = self._get_topo_file_path(v.latitude, v.longitude)

            if topo_file not in result:
                result[topo_file] = {}

            result[topo_file][k] = v

        return result

    def filter_stations(self, stations: dict[str, Station]) -> dict[str, Station]:
        if self._topo is None or (self._upper is None and self._lower is None):
            # Default initialized filter should not do anything, so return unfiltered stations.
            return stations

        if "cf_units" not in sys.modules:
            raise ModuleNotFoundError(
                "valleyfloor_relaltitude filter is missing required dependency 'cf-units'. Please install to use this filter."
            )
        if "xarray" not in sys.modules:
            raise ModuleNotFoundError(
                "valleyfloor_relaltitude filter is missing required dependency 'xarray'. Please install to use this filter."
            )
        if not self._topo.exists():
            raise FileNotFoundError(
                f"Provided location for topography data ({self._topo}) does not exist. It should be either a .nc file, or a folder with several .nc files and a metadata.json file."
            )

        filtered_stations = {}

        batches = self._batch_stations(stations)
        for topo_file, stations in batches.items():
            topo = xr.load_dataset(topo_file)
            names = np.array([k for k in stations.keys()])
            latitudes = np.array([s.latitude for s in stations.values()])
            longitudes = np.array([s.longitude for s in stations.values()])
            altitudes = np.array([s.altitude for s in stations.values()])
            stats = np.array(list(stations.values()))

            ralt = self._calculate_relative_altitude(
                latitudes,
                longitudes,
                radius=self._radius,
                altitudes=altitudes,
                topo=topo,
            )

            mask = np.ones_like(ralt)
            if self._lower is not None:
                mask = np.logical_and(mask, (ralt >= self._lower))
            if self._upper is not None:
                mask = np.logical_and(mask, (ralt <= self._upper))
            if self._keep_nan:
                mask = np.logical_or(mask, np.isnan(ralt))

            for name, stat in zip(names[mask], stats[mask]):
                filtered_stations[name] = stat

        return filtered_stations

    def _calculate_relative_altitude(
        self,
        lats: np.ndarray,
        lons: np.ndarray,
        *,
        radius: float,
        altitudes: np.ndarray,
        topo: "xr.Dataset",
    ) -> np.ndarray:
        """Calculates relative altitude for multiple latitude-longitude pairs

        :param lats: Array of latitudes
        :param lons: Array of longitudes
        :param radius: Radius for base altitude calculation (in meters)
        :param altitudes: Array of station altitudes (in meters)
        :param topo: Topography dataset

        :return:
            Array of relative altitudes (in meters)
        """
        nptopo = topo[self._topo_var].values
        topolat = topo[self._topo_var]["lat"].values
        topolon = topo[self._topo_var]["lon"].values

        # Indexes of the latitude and longitude of the stations in the topo dataset.
        latidx = np.searchsorted(topolat, lats)
        lonidx = np.searchsorted(topolon, lons)

        relative_altitudes = np.empty_like(lats, dtype=np.float64)

        # Margin for rough slicing of topo data, to avoid expensive distance calculation.
        dist = abs(topolat[1] - topolat[0])
        margin = int(0.1 + (1 / dist) * (radius / 1_000) / 100)

        for i, (lat, lon, altitude) in enumerate(zip(lats, lons, altitudes)):
            # For small radiuses, do a rough slicing of topo dataset to avoid expensive distance
            # calculation for distant points.
            if radius < 100_000:
                lat_slice = slice(latidx[i] - margin, latidx[i] + margin)
                lat_subset = topolat[lat_slice]
                if lat >= 88 or lat <= -88:
                    # Include 360deg longitude near poles
                    subset_topo = nptopo[lat_slice, :]
                else:
                    lon_slice = slice(lonidx[i] - margin, lonidx[i] + margin)
                    subset_topo = nptopo[lat_slice, lon_slice]
                    lon_subset = topolon[lon_slice]
            else:
                subset_topo = nptopo
                lon_subset = topolon

            # Distance calculation for each point.
            coord = np.meshgrid(lon_subset, lat_subset)
            distances = haversine(coord[0], coord[1], lon, lat)

            values_within_radius = subset_topo[distances <= radius]

            min_value = np.nanmin(values_within_radius)

            relative_altitudes[i] = altitude - max(min_value, 0)

        return relative_altitudes
