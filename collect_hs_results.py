import os
import glob
import json
from results_collection_utils import HSResultsData, append_result, format_columns
from sortedcontainers import SortedDict

os.environ["NOJIT"] = "false"


# ==============================    CONFIG FILE EXAMPLE    ==============================
# {"config_name": "recursive_grid_9_symbols_49days",
#  "logging_level": 0,
#  "long": {"auto_unstuck_ema_dist": 0.048517444291398794,
#           "auto_unstuck_wallet_exposure_threshold": 0.2863892176776237,
#           "backwards_tp": true,
#           "ddown_factor": 2.510540540936911,
#           "ema_span_0": 1887.0805012670946,
#           "ema_span_1": 9976.858778004706,
#           "enabled": true,
#           "initial_eprice_ema_dist": -0.07400807098123924,
#           "initial_qty_pct": 0.044577515684342574,
#           "markup_range": 0.022634192860467042,
#           "min_markup": 0.010266573111291963,
#           "n_close_orders": 5,
#           "rentry_pprice_dist": 0.03582221188932456,
#           "rentry_pprice_dist_wallet_exposure_weighting": 29.956136002102458,
#           "wallet_exposure_limit": 1},
#  "short": {"auto_unstuck_ema_dist": 0.024100048487077787,
#            "auto_unstuck_wallet_exposure_threshold": 0.2956970159789194,
#            "backwards_tp": true,
#            "ddown_factor": 2.2182111597980536,
#            "ema_span_0": 828.7129980839718,
#            "ema_span_1": 6638.710660705248,
#            "enabled": true,
#            "initial_eprice_ema_dist": -0.05619188212009357,
#            "initial_qty_pct": 0.040297489692923925,
#            "markup_range": 0.04142093444613851,
#            "min_markup": 0.04361211720251938,
#            "n_close_orders": 15,
#            "rentry_pprice_dist": 0.008890376302888497,
#            "rentry_pprice_dist_wallet_exposure_weighting": 2.3347318746818075,
#            "wallet_exposure_limit": 1}}


def print_results_table(dir_name, results_sorted):
    columns = ["TICKER", "PNL", "PNL LONG", "PNL SHORT", "LOSS LONG", "LOSS SHORT", "LONG EMA 0", "LONG EMA 1",
               "SHORT EMA 0", "SHORT EMA 1", "DATE RANGE", "RESULT FILE", "CONFIG FILE"]
    table_format = format_columns(columns)
    table_header = table_format.format(*columns)
    header_len = len(table_header)
    print("\n\nResults for dir '{0}':\n{1}\n{2}"
          .format(dir_name, table_header, "-" * header_len))
    for pnl in results_sorted:
        rfd = results_sorted[pnl]
        print(table_format.format(rfd.ticker, rfd.pnl, rfd.pnl_long, rfd.pnl_short, rfd.loss_long, rfd.loss_short,
                                  rfd.config_long["ema_span_0"], rfd.config_long["ema_span_1"],
                                  rfd.config_short["ema_span_0"], rfd.config_short["ema_span_1"],
                                  rfd.run_conditions.get("date_range", ""), rfd.results_file, rfd.config_file))
    print("-" * header_len)
    print(table_header)
    print("-" * header_len)


def main():
    results_dirs = [
        # "C:/GitRepositories/my_passivbot/results_harmony_search_recursive_grid/2022-05-23T15-43-58_9_symbols___",
        # "C:/GitRepositories/my_passivbot/results_harmony_search_recursive_grid/2022-05-22T19-27-02_9_symbols"
        # "C:/GitRepositories/my_passivbot/results_harmony_search_recursive_grid/2022-06-02T09-30-55_9_symbols"
        # "C:/GitRepositories/my_passivbot/results_harmony_search_recursive_grid/2022-06-29T20-42-46_FTMUSDT"
        # "C:/GitRepositories/my_passivbot/results_harmony_search_recursive_grid/2022-07-01T08-58-47_FTMUSDT"
        # "C:/GitRepositories/my_passivbot/results_harmony_search_recursive_grid/2022-07-02T12-55-33_FTMUSDT"
        # "C:/GitRepositories/my_passivbot/results_harmony_search_recursive_grid/2022-07-02T23-32-19_FTMUSDT"
        # "C:/GitRepositories/my_passivbot/results_harmony_search_recursive_grid/2022-07-06T20-06-15_FTMUSDT"
        # "C:/GitRepositories/my_passivbot/results_harmony_search_recursive_grid/2022-07-07T00-17-59_FTMUSDT"
        # "C:/GitRepositories/my_passivbot/results_harmony_search_recursive_grid/2022-07-11T01-18-55_FTMUSDT"
        # "C:/GitRepositories/my_passivbot/results_harmony_search_recursive_grid/2022-07-12T01-01-40_6_symbols"
        "C:/GitRepositories/my_passivbot/results_harmony_search_recursive_grid/2022-07-14T09-34-26_6_symbols"
    ]

    for results_dir in results_dirs:
        dir_name = results_dir[results_dir.rindex("/") + 1:]
        results_list = glob.glob(results_dir + "/*_result_*.json")
        results_sorted = SortedDict()

        for result_file_name in results_list:
            file_name = result_file_name[result_file_name.rindex("\\") + 1:]
            file_index = file_name[:file_name.index("_")]
            config_file_pattern = results_dir + f"/{file_index}_best_config_*.json"
            config_files = glob.glob(config_file_pattern)
            if not config_files:
                print(f"ERROR: Config file not found for result file '{result_file_name}'")
                continue
            config_file_name = config_files[0]  # there should be no other config files for the result file

            run_cond_file_pattern = results_dir + "/hs_run_conditions.json"
            run_cond_files = glob.glob(run_cond_file_pattern)
            run_conditions = {}
            if run_cond_files:
                run_cond_file_name = run_cond_files[0]
                with open(run_cond_file_name, "r") as run_cond_file:
                    run_conditions = json.load(run_cond_file)

            with open(config_file_name, "r") as config_file:
                config_data = json.load(config_file)
                with open(result_file_name, "r") as result_file:
                    result_data = json.load(result_file)
                    for ticker in result_data:
                        d = result_data[ticker]
                        pnl = (d["pnl_sum_long"] + d["pnl_sum_short"])
                        rfd = HSResultsData(ticker, d["starting_balance"], d["final_balance_long"],
                                            d["final_balance_short"], pnl, d["pnl_sum_long"], d["pnl_sum_short"],
                                            d["loss_sum_long"], d["loss_sum_short"],
                                            result_file_name[:-5], config_file_name[:-5],
                                            config_data["long"], config_data["short"],
                                            d, config_data, run_conditions)
                        append_result(results_sorted, pnl, rfd)

        print_results_table(dir_name, results_sorted)


if __name__ == "__main__":
    main()
