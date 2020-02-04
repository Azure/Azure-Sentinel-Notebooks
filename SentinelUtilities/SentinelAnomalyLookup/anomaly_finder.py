# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
Anomaly Finder module:
This module has two classes: AnomalyQueries and AnomalyFinder
"""

import copy
import datetime as dt
import pandas as pd
from pandas.io.json import json_normalize
from azure.loganalytics.models import QueryBody

from SentinelUtils.obfuscation_utility import ObfuscationUtility
from SentinelLog.log import Log
from .anomaly_lookup_view_helper import AnomalyLookupViewHelper


class AnomalyQueries(): # pylint: disable=too-few-public-methods
    """ KQLs for anomaly lookup """

    KEY = b'7jH91qslpgxNSdVPiQwtr2D4bSg2i5ArfJqAMA1zCkU='
    QUERIES = {}
    # pylint: disable=line-too-long
    QUERIES['LISTTABLES'] = b'gAAAAABdNjjk1mX80_10papIcwNncViofTHxyN0UxY4LbKxYdIX-jBhGue8E2j7HOFUnkC_iQtR8q58OHpQzVVHdR264WDvRZxUULG6WaC5kLk-DXCpq7-JidKVvD2om3Foq0OYPxOuE0YNwoIMsXJnISmmP2eilXg=='
    # pylint: disable=line-too-long
    QUERIES['ISCATCOLUMN'] = b'gAAAAABdNjkBT7XTAvPjCp56dI7LRL35EPMzF8UX_c4Hs0q910bTI2y-6viJGG7ZlXjclORrXFK68dAd2dYfLB0A_rw0Q9CeLEGUuWkHSFc7al2xwu7uEgliddsQQyocWhqyWlEtFEReIeJaqZYaSOkLon7sPN_icKEwiHc096kCkyjw5D0TeZ0Kgmnc5799Al7ND0kAk7KO'
    # pylint: disable=line-too-long
    QUERIES['ISCATHEURISTIC'] = b'gAAAAABdNjkglsyzKMCUkIXq3aqcim0F70S86HfAqaiyNUIF0La2st1DkiQTFK_vqVIyxiY25i78FiT6y0yZG4YQmpAVVwRJ302KkeAPVq0mPPK1FKbRcnnqmIc1HOAycyv3dmDHDUG7-_b-wyy8IDneWYyTE3TxyLUcG3kJRTmQd_6-hLXfDUjctjm0VPrA9zcrN8Il1y-nq-4jOsFZbO0qvHZfnLBTwaf52hkXPqmkZN9Rz-deW6Q4VY_j7Vw7rRrXM5WxRchL2kJBhGOq-hM8A3W9AA7qHnkgVu2BOVEYZAT_EnHvks8YMcWP04WKs49Dw5Ga4UMqJeU4MJH8PKfNmn7zcuLwMA=='
    # pylint: disable=line-too-long
    QUERIES['TIMESERIESANOMALYDETECTION'] = b'gAAAAABeNN8ojnOJUuvi1_FI8bqz200wGX1CPFnxU8FHDnwmFx7Ywm54WwbFXMWXVIpiLf9zjv5Fcl85wdyBdA6KS7_xph89Geb5CQOoqMGt_-syZ_KgE4CXQoCDCfWmCYXlx2zzIZX5g88SfVJeLmWbCUsk20KTO0Ecdt6TauIUuLkCh85v55_j8RSxXvwZy4y-WAate9hZh1xoRV5fjvq1_ox2V_qpJO-HpzdCuZGelMx3DkxL0PUy2_SXLZdaa5HLl0vM0IfmiDqIQgcxnjAEwk6GGezh3FvT43BCwO_HX5PHixCkqozeXzbsLuWxOMpoZ5I1174dVWK-8e9uiVvMfwyOqeC9tlKoAUXAEBsXS41kEbAMTwlK3VcCqq9iTfnW0jUkSlMV7P_JbWOVxErwC4DtIKP5d6AyNcqVhBlOYZwouqoY734vBhDsx95bzN2mwwL2-_Set_ksdoxTLlFVaWK9MY4tmBCsoQSVHrVuo00K1zPYIh43VgbVm6gFLs7kdjFDraMb5fjx0VxXQrkUkeO3xZ7i9caKl2ODpoVf2ahAPxqPTmHIG9bqQBb2SGu3PakxrRiRanOLY-pJ4eN54fQlYhk-O-1UwpUnna4WVMbqST4tFbEBCpr4IeGNqnaEeNccuHaWHDdjxIEt5sZ402LFJAV0HvMOxOVD3qUjUroHFysJrZXzYJF9HApBbtryokMjgh1YPGAwguniTTyUQolrV_1m54yhJLd7I-39MnBpfobO6sXAtZjPxZfoCCmiJta_JaAuj2sW-8goxU0NBWUxBsiEnPIrHyJKLiduavgID2UcHR4rhByyUg3EzbeKFO-WS-oIVXn0jFUfGjhOKc70Xc1R3L_vvGe2029AYkWmHb36yEJgVlVJ4YQ_7eMSjosZA6R97SDzYXCC1eOopH1hyexwvJwmlzP2gb3NcZ41WbmCTA7vYlT1uH4IqMiuvNWwkZ7MpPIccOnwFWkLFzh_BpgDfvnGy-loqaTNuuLUYzoAyhejzfBQPwG7AlPwH85pfNGarrz7z47uMYQE51-R2gxpDSmw3QvWacKIs3F2g94umQjXJkZ9otiNxPqZceKINig3pFj_SMRiQ1vXRNyKUM8BYptJJ7CFR5TI37lElejgoQBD3VQ7uyK_Ghz8M4cJG1P3ry9d8mk0-vwNClGkb4WGgLR69dPBSZM03uQ14oolEHxuwPQgBoLM-Rlu3YuGQBfbCtqtarLa8IwFBQcbA6WsKJ2dDnCcrRdCuMMTsKuJlSfoU-7jAOwVN-ISg8m47aWbJZtjAODzPxuv9KOQlTfApJcjla37UKKctce9kVkYeoqi6dJnSF9HLsfbRhSIf9bWKHue2ML20urH-0xhIDxvSA=='
    # pylint: disable=line-too-long
    QUERIES['TIMEWINDOWQUERY'] = b'gAAAAABdOjxI1Cq7frn_5Gj1l2vvA6Eu-a5qghqvRTBc8I9gWdcI8JiALXjpT7qJwf8ZBCKCrwYtMXY2-bp7Cj4jwYVXVDKmXRjoyz0xLbiVdCkIc07U2sNjpwzO1y1OvRr2apYv5Y9_yh_vOpqN4uv1WUezH_z1bXNCO-yI-LMIlidav4Xh5KwRtGBTnXGBk5YidPJVHfnZZGpCQ5w7g4t0ptoM5p6w_eXC8RZ82J3QLIVGtguWISFYweE5GWVJkkUXq3aq3n36uIFl2T3YllLUX2FytfOw_B8Xt1UrspWURfgDx1xqyCnqUEPG_EnO-TuGKFbMkh6AjpcduidHTuuS45YGatPvzRzyAzElLnbj7-s0gc-0POrUyiNaeTj_Tg0wTBsIJklL'
    # pylint: disable=line-too-long
    QUERIES['ISENTITYINTABLE'] = b'gAAAAABdNkO8YYV6ElbBqI9qp0oLHLquoYJD_7umEu1sDgyHouYcN0jU6vlOPp8AN5lecaMvXPUqQ5ZiFw6393Z9l7kNOB7IMITURv59MZJxeEVpt5ud9F4ge-5JGge5k7ux2YU50z-u9djJYet2SO-n1MpD5xO14ODKtBPsr9guZ40wYJwMzwLCjDSpTXFnIDjYrXDhfU3D2YGc4jnrq2EePBUAPPKxnIXg7AtmnGm4Add1_aV-pDlHMXTn09Z3kvlUcHpHBw7g'

    @staticmethod
    def get_query(name):
        """ get KQL """

        en_query = AnomalyQueries.QUERIES[name]
        obfuscate = ObfuscationUtility(AnomalyQueries.KEY)
        query = obfuscate.deobfuscate_text(en_query)
        return query


class AnomalyFinder():
    """
    This class provides process flow functions for anomaly lookup.
    Method - run is the main entry point.
    """

    def __init__(self, workspace_id, la_data_client):
        self.workspace_id = workspace_id
        self.la_data_client = la_data_client
        self.logger = Log()
        self.anomaly = ''

    def query_table_list(self):
        """ Get a list of data tables from Log Analytics for the user """

        query = AnomalyQueries.get_query('LISTTABLES')
        return self.query_loganalytics(query)

    def query_loganalytics(self, query):
        """ This method will call Log Analytics through LA client """

        res = self.la_data_client.query(self.workspace_id, QueryBody(query=query))
        json = res.as_dict()
        cols = json_normalize(json['tables'][0], 'columns')
        data_frame = json_normalize(json['tables'][0], 'rows')
        if data_frame.shape[0] != 0:
            data_frame.columns = cols.name
        return data_frame

    @staticmethod
    def construct_related_queries(df_anomalies):
        """ This method constructs query for user to repo and can be saves for future references """

        if df_anomalies.shape[0] == 0:
            return None

        queries = ''
        for tbl in df_anomalies.Table.unique():

            cur_table_anomalies = df_anomalies.ix[df_anomalies.Table == tbl, :]
            query = """{tbl} \
            | where TimeGenerated > datetime({maxTimestamp})-1d and TimeGenerated < datetime({maxTimestamp}) \
            | where {entCol} has "{qEntity}" \
            | where """.format(**{
                'tbl': tbl,
                'qTimestamp': cur_table_anomalies.qTimestamp.iloc[0],
                'maxTimestamp': cur_table_anomalies.maxTimestamp.iloc[0],
                'entCol': cur_table_anomalies.entCol.iloc[0],
                'qEntity': cur_table_anomalies.qEntity.iloc[0]
            })

            for j, row in cur_table_anomalies.iterrows(): # pylint: disable=unused-variable
                query += " {col} == to{colType}(\"{colVal}\") or".format(
                    col=row.colName,
                    colType=(row.colType) if 'colType' in row.keys() else 'string',
                    colVal=row.colVal.replace('"', '')
                )

            query = query[:-2] # drop the last or
            query += " | take 1000; " # limit the output size
            query = query.replace("\\", "\\\\")

            queries += query
        return queries

    # pylint: disable=too-many-locals
    def get_timewindow(self, q_entity, q_timestamp, ent_col, tbl):
        """ find the relevant time window for analysis """

        win_start = 0
        min_timestamp = None
        delta = None
        max_timestamp = None
        long_min_timestamp = None
        time_window_query_template = AnomalyQueries.get_query('TIMEWINDOWQUERY')

        for from_hour in range(-30, 0, 1):
            kql_time_range_d = time_window_query_template.format(
                table=tbl,
                qDate=q_timestamp,
                entColumn=ent_col,
                qEntity=q_entity,
                f=from_hour,
                t=from_hour+1,
                delta='d')

            df_time_range = self.query_loganalytics(kql_time_range_d)

            if df_time_range.shape[0] > 0:
                win_start = from_hour
                break

        dt_q_timestamp = pd.to_datetime(q_timestamp)
        ind2now = dt.datetime.utcnow() - dt_q_timestamp
        if win_start < -3:
            if ind2now > dt.timedelta(days=1):
                delta = '1d'
                max_timestamp = dt_q_timestamp + dt.timedelta(days=1)
            else:
                delta = '1d'
                max_timestamp = dt.datetime.now()
            long_min_timestamp = max_timestamp + dt.timedelta(days=win_start)
            min_timestamp = max_timestamp + dt.timedelta(days=max([-6, win_start]))

        elif win_start < 0: # switch to hours
            win_start_hour = -5
            for from_hour in range(-3*24, -5, 1):
                kql_time_range_h = time_window_query_template.format(
                    table=tbl,
                    qDate=q_timestamp,
                    entColumn=ent_col,
                    qEntity=q_entity,
                    f=from_hour,
                    t=from_hour+1,
                    delta='h')

                df_time_range = self.query_loganalytics(kql_time_range_h)

                if df_time_range.shape[0] > 0:
                    win_start_hour = from_hour
                    break
            if win_start_hour < -5:
                if ind2now > dt.timedelta(hours=1):
                    delta = '1h'
                    max_timestamp = dt_q_timestamp + dt.timedelta(hours=1)
                else:
                    delta = '1h'
                    max_timestamp = dt.datetime.now()
                min_timestamp = max_timestamp + dt.timedelta(hours=win_start_hour)
                long_min_timestamp = min_timestamp

        return min_timestamp, delta, max_timestamp, long_min_timestamp

    # pylint: disable=too-many-locals
    def run(self, q_timestamp, q_entity, tables):
        """ Main function for Anomaly Lookup """

        progress_bar = AnomalyLookupViewHelper.define_int_progress_bar()
        display(progress_bar)  # pylint: disable=undefined-variable

        # list tables if not given
        if not tables:
            kql_list_tables = AnomalyQueries.get_query('LISTTABLES')
            tables = self.query_loganalytics(kql_list_tables)
            tables = tables.TableName.tolist()

        progress_bar.value += 1

        # find the column in which the query entity appears in each table
        # - assumption that it appears in just one columns
        tables2search = []
        is_entity_in_table_template = AnomalyQueries.get_query('ISENTITYINTABLE')

        for tbl in tables:
            print(tbl)
            kql_entity_in_table = is_entity_in_table_template.format(
                table=tbl,
                qDate=q_timestamp,
                qEntity=q_entity)
            ent_in_table = self.query_loganalytics(kql_entity_in_table)

            if ent_in_table.shape[0] > 0:
                ent_col = [col for col in ent_in_table.select_dtypes('object').columns[1:] if
                           ent_in_table.ix[0, col] is not None
                           and ent_in_table.ix[:, col].str.contains(q_entity, case=False).all()]
                if ent_col:
                    ent_col = ent_col[0]
                tables2search.append({'table': tbl, 'entCol': ent_col})

        progress_bar.value += 2

        # for each table, find the time window to query on
        for tbl in tables2search:
            tbl['minTimestamp'], tbl['delta'], tbl['maxTimestamp'], tbl['longMinTimestamp'] = \
            self.get_timewindow(q_entity, q_timestamp, tbl['entCol'], tbl['table'])

        progress_bar.value += 1

        # identify all the categorical columns per table on which we will find anomalies
        categorical_cols = []
        is_cat_column_template = AnomalyQueries.get_query('ISCATCOLUMN')
        is_cat_heuristic_template = AnomalyQueries.get_query('ISCATHEURISTIC')
        for tbl in tables2search:
            kql_is_cat_column = is_cat_column_template.format(table=tbl['table'])
            df_cols = self.query_loganalytics(kql_is_cat_column)

            for col in df_cols.ColumnName:
                kql_is_cat_heuristic = is_cat_heuristic_template.format(
                    table=tbl['table'],
                    column=col)
                df_is_cat = self.query_loganalytics(kql_is_cat_heuristic)

                if df_is_cat.shape[0] > 0:
                    cat_col_info = copy.deepcopy(tbl)
                    cat_col_info['col'] = col
                    categorical_cols.append(cat_col_info)

        progress_bar.value += 2

        anomalies_list = []
        time_series_anomaly_detection_template = \
            AnomalyQueries.get_query('TIMESERIESANOMALYDETECTION')
        for col_info in categorical_cols:
            max_timestamp = col_info['maxTimestamp'].strftime('%Y-%m-%dT%H:%M:%S.%f')
            long_min_timestamp = col_info['longMinTimestamp'].strftime('%Y-%m-%dT%H:%M:%S.%f')

            kql_time_series_anomaly_detection = time_series_anomaly_detection_template.format(
                table=col_info['table'],
                column=col_info['col'],
                entColumn=col_info['entCol'],
                qEntity=q_entity,
                minTimestamp=long_min_timestamp,
                maxTimestamp=max_timestamp,
                qTimestamp=q_timestamp,
                delta=col_info['delta'])

            cur_anomalies = self.query_loganalytics(kql_time_series_anomaly_detection)

            anomalies_list.append(cur_anomalies)

        progress_bar.value += 2

        if anomalies_list:
            anomalies = pd.concat(anomalies_list, axis=0)
        else:
            anomalies = pd.DataFrame()

        progress_bar.value += 1
        queries = AnomalyFinder.construct_related_queries(anomalies)
        progress_bar.close()
        self.anomaly = str(anomalies.to_json(orient='records'))

        return anomalies, queries
# End of the Module #
