import numpy as np
import pandas as pd
from .timeseries.Data import Data


def timeseries_data_to_pd(data: Data):
    """Convert pyaro.Data to a pandas dataframe

    :param data: a pyaro Data object
    :return: a pandas dataframe
    """
    size = len(data)
    index = np.arange(size)
    cols = list(data.keys())
    vals = []
    df = pd.DataFrame(index=index, columns=cols)
    for col in cols:
        df[col] = data[col]
    return df
