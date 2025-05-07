import abc
from enum import IntEnum, unique
import numpy as np


@unique
class Flag(IntEnum):
    """Flag of measurement data.

    :param IntEnum: all flags are simple integers
    """

    VALID = 0
    INVALID = 1
    BELOW_THRESHOLD = 2


class Data(abc.ABC):
    """Baseclass for data returned from a pyaro.timeseries.Reader.

    This is the minimum set of columns required for a reader to return.
    A reader is welcome to return a self-implemented subclass of
    Data.

    All Data arrays are accessible as a dict or as property, e.g.
    ```
    td = Data()
    print(td.values)
    print(td["values"])
    ```

    """

    _dtype = [
        ("values", "f"),
        ("stations", "U64"),
        ("latitudes", "f"),
        ("longitudes", "f"),
        ("altitudes", "f"),
        ("start_times", "datetime64[s]"),
        ("end_times", "datetime64[s]"),
        ("flags", "i2"),
        ("standard_deviations", "f"),
    ]

    def __init__(self, variable, units) -> None:
        self._variable = variable
        self._units = units

    def _set_variable(self, variable: str) -> None:
        """Friend method to set the variable name

        This is the setter function for variable. It should only be called by
        friend-classes like VariableNameChanger.

        :param variable: variable-name
        """
        self._variable = variable

    @abc.abstractmethod
    def keys(self):
        """all available data-fields, excluding variable and units which are
        considered metadata"""
        return {}.keys()

    @abc.abstractmethod
    def slice(self, index):  # -> Self: for 3.11
        """Get a copy of this dataset as a slice.

        :param index: A boolean index of the size of data or integer. array
        :return: a new Data object
        """
        pass

    def __getitem__(self, key):
        return self.slice(key)

    @abc.abstractmethod
    def __len__(self) -> int:
        pass

    @property
    def variable(self) -> str:
        """Variable name for all the data

        :return: variable name
        """
        return self._variable

    @property
    def units(self) -> str:
        """Units in CF-notation, the same unit applies to all values

        :return: Units in CF-notation
        """
        return self._units

    @property
    @abc.abstractmethod
    def values(self) -> np.ndarray:
        """A 1-dimensional float array of values.

        :return: 1dim array of floats
        """
        return

    @property
    @abc.abstractmethod
    def stations(self) -> np.ndarray:
        """A 1-dimensional array of station identifiers (strings, usually name)

        :return: 1dim array of strings, max-length 64-chars
        """
        return

    @property
    @abc.abstractmethod
    def latitudes(self) -> np.ndarray:
        """A 1-dimensional array of latitudes (float)

        :return: 1dim array of floats
        """
        return

    @property
    @abc.abstractmethod
    def longitudes(self) -> np.ndarray:
        """A 1-dimensional array of longitudes (float)

        :return: 1dim array of floats
        """
        return

    @property
    @abc.abstractmethod
    def altitudes(self) -> np.ndarray:
        """A 1-dimensional array of altitudes (float)

        :return: 1dim array of floats
        """
        return

    @property
    @abc.abstractmethod
    def start_times(self) -> np.ndarray:
        """A 1-dimensional array of int64 datetimes indicating the start
        of the measurement

        :return: 1dim array of datetime64
        """
        return

    @property
    @abc.abstractmethod
    def end_times(self) -> np.ndarray:
        """A 1-dimensional array of int64 datetimes indicating the end
        of the measurement

        :return: 1dim array of datetime64
        """
        return

    @property
    @abc.abstractmethod
    def flags(self) -> np.ndarray:
        """A 1-dimensional array of flags as defined in pyaro

        :return: 1dim array of ints
        """
        return

    @property
    @abc.abstractmethod
    def standard_deviations(self) -> np.ndarray:
        """A 1-dimensional array of stdevs. NaNs describe
        not available stdev per measurement

        :return: 1dim array of floats
        """
        return


class DynamicRecArrayException(Exception):
    pass


class DynamicRecArray:
    def __init__(self, dtype):
        self.dtype = np.dtype(dtype)
        self.length = 0
        self.capacity = 10
        self._data = np.empty(self.capacity, dtype=self.dtype)

    def __len__(self):
        return self.length

    def keys(self):
        """all available data-fields, excluding variable and units which are
        considered metadata"""
        return self._data.dtype.names

    def append(self, rec):
        if self.length == self.capacity:
            self.capacity += 10 + (self.capacity >> 3)  # 20 + 1.125self.capacity
            self._data = np.resize(self._data, self.capacity)
        self._data[self.length] = rec
        self.length += 1

    def append_array(self, **kwargs):
        for key in self.keys():
            if not key in kwargs:
                raise DynamicRecArrayException(f"missing key {key} in arguments")
            if kwargs[key].shape[0] != kwargs["values"].shape[0]:
                raise DynamicRecArrayException(
                    f"array {key} size ({kwargs['values'].shape[0]}) != values size ({kwargs['values'].shape[0]})"
                )
        add_len = kwargs["values"].shape[0]
        if add_len > 0:
            last_pos = len(self)
            data = np.resize(self.data, last_pos + add_len)
            for key in self.keys():
                data[key][last_pos:] = kwargs[key]
            self.set_data(data)

    def set_data(self, data):
        self.length = len(data)
        self.capacity = len(data)
        self._data = data

    @property
    def data(self):
        if self.capacity != self.length:
            self._data = self._data[:][: self.length]
            self.capacity = len(self._data)
        return self._data


class NpStructuredData(Data):
    """An implementation of Data using numpy Structured Arrays.

    This is the minimum set of columns required for a reader to return.
    A reader is welcome to return a self-implemented subclass of
    Data.

    Data can be added by rows with the append method, or a completed numpy.StructuredArray
    can be submitted using set_data.

    """

    _dtype = [
        ("values", "f"),
        ("stations", "U64"),
        ("latitudes", "f"),
        ("longitudes", "f"),
        ("altitudes", "f"),
        ("start_times", "datetime64[s]"),
        ("end_times", "datetime64[s]"),
        ("flags", "i2"),
        ("standard_deviations", "f"),
    ]

    def __init__(self, variable="", units="") -> None:
        self._variable = variable
        self._units = units
        self._data = DynamicRecArray(self._dtype)

    def __len__(self) -> int:
        """Number of data-points"""
        return len(self._data)

    def __getitem__(self, key):
        """access the data as a dict"""
        return self._data.data[key]

    def keys(self):
        """all available data-fields, excluding variable and units which are
        considered metadata"""
        return self._data.keys()

    def append(
        self,
        value,
        station,
        latitude,
        longitude,
        altitude,
        start_time,
        end_time,
        flag=Flag.VALID,
        standard_deviation=np.nan,
    ):
        """append with a new data-row, or numpy arrays

        :param value
        :param station
        :param latitude
        :param longitude
        :param altitude
        :param start_time
        :param end_time
        :param flag: defaults to Flag.VALID
        :param standard_deviation: defaults to np.nan
        """
        if type(value).__module__ == np.__name__:  # numpy array handling
            self._data.append_array(
                values=value,
                stations=station,
                latitudes=latitude,
                longitudes=longitude,
                altitudes=altitude,
                start_times=start_time,
                end_times=end_time,
                flags=flag,
                standard_deviations=standard_deviation,
            )
            return

        if len(station) > 64:
            raise Exception(f"station name too long, max 64char: {station}")
        #        x = np.array([(value, station, latitude, longitude, altitude, start_time, end_time, flag, standard_deviation)],
        #                    dtype=self._dtype)
        self._data.append(
            (
                value,
                station,
                latitude,
                longitude,
                altitude,
                start_time,
                end_time,
                flag,
                standard_deviation,
            )
        )
        return

    def set_data(self, variable: str, units: str, data: np.array):
        """Initialization code for the data.
        Only known data-fields will be read from data, i.e. it is not
        possible to extend TimeseriesData without subclassing.

        :param variable: variable name
        :param units: variable units
        :param data: a numpy structured array with all fields (see append)
        :raises KeyError: on missing field
        :raises Exception: if not all data-ndarrays have same size
        :raises Exception: if not all data-fields are ndarrays
        """
        for key in self.keys():
            if not key in data.dtype.names:
                raise KeyError(f"{key} not in data: {data.dtype}")
            if not isinstance(data[key], (np.ndarray, np.generic)):
                raise Exception(f"data[{key}] is not a numpy.ndarray")
            if len(data[key]) != len(data["values"]):
                raise Exception(f"values and {key} not of same size")
        self._variable = variable
        self._units = units
        self._data.set_data(data)
        return

    def slice(self, index):
        newData = NpStructuredData()
        newData.set_data(self.variable, self.units, self._data.data[index])
        return newData

    @property
    def variable(self) -> str:
        """Variable name for all the data

        :return: variable name
        """
        return self._variable

    @property
    def units(self) -> str:
        """Units in CF-notation, the same unit applies to all values

        :return: Units in CF-notation
        """
        return self._units

    @property
    def values(self) -> np.ndarray:
        """A 1-dimensional float array of values.

        :return: 1dim array of floats
        """
        return self["values"]

    @property
    def stations(self) -> np.ndarray:
        """A 1-dimensional array of station identifiers (strings, usually name)

        :return: 1dim array of strings, max-length 64-chars
        """
        return self["stations"]

    @property
    def latitudes(self) -> np.ndarray:
        """A 1-dimensional array of latitudes (float)

        :return: 1dim array of floats
        """
        return self["latitudes"]

    @property
    def longitudes(self) -> np.ndarray:
        """A 1-dimensional array of longitudes (float)

        :return: 1dim array of floats
        """
        return self["longitudes"]

    @property
    def altitudes(self) -> np.ndarray:
        """A 1-dimensional array of altitudes (float)

        :return: 1dim array of floats
        """
        return self["altitudes"]

    @property
    def start_times(self) -> np.ndarray:
        """A 1-dimensional array of int64 datetimes indicating the start
        of the measurement

        :return: 1dim array of datetime64
        """
        return self["start_times"]

    @property
    def end_times(self) -> np.ndarray:
        """A 1-dimensional array of int64 datetimes indicating the end
        of the measurement

        :return: 1dim array of datetime64
        """
        return self["end_times"]

    @property
    def flags(self) -> np.ndarray:
        """A 1-dimensional array of flags as defined in pyaro

        :return: 1dim array of ints
        """
        return self["flags"]

    @property
    def standard_deviations(self) -> np.ndarray:
        """A 1-dimensional array of stdevs. NaNs describe
        not available stdev per measurement

        :return: 1dim array of floats
        """
        return self["standard_deviations"]

    def __str__(self):
        return f"{self.variable}, {self.units}, {self._data.data}"


if __name__ == "__main__":
    # code for micro-benchmarking
    import timeit

    def append_data():
        da = NpStructuredData("var", "km")
        for i in range(100000):
            value = 0.3
            station = "123"
            lat = 3.2
            lon = 4.3
            alt = 100
            start = np.datetime64("1997-01-01 00:00:00")
            end = np.datetime64("1997-01-01 00:00:00")
            da.append(value, station, lat, lon, alt, start, end, Flag.VALID, np.nan)

    number = 3
    print(timeit.timeit("append_data()", globals=globals(), number=number) / number)
