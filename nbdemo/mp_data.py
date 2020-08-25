# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Demo QueryProvider."""
from pathlib import Path
import pickle
from typing import Any, Iterable
from time import sleep

import pandas as pd


def read_pd_df(data_file, query_name):
    """Read DataFrame from file."""
    if not Path(data_file).is_file():
        raise FileNotFoundError(
            f"Data file {data_file} for query {query_name} not found."
        )

    if data_file.lower().endswith("csv"):
        return pd.read_csv(
            data_file, infer_datetime_format=True, parse_dates=["TimeGenerated"]
        )
    return pd.read_pickle(data_file)


class TILookupDemo:
    """TILookup demo class"""

    _DATA_DEFS = {
        "ipv4": "data/ti_results_ipv4.pkl",
        "url": "data/ti_results_url.pkl",
    }

    def lookup_ioc(self, ioc_type, **kwargs):
        """Lookup single IoC."""
        sleep(1)
        return read_pd_df(self._DATA_DEFS.get(ioc_type), ioc_type)

    @staticmethod
    def result_to_df(results):
        """Convert IoC results to DataFrame."""
        if isinstance(results, pd.DataFrame):
            return results
        return pd.DataFrame()


class GeoLiteLookupDemo:
    """GeoLitLookup demo class."""

    _DATA_DEFS = {
        "ip_locs": "data/ip_locations.pkl",
    }

    def lookup_ip(
        self,
        ip_address: str = None,
        ip_addr_list: Iterable = None,
        ip_entity: Any = None,
    ):
        """Look up location."""
        del ip_address, ip_addr_list, ip_entity
        with open(self._DATA_DEFS["ip_locs"], "rb") as iploc_file:
            ip_locs = pickle.load(iploc_file)
        return str(ip_locs), ip_locs


_ASN_DATA = pd.read_pickle("data/az_whois.df.pkl")


def get_whois_info_demo(ip_addr, show_progress=False):
    """Lookup Whois data from dataframe."""
    sleep(0.02)
    if show_progress:
        print(".", end="")
    if "ExtASN" not in _ASN_DATA.columns:
        return "Unknown", {}
    match_row = _ASN_DATA[_ASN_DATA["AllExtIPs"] == ip_addr]
    asn_text = match_row["ExtASN"].unique()[0]
    if isinstance(asn_text, tuple):
        return asn_text[0], {}
    return asn_text, {}
