#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Utility functions for SDN-related functionalities"""

import json

import tornado.httpclient

JSON_HEADERS = {"Content-Type": "application/json"}


async def apply_sdn_configuration (controller_url, sdn_configuration):
    print ("connecting to controller URL to apply SDN configuration")

    api_url = f"{controller_url}/configuration"
    http_client = tornado.httpclient.AsyncHTTPClient()
    http_request = tornado.httpclient.HTTPRequest(
        api_url,
        method="POST",
        headers=JSON_HEADERS,
        body=json.dumps(sdn_configuration)
    )
    try:
        response = await http_client.fetch(http_request)
        return json.loads(response.body)

    except tornado.httpclient.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        if e.response:
            return {"error": f"Failed to apply configuration: {e.response.body}"}
        return {"error": f"HTTPError: {str(e)}"}

    except Exception as e:
        print(f"An error occurred: {e}")
        return {"error": f"An unexpected error occurred: {str(e)}"}


async def retrieve_sdn_topology (controller_url):
    print ("connecting to controller URL to retrieve SDN topology")

    api_url = f"{controller_url}/topology"
    http_client = tornado.httpclient.AsyncHTTPClient()
    http_request = tornado.httpclient.HTTPRequest(
        api_url,
        method="GET",
        headers=JSON_HEADERS
    )
    response = await http_client.fetch(http_request)
    return json.loads(response.body)


async def apply_sdn_flows (controller_url, sdn_flows):
    print ("connecting to controller URL to apply SDN flows")

    api_url = f"{controller_url}/flows"
    http_client = tornado.httpclient.AsyncHTTPClient()
    http_request = tornado.httpclient.HTTPRequest(
        api_url,
        method="POST",
        headers=JSON_HEADERS,
        body=json.dumps(sdn_flows)
    )
    response = await http_client.fetch(http_request)
    return json.loads(response.body)


def inject_sdn_properties(exposed_thing, controller_url):
    """Inject SDN related properties to an exposed thing"""

    async def sdn_configuration_write_handler(value):
        await exposed_thing._default_update_property_handler("sdn_configuration", value)
        if value is not None:
            result = await apply_sdn_configuration(controller_url, value)
            if result is not None:
                print (result)
                #await exposed_thing.write_property("sdn_topology", sdn_topology)

    async def sdn_topology_read_handler():
        sdn_topology = await retrieve_sdn_topology (controller_url)
        print(sdn_topology)
        await exposed_thing._default_update_property_handler("sdn_topology", sdn_topology)
        return sdn_topology

    async def sdn_flows_write_handler(value):
        await exposed_thing._default_update_property_handler("sdn_flows", value)

    prop_dict = {
        "type": "string",
        "observable": True
    }
    sdn_property_handlers = {
        "sdn_configuration": sdn_configuration_write_handler,
        "sdn_flows": sdn_flows_write_handler
    }
    for proprty, handler in sdn_property_handlers.items():
        exposed_thing.add_property(proprty, prop_dict)
        exposed_thing.set_property_write_handler(proprty, handler)
    exposed_thing.add_property("sdn_topology", prop_dict)
    exposed_thing.set_property_read_handler("sdn_topology", sdn_topology_read_handler)
