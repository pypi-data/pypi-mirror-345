from importlib import metadata

__version__ = metadata.version(__package__)

from .plugins import list_timeseries_engines, open_timeseries

try:
    from .pandas_helpers import timeseries_data_to_pd
except:
    pass
