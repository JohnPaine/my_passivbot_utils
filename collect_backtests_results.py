import os
import glob
import json
from sortedcontainers import SortedDict
from results_collection_utils import BacktestResultsData, append_result, format_columns

os.environ["NOJIT"] = "false"

# ==============================    BACKTEST RESULTS FILE EXAMPLE    ==============================
# {
#     "market_type": "futures",
#     "user": "binance_backtest_1",
#     "symbol": "FTMUSDT",
#     "latency_simulation_ms": 1000,
#     "starting_balance": 1000,
#     "start_date": "2022-01-01",
#     "end_date": "2022-05-27",
#     "base_dir": "backtests",
#     "ohlcv": false,
#     "spot": false,
#     "exchange": "binance",
#     "session_name": "2022-01-01_2022-05-27",
#     "caches_dirpath": "backtests\\binance\\FTMUSDT\\caches\\",
#     "optimize_dirpath": "backtests\\binance\\FTMUSDT\\optimize\\",
#     "plots_dirpath": "backtests\\binance\\FTMUSDT\\plots\\2022-06-05T120027\\",
#     "maker_fee": 0.0002,
#     "taker_fee": 0.0004,
#     "inverse": false,
#     "max_leverage": 25,
#     "min_qty": 1.0,
#     "min_cost": 5.0,
#     "qty_step": 1.0,
#     "price_step": 0.0001,
#     "c_mult": 1.0,
#     "hedge_mode": true,
#     "n_parts": null,
#     "config_name": "recursive_grid_9_symbols_146days",
#     "logging_level": 0,
#     "long": {
#         "auto_unstuck_ema_dist": 0.0921432453527539,
#         "auto_unstuck_wallet_exposure_threshold": 0.14844892557720607,
#         "backwards_tp": true,
#         "ddown_factor": 3,
#         "ema_span_0": 1073.803573141247,
#         "ema_span_1": 9553.485102080393,
#         "enabled": true,
#         "initial_eprice_ema_dist": -0.03336925830826522,
#         "initial_qty_pct": 0.015376777120115669,
#         "markup_range": 0.03423356283898927,
#         "min_markup": 0.04356330078699584,
#         "n_close_orders": 30,
#         "rentry_pprice_dist": 0.028389542334091657,
#         "rentry_pprice_dist_wallet_exposure_weighting": 29.80495018704926,
#         "wallet_exposure_limit": 1
#     },
#     "short": {
#         "auto_unstuck_ema_dist": 0.015081541870091553,
#         "auto_unstuck_wallet_exposure_threshold": 0.4670150570651598,
#         "backwards_tp": true,
#         "ddown_factor": 2.32616347410591,
#         "ema_span_0": 2374.20011073752,
#         "ema_span_1": 1872.0721906004637,
#         "enabled": true,
#         "initial_eprice_ema_dist": -0.014968738809220589,
#         "initial_qty_pct": 0.03159336079542576,
#         "markup_range": 0.03861681574634097,
#         "min_markup": 0.05051569206153051,
#         "n_close_orders": 10,
#         "rentry_pprice_dist": 0.015375677479105725,
#         "rentry_pprice_dist_wallet_exposure_weighting": 75.97881834745871,
#         "wallet_exposure_limit": 1
#     },
#     "n_days": 146.0,
#     "passivbot_mode": "recursive_grid",
#     "result": {
#         "DGstd_long": 0.05360923978934299,
#         "DGstd_short": 0.018990799439381874,
#         "adg_DGstd_ratio_long": -0.0337359574461627,
#         "adg_DGstd_ratio_short": 0.15312813645744347,
#         "adg_long": -0.0018085590322544072,
#         "adg_per_exposure_long": -0.0018085590322544072,
#         "adg_per_exposure_short": 0.0029080257279896085,
#         "adg_realized_long": 0.0005513918798030204,
#         "adg_realized_per_exposure_long": 0.0005513918798030204,
#         "adg_realized_per_exposure_short": 0.0027327474172782473,
#         "adg_realized_short": 0.0027327474172782473,
#         "adg_short": 0.0029080257279896085,
#         "avg_fills_per_day_long": 0.3493167300072774,
#         "avg_fills_per_day_short": 0.6438386788369427,
#         "biggest_psize_long": 1648.0,
#         "biggest_psize_quote_long": 1253.2721,
#         "biggest_psize_quote_short": 590.3421,
#         "biggest_psize_short": 1583.0,
#         "closest_bkr_long": 0.98608724150173,
#         "closest_bkr_short": 1.0,
#         "eqbal_ratio_mean_long": 0.8998356488223596,
#         "eqbal_ratio_mean_short": 0.9858316955981364,
#         "eqbal_ratio_min_long": 0.3026969191315857,
#         "eqbal_ratio_min_short": 0.8412286547774228,
#         "exchange": "binance",
#         "fee_sum_long": -1.6687238599999998,
#         "fee_sum_short": -2.2161422200000005,
#         "final_balance_long": 1083.8078697622907,
#         "final_balance_short": 1489.491909706722,
#         "final_equity_long": 615.7087761399998,
#         "final_equity_short": 1484.8781577800005,
#         "gain_long": 0.08547659362229094,
#         "gain_short": 0.4917080519267214,
#         "hrs_stuck_avg": 76.17355072463768,
#         "hrs_stuck_avg_long": 76.17355072463768,
#         "hrs_stuck_avg_short": 36.8840350877193,
#         "hrs_stuck_max": 586.7166666666667,
#         "hrs_stuck_max_long": 586.7166666666667,
#         "hrs_stuck_max_short": 554.8,
#         "loss_sum_long": -164.06580637770895,
#         "loss_sum_short": 0.0,
#         "n_closes_long": 20,
#         "n_closes_short": 38,
#         "n_days": 145.99930555555557,
#         "n_entries_long": 31,
#         "n_entries_short": 56,
#         "n_fills_long": 51,
#         "n_fills_short": 94,
#         "n_ientries_long": 9,
#         "n_ientries_short": 30,
#         "n_normal_closes_long": 17,
#         "n_normal_closes_short": 38,
#         "n_rentries_long": 19,
#         "n_rentries_short": 26,
#         "n_unstuck_closes_long": 3,
#         "n_unstuck_closes_short": 0,
#         "n_unstuck_entries_long": 3,
#         "n_unstuck_entries_short": 0,
#         "net_pnl_plus_fees_long": 83.80786976229095,
#         "net_pnl_plus_fees_short": 489.4919097067214,
#         "pa_distance_max_long": 2.271584638115475,
#         "pa_distance_max_short": 0.2844855086832515,
#         "pa_distance_mean_long": 0.2601215405744941,
#         "pa_distance_mean_short": 0.05682377535380433,
#         "pa_distance_std_long": 0.38713255882055336,
#         "pa_distance_std_short": 0.052375851590069404,
#         "pnl_sum_long": 85.47659362229095,
#         "pnl_sum_short": 491.7080519267214,
#         "profit_sum_long": 249.54239999999993,
#         "profit_sum_short": 491.7080519267214,
#         "starting_balance": 1000.0,
#         "symbol": "FTMUSDT",
#         "volume_quote_long": 8343.6193,
#         "volume_quote_short": 11080.711099999999
#     }
# }


def print_results_table(dir_path, results_sorted):
    columns = ["TICKER", "PNL, %", "PNL, $", "START $", "FINAL $ Long", "FINAL $ Short", "TEST RUN DT", "START DATE",
               "END DATE", "PROFIT LONG", "PROFIT SHORT", "LOSS LONG", "LOSS SHORT", "LONG EXP.L", "SHORT EXP.L",
               "AVG HS L", "MAX HS L", "AVG HS S", "MAX HS S", "CONFIG NAME"]
    table_format = format_columns(columns, {"TEST RUN DT": 18})
    table_header = table_format.format(*columns)
    header_len = len(table_header)
    print("\n\nResults for dir '{0}':\n{1}\n{2}"
          .format(dir_path, table_header, "-" * header_len))
    for pnl in results_sorted:
        brd = results_sorted[pnl]
        conf_long = brd.result_data["long"]
        conf_short = brd.result_data["short"]
        rd = brd.result_data["result"]
        start_balance = brd.result_data["starting_balance"]
        pnl_usd = round(brd.pnl, 1)
        pnl_rel = round(brd.pnl / start_balance * 100., 1)
        fb_long = round(rd["final_balance_long"], 3)
        fb_short = round(rd["final_balance_short"], 3)
        l_long = round(rd["loss_sum_long"], 2)
        l_short = round(rd["loss_sum_short"], 2)
        avg_hsl = round(rd["hrs_stuck_avg_long"])
        max_hsl = round(rd["hrs_stuck_max_long"])
        avg_hss = round(rd["hrs_stuck_avg_short"])
        max_hss = round(rd["hrs_stuck_max_short"])
        print(table_format.format(brd.ticker, pnl_rel, pnl_usd, start_balance, fb_long, fb_short, brd.test_run_dt,
                                  brd.result_data["start_date"], brd.result_data["end_date"], rd["profit_sum_long"],
                                  rd["profit_sum_short"], l_long, l_short,
                                  conf_long["wallet_exposure_limit"], conf_short["wallet_exposure_limit"],
                                  avg_hsl, max_hsl, avg_hss, max_hss,
                                  brd.result_data["config_name"]))
    print("-" * header_len)
    print(table_header)
    print("-" * header_len)


def main():
    results_dirs = [
        "h:/GitRepositories/my_passivbot/backtests/binance"
        # "g:/STORAGE/PASSIVBOT_DATA/backtests/binance"
        # "C:/GitRepositories/my_passivbot/backtests/binance/FTMUSDT/plots"
    ]

    results_sorted = SortedDict()
    for results_dir in results_dirs:
        for root, _, _ in os.walk(results_dir):
            dir_path = root
            results_file_path = dir_path + "/result.json"
            if os.path.exists(results_file_path):
                test_run_dt = dir_path[dir_path.rindex("\\") + 1:]
                with open(results_file_path, "r") as result_file:
                    result_data = json.load(result_file)
                    ticker = result_data["symbol"]
                    d = result_data["result"]
                    pnl = (d["pnl_sum_long"] + d["pnl_sum_short"])
                    brd = BacktestResultsData(ticker, test_run_dt, pnl, result_data)
                    append_result(results_sorted, pnl, brd)

        print_results_table(results_dir, results_sorted)


if __name__ == "__main__":
    main()
