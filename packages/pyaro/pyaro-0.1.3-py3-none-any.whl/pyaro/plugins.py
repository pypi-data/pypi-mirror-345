import functools
import sys
import warnings

if sys.version_info >= (3, 10):
    from importlib.metadata import EntryPoints, entry_points
else:
    from importlib_metadata import EntryPoints, entry_points

from .timeseries.Engine import Engine as TimeseriesEngine
from .timeseries.Reader import Reader as TimeseriesReader


def build_timeseries_engines(entrypoints: EntryPoints) -> dict[str, TimeseriesEngine]:
    backend_entrypoints: dict[str, TimeseriesEngine] = {}
    for entrypoint in entrypoints:
        name = entrypoint.name
        if name in backend_entrypoints:
            warnings.warn(
                f"found multiple versions of {entrypoint.group} entrypoint {name} for {entrypoint.value}"
            )
            continue
        try:
            backend = entrypoint.load()
            backend_entrypoints[name] = backend()
        except Exception as ex:
            warnings.warn(f"Engine {name!r} loading failed:\n{ex}", RuntimeWarning)
    return backend_entrypoints


@functools.lru_cache(maxsize=1)
def list_timeseries_engines() -> dict[str, TimeseriesEngine]:
    """
    Return a dictionary of available timeseries_readers and their objects.

    Returns
    -------
    dictionary

    Notes
    -----
    This function lives in the backends namespace (``engs=pyaro.list_timeseries_engines()``).
    More information about each reader is available via the TimeseriesEngine obj.url() and
    obj.description()

    # New selection mechanism introduced with Python 3.10. See GH6514.
    """
    entrypoints = entry_points(group="pyaro.timeseries")
    return build_timeseries_engines(entrypoints)


def open_timeseries(name, *args, **kwargs) -> TimeseriesReader:
    """open a timeseries reader directly, sending args and kwargs
    directly to the TimeseriesReader.open_reader() function

    :param name: the name of the entrypoint as key in list_timeseries_readers
    :return: an implementation-object of a TimeseriesReader opened to a location
    """
    engine = list_timeseries_engines()[name]

    return engine.open(*args, **kwargs)
