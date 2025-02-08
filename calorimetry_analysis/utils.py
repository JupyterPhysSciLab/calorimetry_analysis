import pandas

def find_pandas_dataframe_names():
    """
    This operation will search the interactive name space for pandas
    DataFrame objects. It will not find DataFrames that are children
    of objects in the interactive namespace. You will need to provide
    your own operation for finding those.

    :return list: string names for objects in the global interactive
    namespace that are pandas DataFrames.
    """
    from pandas import DataFrame as df
    from IPython import get_ipython

    dataframenames = []
    global_dict = get_ipython().user_ns
    for k in global_dict:
        if not (str.startswith(k, '_')) and isinstance(global_dict[k], df):
            dataframenames.append(k)
    return dataframenames


def parr6772_time_series_to_elapsed_time(times: pandas.Series) -> pandas.Series:
    from pandas import Series

    def parse_time(date_str):
        from datetime import datetime
        date = datetime.strptime(date_str, '%m/%d/%y %H:%M:%S')
        timestamp = date.timestamp()
        return timestamp

    time_list = []
    start_time = parse_time(str(times[0]))
    for k in times:
        time_list.append(parse_time(str(k)) - start_time)
    return Series(time_list)

def load_parr6772(datalog)-> pandas.DataFrame:
    """Reads a Parr 6772 thermometer Datalog.csv file and returns a
    pandas.DataFrame containing the columns "date", "Temp(C)" and "Time(s)",
    where the last column is the elapsed time since the first datapoint in
    the file.

    :param datalog: String containing the datalog file name or path.
    """
    from pandas import read_csv

    df = read_csv(datalog, header=None, usecols=[0,1], names = ["date",
                                                                "Temp(C)"])
    df["Time(s)"] = parr6772_time_series_to_elapsed_time(df["date"])
    return df