import datetime
import logging
import sys
import unittest
import os

import numpy as np

import pyaro
import pyaro.timeseries
from pyaro.timeseries.Filter import FilterException
from pyaro.timeseries.Wrappers import VariableNameChangingReader

try:
    import pandas

    has_pandas = True
except ImportError:
    has_pandas = False

try:
    import geocoder_reverse_natural_earth

    has_geocode = True
except ImportError:
    has_geocode = False


class TestCSVTimeSeriesReader(unittest.TestCase):
    file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "testdata",
        "datadir",
        "csvReader_testdata.csv",
    )
    file_with_header = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "testdata",
        "datadir",
        "csvReader_testdata.csv.with_header",
    )
    elevation_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "testdata",
        "datadir_elevation",
        "csvReader_testdata_elevation.csv",
    )
    multifile = "glob:" + os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "testdata", "datadir", "**/*.csv"
    )
    multifile_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "testdata", "datadir"
    )

    def setUp(self):
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)
        pass

    def test_init(self):
        engine = pyaro.list_timeseries_engines()["csv_timeseries"]
        self.assertEqual(engine.url(), "https://github.com/metno/pyaro")
        # just see that it doesn't fails
        engine.description()
        engine.args()
        with engine.open(self.file, filters=[]) as ts:
            count = 0
            for var in ts.variables():
                count += len(ts.data(var))
            self.assertEqual(count, 208)
            self.assertEqual(len(ts.stations()), 2)

    def test_init_multifile(self):
        engine = pyaro.list_timeseries_engines()["csv_timeseries"]
        self.assertEqual(engine.url(), "https://github.com/metno/pyaro")
        # just see that it doesn't fails
        engine.description()
        engine.args()
        with engine.open(self.multifile, filters=[]) as ts:
            count = 0
            for var in ts.variables():
                count += len(ts.data(var))
            self.assertEqual(count, 426)
            self.assertEqual(len(ts.stations()), 2)

    def test_init_directory(self):
        engine = pyaro.list_timeseries_engines()["csv_timeseries"]
        self.assertEqual(engine.url(), "https://github.com/metno/pyaro")
        # just see that it doesn't fails
        engine.description()
        engine.args()
        with engine.open(self.multifile_dir, filters=[]) as ts:
            count = 0
            for var in ts.variables():
                count += len(ts.data(var))
            self.assertEqual(count, 218)
            self.assertEqual(len(ts.stations()), 2)

    def test_init2(self):
        with pyaro.open_timeseries(
            "csv_timeseries", *[self.file], **{"filters": []}
        ) as ts:
            count = 0
            for var in ts.variables():
                count += len(ts.data(var))
            self.assertEqual(count, 208)
            self.assertEqual(len(ts.stations()), 2)

    def test_init_extra_columns(self):
        columns = {
            "variable": 0,
            "station": 1,
            "longitude": 2,
            "latitude": 3,
            "value": 4,
            "units": 5,
            "start_time": 6,
            "end_time": 7,
            "altitude": "0",
            "country": "NO",
            "standard_deviation": "NaN",
            "flag": "0",
            "area_classification": 8,
        }
        with pyaro.open_timeseries(
            "csv_timeseries", *[self.file], **{"filters": [], "columns": columns}
        ) as ts:
            areas = ["Rural", "Urban"]
            stations = ts.stations()
            self.assertEqual(stations["station1"]["area_classification"], areas[0])
            self.assertEqual(stations["station2"]["area_classification"], areas[1])

    def test_metadata(self):
        with pyaro.open_timeseries(
            "csv_timeseries", *[self.file], **{"filters": []}
        ) as ts:
            self.assertIsInstance(ts.metadata(), dict)
            self.assertIn("path", ts.metadata())

    def test_data(self):
        engines = pyaro.list_timeseries_engines()
        with engines["csv_timeseries"].open(
            filename=self.file,
            filters=[pyaro.timeseries.filters.get("countries", include=["NO"])],
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
        self.assertTrue(True)

    def test_append_data(self):
        engines = pyaro.list_timeseries_engines()
        with engines["csv_timeseries"].open(
            filename=self.file,
            filters={"countries": {"include": ["NO"]}},
        ) as ts:
            var = next(iter(ts.variables()))
            data = ts.data(var)
            old_size = len(data)
            rounds = 3
            for _ in range(rounds):
                data.append(
                    value=data.values,
                    station=data.stations,
                    start_time=data.start_times,
                    end_time=data.end_times,
                    latitude=data.latitudes,
                    longitude=data.longitudes,
                    altitude=data.altitudes,
                    flag=data.flags,
                    standard_deviation=data.standard_deviations,
                )
            self.assertEqual(
                (2 ** rounds) * old_size, len(data), "data append by array"
            )

    def test_stationfilter(self):
        engine = pyaro.list_timeseries_engines()["csv_timeseries"]
        sfilter = pyaro.timeseries.filters.get("stations", exclude=["station1"])
        with engine.open(self.file, filters=[sfilter]) as ts:
            count = 0
            for var in ts.variables():
                count += len(ts.data(var))
            self.assertEqual(count, 104)
            self.assertEqual(len(ts.stations()), 1)

    def test_boundingboxfilter_exception(self):
        with self.assertRaises(pyaro.timeseries.Filter.BoundingBoxException):
            pyaro.timeseries.filters.get("bounding_boxes", include=[(-90, 0, 90, 180)])

    def test_boundingboxfilter(self):
        engine = pyaro.list_timeseries_engines()["csv_timeseries"]
        sfilter = pyaro.timeseries.filters.get(
            "bounding_boxes", include=[(90, 180, -90, 0)]
        )
        self.assertEqual(sfilter.init_kwargs()["include"][0][3], 0)
        with engine.open(self.file, filters=[sfilter]) as ts:
            count = 0
            for var in ts.variables():
                count += len(ts.data(var))
            self.assertEqual(len(ts.stations()), 1)
            self.assertEqual(count, 104)
        sfilter = pyaro.timeseries.filters.get(
            "bounding_boxes", exclude=[(90, 0, -90, -180)]
        )
        self.assertEqual(sfilter.init_kwargs()["exclude"][0][3], -180)
        with engine.open(self.file, filters=[sfilter]) as ts:
            count = 0
            for var in ts.variables():
                count += len(ts.data(var))
            self.assertEqual(len(ts.stations()), 1)
            self.assertEqual(count, 104)

    def test_timebounds_exception(self):
        with self.assertRaises(pyaro.timeseries.Filter.TimeBoundsException):
            pyaro.timeseries.filters.get(
                "time_bounds",
                start_include=[("1903-01-01 00:00:00", "1901-12-31 23:59:59")],
            )

    def test_timebounds(self):
        engine = pyaro.list_timeseries_engines()["csv_timeseries"]
        tfilter = pyaro.timeseries.filters.get(
            "time_bounds",
            startend_include=[("1997-01-01 00:00:00", "1997-02-01 00:00:00")],
            end_exclude=[("1997-01-05 00:00:00", "1997-01-07 00:00:00")],
        )
        self.assertEqual(
            tfilter.init_kwargs()["startend_include"][0][1], "1997-02-01 00:00:00"
        )
        (dt1, dt2) = tfilter.envelope()
        self.assertIsInstance(dt1, datetime.datetime)
        self.assertIsInstance(dt2, datetime.datetime)
        with engine.open(self.file, filters=[tfilter]) as ts:
            count = 0
            for var in ts.variables():
                count += len(ts.data(var))
            self.assertEqual(len(ts.stations()), 2)
            self.assertEqual(count, 112)

    def test_flagfilter(self):
        engine = pyaro.list_timeseries_engines()["csv_timeseries"]
        ffilter = pyaro.timeseries.filters.get(
            "flags",
            include=[
                pyaro.timeseries.Flag.VALID,
                pyaro.timeseries.Flag.BELOW_THRESHOLD,
            ],
        )
        self.assertEqual(
            ffilter.init_kwargs()["include"][0], pyaro.timeseries.Flag.VALID
        )
        with engine.open(self.file, filters=[ffilter]) as ts:
            count = 0
            for var in ts.variables():
                count += len(ts.data(var))
            self.assertEqual(len(ts.stations()), 2)
            self.assertEqual(count, 208)

        ffilter = pyaro.timeseries.filters.get(
            "flags", include=[pyaro.timeseries.Flag.INVALID]
        )
        with engine.open(self.file, filters=[ffilter]) as ts:
            count = 0
            for var in ts.variables():
                count += len(ts.data(var))
            self.assertEqual(len(ts.stations()), 2)
            self.assertEqual(count, 0)

    def test_variable_time_station_filter(self):
        vtsfilter = pyaro.timeseries.filters.get(
            "time_variable_station",
            exclude=[
                # excluding 2 days each
                ("1997-01-11 00:00:00", "1997-01-12 23:59:59", "SOx", "station2"),
                ("1997-01-13 00:00:00", "1997-01-14 23:59:59", "NOx", "station1"),
            ],
        )
        self.assertEqual(
            vtsfilter.init_kwargs()["exclude"][0][0], "1997-01-11 00:00:00"
        )
        engine = pyaro.list_timeseries_engines()["csv_timeseries"]
        with engine.open(self.file, filters=[vtsfilter]) as ts:
            count = 0
            for var in ts.variables():
                count += len(ts.data(var))
            self.assertEqual(len(ts.stations()), 2)
            self.assertEqual(count, 204)

    def test_variable_time_station_filter_csv(self):
        csvfile = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "testdata",
            "timeVariableStationFilter_exclude.csv",
        )

        vtsfilter = pyaro.timeseries.filters.get(
            "time_variable_station",
            exclude_from_csvfile=csvfile,
        )
        print(vtsfilter)
        self.assertEqual(
            vtsfilter.init_kwargs()["exclude"][0][0], "1997-01-11 00:00:00"
        )
        engine = pyaro.list_timeseries_engines()["csv_timeseries"]
        with engine.open(self.file, filters=[vtsfilter]) as ts:
            count = 0
            for var in ts.variables():
                count += len(ts.data(var))
            self.assertEqual(len(ts.stations()), 2)
            self.assertEqual(count, 204)

    def test_wrappers(self):
        engine = pyaro.list_timeseries_engines()["csv_timeseries"]
        newsox = "oxidised_sulphur"
        with VariableNameChangingReader(
            engine.open(self.file, filters=[]), {"SOx": newsox}
        ) as ts:
            self.assertEqual(ts.data(newsox).variable, newsox)
            self.assertGreater(len(ts.metadata()), 0)
        pass

    def test_variables_filter(self):
        engine = pyaro.list_timeseries_engines()["csv_timeseries"]
        newsox = "oxidised_sulphur"
        vfilter = pyaro.timeseries.filters.get(
            "variables", reader_to_new={"SOx": newsox}
        )
        with engine.open(self.file, filters=[vfilter]) as ts:
            self.assertEqual(ts.data(newsox).variable, newsox)
        pass

    def test_duplicate_filter(self):
        engine = pyaro.list_timeseries_engines()["csv_timeseries"]
        with engine.open(
            self.multifile_dir + "/csvReader_testdata2.csv",
            filters={"duplicates": {"duplicate_keys": None}},
        ) as ts:
            self.assertEqual(len(ts.data("NOx")), 8)
        with engine.open(
            self.multifile_dir + "/csvReader_testdata2.csv",
            filters={
                "duplicates": {"duplicate_keys": ["stations", "start_times", "values"]}
            },
        ) as ts:
            self.assertEqual(len(ts.data("NOx")), 10)

    def test_time_resolution_filter(self):
        engine = pyaro.list_timeseries_engines()["csv_timeseries"]
        with self.assertRaises(FilterException):
            with engine.open(
                self.file,
                filters={"time_resolution": {"resolutions": ["ldjf4098"]}},
            ) as ts:
                pass
        with engine.open(
            self.file,
            filters={"time_resolution": {"resolutions": ["1 day"]}},
        ) as ts:
            count = 0
            for var in ts.variables():
                count += len(ts.data(var))
            self.assertEqual(count, 208)
        for resolution in "1 minute, 1 hour, 1week, 1month, 3year".split(","):
            with engine.open(
                self.file,
                filters={"time_resolution": {"resolutions": ["1 hour"]}},
            ) as ts:
                count = 0
                for var in ts.variables():
                    count += len(ts.data(var))
                self.assertEqual(count, 0)

    def test_filterFactory(self):
        filters = pyaro.timeseries.filters.list()
        print(filters["variables"])
        self.assertTrue(True)

    def test_filterCollection(self):
        with pyaro.open_timeseries(
            "csv_timeseries",
            filename=self.file,
        ) as ts:
            filters = pyaro.timeseries.FilterCollection(
                {
                    "countries": {"include": ["NO"]},
                    "stations": {"include": ["station1"]},
                }
            )
            data1 = ts.data("SOx")
            data2 = filters.filter(ts, "SOx")
            self.assertEqual(len(data1), 2 * len(data2))

    @unittest.skipUnless(has_pandas, "no pandas installed")
    def test_timeseries_data_to_pd(self):
        with pyaro.open_timeseries(
            "csv_timeseries", *[self.file], **{"filters": []}
        ) as ts:
            count = 0
            vars = list(ts.variables())
            data = ts.data(vars[0])
            df = pyaro.timeseries_data_to_pd(data)
            self.assertEqual(len(df), len(data))
            self.assertEqual(len(df["values"]), len(data["values"]))
            self.assertEqual(df["values"][3], data["values"][3])

    @unittest.skipUnless(has_geocode, "geocode-reverse-natural-earth not available")
    def test_country_lookup(self):
        with pyaro.open_timeseries(
            "csv_timeseries", *[self.file], **{"filters": [], "country_lookup": True}
        ) as ts:
            count = 0
            vars = list(ts.variables())
            data = ts.data(vars[0])
        self.assertTrue(False)

    def test_altitude_filter_1(self):
        engines = pyaro.list_timeseries_engines()
        with engines["csv_timeseries"].open(
            filename=self.elevation_file,
            filters=[pyaro.timeseries.filters.get("altitude", max_altitude=150)],
            columns={
                "variable": 0,
                "station": 1,
                "longitude": 2,
                "latitude": 3,
                "value": 4,
                "units": 5,
                "start_time": 6,
                "end_time": 7,
                "altitude": 9,
                "country": "NO",
                "standard_deviation": "NaN",
                "flag": "0",
            },
        ) as ts:
            self.assertEqual(len(ts.stations()), 1)

    def test_altitude_filter_2(self):
        engines = pyaro.list_timeseries_engines()
        with engines["csv_timeseries"].open(
            filename=self.elevation_file,
            filters=[pyaro.timeseries.filters.get("altitude", min_altitude=250)],
            columns={
                "variable": 0,
                "station": 1,
                "longitude": 2,
                "latitude": 3,
                "value": 4,
                "units": 5,
                "start_time": 6,
                "end_time": 7,
                "altitude": 9,
                "country": "NO",
                "standard_deviation": "NaN",
                "flag": "0",
            },
        ) as ts:
            self.assertEqual(len(ts.stations()), 1)

    def test_altitude_filter_3(self):
        engines = pyaro.list_timeseries_engines()
        with engines["csv_timeseries"].open(
            filename=self.elevation_file,
            filters=[
                pyaro.timeseries.filters.get(
                    "altitude", min_altitude=150, max_altitude=250
                )
            ],
            columns={
                "variable": 0,
                "station": 1,
                "longitude": 2,
                "latitude": 3,
                "value": 4,
                "units": 5,
                "start_time": 6,
                "end_time": 7,
                "altitude": 9,
                "country": "NO",
                "standard_deviation": "NaN",
                "flag": "0",
            },
        ) as ts:
            self.assertEqual(len(ts.stations()), 1)

    def test_relaltitude_filter_emep_1(self):
        engines = pyaro.list_timeseries_engines()
        with engines["csv_timeseries"].open(
            filename=self.elevation_file,
            filters=[
                pyaro.timeseries.filters.get(
                    "relaltitude",
                    topo_file="./tests/testdata/datadir_elevation/topography.nc",
                    rdiff=0,
                )
            ],
            columns={
                "variable": 0,
                "station": 1,
                "longitude": 2,
                "latitude": 3,
                "value": 4,
                "units": 5,
                "start_time": 6,
                "end_time": 7,
                "altitude": 9,
                "country": "NO",
                "standard_deviation": "NaN",
                "flag": "0",
            },
        ) as ts:
            # Altitudes in test dataset:
            # Station     | Alt_obs   | Modeobs | rdiff |
            # Station 1   | 100       | 12.2554 |  87.7446 |
            # Station 2   | 200       |  4.9016 | 195.0984 |
            # Station 3   | 300       |  4.9016 | 195.0984 |
            # Since rtol = 0, no station should be included.
            self.assertEqual(len(ts.stations()), 0)

    def test_relaltitude_filter_emep_2(self):
        engines = pyaro.list_timeseries_engines()
        with engines["csv_timeseries"].open(
            filename=self.elevation_file,
            filters=[
                pyaro.timeseries.filters.get(
                    "relaltitude",
                    topo_file="./tests/testdata/datadir_elevation/topography.nc",
                    rdiff=90,
                )
            ],
            columns={
                "variable": 0,
                "station": 1,
                "longitude": 2,
                "latitude": 3,
                "value": 4,
                "units": 5,
                "start_time": 6,
                "end_time": 7,
                "altitude": 9,
                "country": "NO",
                "standard_deviation": "NaN",
                "flag": "0",
            },
        ) as ts:
            # At rdiff = 90, only the first station should be included.
            self.assertEqual(len(ts.stations()), 1)

    def test_relaltitude_filter_emep_3(self):
        engines = pyaro.list_timeseries_engines()
        with engines["csv_timeseries"].open(
            filename=self.elevation_file,
            filters=[
                pyaro.timeseries.filters.get(
                    "relaltitude",
                    topo_file="./tests/testdata/datadir_elevation/topography.nc",
                    rdiff=300,
                )
            ],
            columns={
                "variable": 0,
                "station": 1,
                "longitude": 2,
                "latitude": 3,
                "value": 4,
                "units": 5,
                "start_time": 6,
                "end_time": 7,
                "altitude": 9,
                "country": "NO",
                "standard_deviation": "NaN",
                "flag": "0",
            },
        ) as ts:
            # Since rdiff=300, all stations should be included.
            self.assertEqual(len(ts.stations()), 3)

    def test_relaltitude_filter_1(self):
        engines = pyaro.list_timeseries_engines()
        with engines["csv_timeseries"].open(
            filename=self.elevation_file,
            filters=[
                pyaro.timeseries.filters.get(
                    "relaltitude",
                    topo_file="./tests/testdata/datadir_elevation/topography.nc",
                    rdiff=0,
                )
            ],
            columns={
                "variable": 0,
                "station": 1,
                "longitude": 2,
                "latitude": 3,
                "value": 4,
                "units": 5,
                "start_time": 6,
                "end_time": 7,
                "altitude": 9,
                "country": "NO",
                "standard_deviation": "NaN",
                "flag": "0",
            },
        ) as ts:
            self.assertEqual(len(ts.stations()), 0)

    def test_relaltitude_filter_2(self):
        engines = pyaro.list_timeseries_engines()
        with engines["csv_timeseries"].open(
            filename=self.elevation_file,
            filters=[
                pyaro.timeseries.filters.get(
                    "relaltitude",
                    topo_file="./tests/testdata/datadir_elevation/topography.nc",
                    rdiff=90,
                )
            ],
            columns={
                "variable": 0,
                "station": 1,
                "longitude": 2,
                "latitude": 3,
                "value": 4,
                "units": 5,
                "start_time": 6,
                "end_time": 7,
                "altitude": 9,
                "country": "NO",
                "standard_deviation": "NaN",
                "flag": "0",
            },
        ) as ts:
            # At rdiff = 90, only the first station should be included.
            self.assertEqual(len(ts.stations()), 1)

    def test_relaltitude_filter_3(self):
        engines = pyaro.list_timeseries_engines()
        with engines["csv_timeseries"].open(
            filename=self.elevation_file,
            filters=[
                pyaro.timeseries.filters.get(
                    "relaltitude",
                    topo_file="./tests/testdata/datadir_elevation/topography.nc",
                    rdiff=300,
                )
            ],
            columns={
                "variable": 0,
                "station": 1,
                "longitude": 2,
                "latitude": 3,
                "value": 4,
                "units": 5,
                "start_time": 6,
                "end_time": 7,
                "altitude": 9,
                "country": "NO",
                "standard_deviation": "NaN",
                "flag": "0",
            },
        ) as ts:
            # Since rdiff=300, all stations should be included.
            self.assertEqual(len(ts.stations()), 3)

    def test_valley_floor_filter(self):
        engines = pyaro.list_timeseries_engines()
        with engines["csv_timeseries"].open(
            filename=self.elevation_file,
            filters=[
                pyaro.timeseries.filters.get(
                    "valleyfloor_relaltitude",
                    topo="tests/testdata/datadir_elevation/gtopo30_subset.nc",
                    radius=5000,
                    lower=150,
                    upper=250,
                )
            ],
            columns={
                "variable": 0,
                "station": 1,
                "longitude": 2,
                "latitude": 3,
                "value": 4,
                "units": 5,
                "start_time": 6,
                "end_time": 7,
                "altitude": 9,
                "country": "NO",
                "standard_deviation": "NaN",
                "flag": "0",
            },
        ) as ts:
            self.assertEqual(len(ts.stations()), 3)

    def test_reading_with_header(self):
        engines = pyaro.list_timeseries_engines()
        with engines["csv_timeseries"].open(
            filename=self.file,
            columns={
                "variable": 0,
                "station": 1,
                "longitude": 2,
                "latitude": 3,
                "value": 4,
                "units": 5,
                "start_time": 6,
                "end_time": 7,
                "altitude": "NaN",
                "country": "NO",
                "standard_deviation": "NaN",
                "flag": "0",
            },
        ) as ts0, engines["csv_timeseries"].open(
            filename=self.file_with_header,
            columns={
                "variable": 0,
                "station": 1,
                "longitude": 2,
                "latitude": 3,
                "value": 4,
                "units": 5,
                "start_time": 6,
                "end_time": 7,
                "altitude": "NaN",
                "country": "NO",
                "standard_deviation": "NaN",
                "flag": "0",
            },
            skip_header_rows=1,
        ) as ts1:
            self.assertTrue(np.all(ts0.data("NOx").values == ts1.data("NOx").values))

    def test_valley_floor_filter_multi_use(self):
        engines = pyaro.list_timeseries_engines()
        filter = pyaro.timeseries.filters.get(
                    "valleyfloor_relaltitude",
                    topo="tests/testdata/datadir_elevation/gtopo30_subset.nc",
                    radius=5000,
                    lower=150,
                    upper=250,
                )
        with engines["csv_timeseries"].open(
            filename=self.elevation_file,
            filters=[filter],
            columns={
                "variable": 0,
                "station": 1,
                "longitude": 2,
                "latitude": 3,
                "value": 4,
                "units": 5,
                "start_time": 6,
                "end_time": 7,
                "altitude": 9,
                "country": "NO",
                "standard_deviation": "NaN",
                "flag": "0",
            },
        ) as ts:
            self.assertEqual(len(ts.stations()), 3)

        with engines["csv_timeseries"].open(
            filename=self.elevation_file,
            filters=[filter],
            columns={
                "variable": 0,
                "station": 1,
                "longitude": 2,
                "latitude": 3,
                "value": 4,
                "units": 5,
                "start_time": 6,
                "end_time": 7,
                "altitude": 9,
                "country": "NO",
                "standard_deviation": "NaN",
                "flag": "0",
            },
        ) as ts:
            self.assertEqual(len(ts.stations()), 3)

if __name__ == "__main__":
    unittest.main()
