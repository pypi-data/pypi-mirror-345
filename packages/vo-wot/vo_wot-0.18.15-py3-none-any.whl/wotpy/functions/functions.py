#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generic function definitions.
"""

import time
import datetime

import numpy as np
import tornado.httpclient
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller

async def forecasting(exposed_thing, property_name):
    servient = exposed_thing.servient

    query = f'from(bucket:"{property_name}") |> range(start: -10m)'
    tables = servient.influxdb.execute_query(query)

    # Serialize to values
    output = tables.to_values(columns=["_value"])
    flat_list = [item for sublist in output for item in sublist]

    arr = np.array(flat_list)

    d = 1  # Assume the data is non-stationary and requires differencing

    # Check for stationarity using ADF test
    p_value = adfuller(arr)[1]
    if p_value < 0.05:
        d = 0  # Data is already stationary, no differencing needed

    p, q = 1, 1

    model = ARIMA(arr, order=(p, d, q))
    model_fit = model.fit()

    predicted_value = model_fit.forecast(steps=1)

    return float(predicted_value[0])


async def mean_value(exposed_thing, property_name, horizon):
    """Queries the influxdb database and averages the data
    for the given property."""

    servient = exposed_thing.servient

    query = 'from(bucket:"{}")\
        |> range(start: -10m)\
        |> tail(n:{})\
        |> mean()'.format(property_name, horizon) #TODO change limit of query

    tables = servient.influxdb.execute_query(query)
    # Serialize to values
    output = tables.to_values(columns=["_value"])
    flat_list = [item for sublist in output for item in sublist]
    return flat_list[0]

async def vo_status(exposed_thing, id):
    """Attempts to access the catalogue port of the VO and if successful
    inserts a row containing an integer (0 for failure or 1 for success)
    in the corresponding table. Returns all rows from the `vo_status` table."""

    servient = exposed_thing.servient

    timestamp = time.time()
    datetime_format = datetime.datetime.fromtimestamp(timestamp)

    try:
        http_client = tornado.httpclient.AsyncHTTPClient()
        url = f"http://localhost:{servient.catalogue_port}"
        await http_client.fetch(url)
    except Exception as exception:
        print(f"Connection to VO Error: {exception}")
        exposed_thing.emit_event("VO_Connection_Error")
        servient.sqlite_db.insert_data("vo_status", (id, datetime_format, 0))
    else:
        servient.sqlite_db.insert_data("vo_status", (id, datetime_format, 1))

    return servient.sqlite_db.execute_query("SELECT * FROM vo_status")
    # TODO initialize event on cli if status_vo is enabled
    # TODO change localhost


# Deployment type A
async def device_status(exposed_thing, device_catalogue_url, id):
    """Attempts to access the catalogue port of the device and if successful
    inserts a row containing an integer (0 for failure or 1 for success)
    in the corresponding table. Returns all rows from the `device_status` table."""

    servient = exposed_thing.servient

    timestamp = time.time()
    datetime_format = datetime.datetime.fromtimestamp(timestamp)
    try:
        http_client = tornado.httpclient.AsyncHTTPClient()
        await http_client.fetch(device_catalogue_url)
    except Exception as exception:
        print(f"Connection to Device Error: {exception}")
        exposed_thing.emit_event("Device_Connection_Error", f"Device_Connection_Error: {False}%")
        servient.sqlite_db.insert_data("device_status", (id, datetime_format, 0))
    else:
        servient.sqlite_db.insert_data("device_status", (id, datetime_format, 1))
    return servient.sqlite_db.execute_query("SELECT * FROM device_status")
    # TODO initialize event on cli if status_device is enabled
    # TODO device must have an id or name
    # TODO think of a way to implement this in deployment type B