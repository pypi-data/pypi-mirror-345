import json
import unittest

from pyaro.timeseries.Station import Station


class TestStations(unittest.TestCase):
    sdict = {
        "station": "stat1",
        "longitude": 10,
        "latitude": 60.0,
        "altitude": 140.3,
        "long_name": "Blindern",
        "country": "NO",
        "url": "https://met.no",
    }
    mdict = {
        "metadata": "mymetadata",
        "revision": "2024-06-08",
    }

    def test_init1(self):
        station = Station(self.sdict)
        self.assertDictEqual(station._fields, self.sdict)

    def test_init2(self):
        station = Station(self.sdict, self.mdict)
        self.assertDictEqual(station._fields, self.sdict)
        self.assertDictEqual(station.metadata, self.mdict)

    def test_init3(self):
        station = Station(self.sdict, self.mdict)
        station2 = Station(**station.init_kwargs())
        self.assertDictEqual(station._fields, station2._fields)
        self.assertDictEqual(station.metadata, station2.metadata)
