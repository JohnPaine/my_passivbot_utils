import os
import glob
import json

import numpy as np
from sortedcontainers import SortedDict
from results_collection_utils import ts_to_date, ts_to_date_str, join_ticks_data_v2


def validate_ticks_data(summary_ticks_data, root):
    if summary_ticks_data is None:
        print(f"\nNot managed to validate ticks data for {root}\n\n")
        return False

    errors = 0
    first_ts = int(summary_ticks_data[0, 0] / 1000)
    last_ts = int(summary_ticks_data[-1, 0] / 1000)
    ts_range = last_ts - first_ts + 1

    print(f"\n\tValidating summary_ticks_data from {first_ts} to {last_ts}...\n")

    rows_data = summary_ticks_data[:, 0]
    std_size = np.size(summary_ticks_data, axis=0)
    std_size2 = len(summary_ticks_data)
    assert(std_size2 == std_size)
    rows_size = len(rows_data)

    if ts_range != std_size:
        print(f"\t\t!!!WARNING!!! ts_range=(last_ts - first_ts)={ts_range} != "
              f"summary_ticks_data.size={std_size}\n")

    if rows_size != std_size:
        print(f"\t\t!!!WARNING!!! rows_size=len(rows_data)={rows_size} != "
              f"summary_ticks_data.size={std_size}\n")

    for i in range(0, std_size):
        shifted = first_ts + i

        current_ts = int(rows_data[i] / 1000)
        if current_ts != shifted:
            error_dt = ts_to_date_str(current_ts * 1000)
            shifted_dt = ts_to_date_str(shifted * 1000)
            print(f"\t\tERROR! Current ts {current_ts} != shifted {shifted} at i={i}!!!")
            print(f"\t\tERROR! error_dt: {error_dt} != shifted_dt {shifted_dt}")

            prev_1_dt = ts_to_date_str(rows_data[i - 1])
            prev_2_dt = ts_to_date_str(rows_data[i - 2])
            prev_3_dt = ts_to_date_str(rows_data[i - 3])
            print(f"\t\t\trows_data[i-1]: {prev_1_dt}")
            print(f"\t\t\trows_data[i-2]: {prev_2_dt}")
            print(f"\t\t\trows_data[i-3]: {prev_3_dt}")

            errors += 1
            if errors > 20:
                break

            if errors == 1:
                last_valid_dt = ts_to_date_str(rows_data[i - 1])
                print(f"\n\tFirst wrong ts was encountered, last_valid_index = {i - 1}, dt: {last_valid_dt}")

    if not errors:
        print(f"\n\nSummary_ticks_data from {first_ts} to {last_ts} was successfully validated! "
              f"(0 errors)\n\n")
        return True
    else:
        print(
            f"\n\nSummary_ticks_data from {first_ts} to {last_ts} was validated with "
            f"{errors} ERRORS!!!\n\n")
        return False


def print_td_stats(tick_data):
    first_ts = tick_data[0, 0]
    last_ts = tick_data[-1, 0]
    start_d = ts_to_date_str(first_ts)
    end_d = ts_to_date_str(last_ts)
    print(f"\tfirst_ts:\t{first_ts}\n\tlast_ts:\t{last_ts}")
    print(f"\tstart_d:\t{start_d}\n\tend_d:\t{end_d}\n")


def main():
    caches_dirs = [
        # "h:/GitRepositories/my_passivbot/backtests/binance"
        # "h:/GitRepositories/my_passivbot/backtests/binance/ADAUSDT"
        "h:/GitRepositories/my_passivbot/backtests/binance/MATICUSDT"
    ]

    for cache_dir in caches_dirs:
        for root, dirs, files in os.walk(cache_dir):
            if "\\" not in root:
                continue

            root_dir_name = os.path.basename(root)

            if root_dir_name == "caches":
                print(f"root: {root}")
                print(f"dirs: {dirs}")
                print(f"files: {files}")

                ticker_path = os.path.abspath(os.path.join(root, os.pardir))
                ticker = os.path.basename(ticker_path)
                print(f"\tCollecting caches for ticker {ticker}")

                summary_ticks_data = None

                for file_name in files:
                    if not file_name.endswith(".npy"):
                        continue

                    print(f"\tcache ticks data for {file_name}:\n")
                    ticks_cache_filepath = os.path.join(root, file_name)
                    tick_data = np.load(ticks_cache_filepath)
                    print_td_stats(tick_data)

                    if summary_ticks_data is None:
                        summary_ticks_data = tick_data
                        print(f"\n\tCreated summary_ticks_data of shape {summary_ticks_data.shape}")
                    else:
                        print(f"\n\tJoining summary_ticks_data of shape {summary_ticks_data.shape} with another "
                              f"tick_data of shape {tick_data.shape}...")
                        summary_ticks_data = join_ticks_data_v2(summary_ticks_data, tick_data)
                        print(f"\tUpdated summary_ticks_data shape (after join): {summary_ticks_data.shape}\n")

                status = validate_ticks_data(summary_ticks_data, root)
                if status:
                    print_td_stats(summary_ticks_data)
                    start_d = ts_to_date(summary_ticks_data[0, 0])
                    end_d = ts_to_date(summary_ticks_data[-1, 0])
                    updated_file_name = f"{start_d.strftime('%Y-%m-%d')}_{end_d.strftime('%Y-%m-%d')}" \
                                        f"__joined__ticks_cache.npy"
                    updated_ticks_cache_filepath = os.path.join(root, updated_file_name)
                    print(f"Saving updated ticks data for {ticker} with filename {updated_file_name}")
                    np.save(updated_ticks_cache_filepath, summary_ticks_data)


if __name__ == "__main__":
    main()
