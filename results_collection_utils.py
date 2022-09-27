from dataclasses import dataclass, fields
import datetime
import numpy as np


@dataclass
class HSResultsData:
    ticker: str
    starting_balance: float
    final_balance_long: float
    final_balance_short: float
    pnl: float
    pnl_long: float
    pnl_short: float
    loss_long: float
    loss_short: float
    results_file: str
    config_file: str
    config_long: dict
    config_short: dict
    result_data: dict
    config_data: dict
    run_conditions: dict


@dataclass
class BacktestResultsData:
    ticker: str
    test_run_dt: str
    pnl: float
    result_data: dict


def round_dict_values(d, round_to=4):
    for k in d:
        val = d[k]
        if isinstance(val, float):
            d[k] = round(val, round_to)
        if isinstance(val, dict):
            round_dict_values(val, round_to)


def round_dc_values(dc, round_to=4):
    for field in fields(dc):
        value = getattr(dc, field.name)
        if isinstance(value, float):
            setattr(dc, field.name, round(value, round_to))
        if isinstance(value, str) and "\\" in value:
            setattr(dc, field.name, value[value.rindex("\\") + 1:])
        if isinstance(value, dict):
            round_dict_values(value, round_to)


def append_result(results_sorted, pnl, result, round_to=4):
    round_dc_values(result, round_to)
    while pnl in results_sorted:
        pnl += 1e-6
    results_sorted[pnl] = result


def format_columns(columns, col_sizes=None):
    if col_sizes is None:
        col_sizes = {}
    fmt = "|"
    idx = 0
    for col in columns:
        if col in col_sizes:
            col_size = col_sizes[col]
        else:
            col_size = 28 if "FILE" in col else 10
        col_name_len = len(col)
        col_size = col_name_len if col_size < col_name_len else col_size
        fmt += "{" + str(idx) + ":" + str(col_size) + "}|"
        idx += 1
    return fmt


def ts_to_date(timestamp: float) -> datetime.datetime:
    if timestamp > 253402297199:
        return datetime.datetime.fromtimestamp(timestamp / 1000)
    return datetime.datetime.fromtimestamp(timestamp)


def ts_to_date_str(timestamp: float) -> str:
    return str(ts_to_date(timestamp)).replace(" ", "T")


def join_ticks_data(np_array_1, np_array_2):
    concatenated = np.concatenate([np_array_1, np_array_2], axis=0)
    return np.unique(concatenated, axis=0)


def join_ticks_data_v2(arr1: np.ndarray, arr2: np.ndarray):
    if not len(arr1):
        return arr2
    if not len(arr2):
        return arr1

    s1 = int(arr1[0, 0])
    e1 = int(arr1[-1, 0])
    s2 = int(arr2[0, 0])
    e2 = int(arr2[-1, 0])

    if s1 <= s2:
        if s2 == s1 and e2 > e1:
            # we can return arr2 here since it should contain all data from arr1 already, but we could also
            # go through arr2 searching for missing data that might be presented in arr1 (TODO?)
            print(f"1. join_ticks_data_v2, returning arr2")
            return arr2
        if e1 >= e2:
            # we can return arr1 here since it should contain all data from arr2 already, but we could also
            # go through arr1 searching for missing data that might be presented in arr2 (TODO?)
            print(f"2. join_ticks_data_v2, returning arr1")
            return arr1
        # s1 < s2, e1 < e2:
        m = int((s2 - e1) / 1000)
        print(f"3. join_ticks_data_v2, m: {m}")
        if m >= 1:
            print(f"4. join_ticks_data_v2, m >= 1, concatenating arr1 with arr2")
            return np.concatenate([arr1, arr2], axis=0)
        if m == 0:
            arr1 = np.delete(arr1, -1, 0)
            print(f"5. join_ticks_data_v2, !!!m == 0!!! concatenating arr1[0:-1] with arr2")
            return np.concatenate([arr1, arr2], axis=0)
        # m < 0
        arr2 = np.delete(arr2, range(0, -m + 1), 0)
        print(f"6. join_ticks_data_v2, m < 0, concatenating arr1 with arr2[m:]")
        return np.concatenate([arr1, arr2], axis=0)

    # s1 > s2:
    if e2 >= e1:
        # we can return arr2 here since it should contain all data from arr1 already, but we could also
        # go through arr2 searching for missing data that might be presented in arr1 (TODO?)
        print(f"7. join_ticks_data_v2, returning arr2")
        return arr2
    # s1 > s2, e1 > e2
    m = int((s1 - e2) / 1000)
    print(f"8. join_ticks_data_v2, m: {m}")
    if m >= 1:
        print(f"9. join_ticks_data_v2, m >= 1, concatenating arr2 with arr1")
        return np.concatenate([arr2, arr1], axis=0)
    if m == 0:
        arr2 = np.delete(arr2, -1, 0)
        print(f"10. join_ticks_data_v2, !!!m == 0!!! concatenating arr2[0:-1] with arr2")
        return np.concatenate([arr2, arr1], axis=0)
    # m < 0
    arr1 = np.delete(arr1, range(0, -m + 1), 0)
    print(f"11. join_ticks_data_v2, m < 0, concatenating arr2 with arr1[m:]")
    return np.concatenate([arr2, arr1], axis=0)
