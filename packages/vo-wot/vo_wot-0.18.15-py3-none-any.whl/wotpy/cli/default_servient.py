#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Default Servient class
"""

import logging
import ssl
from urllib.parse import urlparse, urlunparse

from wotpy.utils.utils import dict_merge
from wotpy.wot.servient import Servient


class DefaultServient(Servient):
    """Servient with preconfigured values."""

    DEFAULT_CONFIG = {
        "type": "VO",
        "deploymentType": "A",
        "catalogue": 9090,
        "bindingNB": {
            "bindingModeNB": ["U", "H"],
            "hostname": None,
            "ports": {
                "coapPort": 5683,
                "httpPort": 8080
            },
            "netconf": {
                "enabled": False,
                "schedulerURL": None,
                "netconfServerURL": None
            },
            "sdn": {
                "enabled": False,
                "controllerURL": None
            },
            "brokerIP": None,
            "routerURL": None,
            "serverCert": None,
            "serverKey": None,
            "externalCertificate": False,
            "mqttCAFile": None,
            "OSCORECredentialsMap": None,
            "securityNB": {
                "securityScheme": "nosec",
                "username": None,
                "password": None,
                "token": None
            }
        },
        "bindingSB": {
            "bindingModeSB": None,
            "mqttCAFile": None,
            "OSCORECredentialsMap": None,
            "securitySB": {
                "securitySBHTTP": {
                    "securityScheme": "nosec",
                    "username": None,
                    "password": None,
                    "token": None,
                    "holderUrl": None,
                    "requester": None
                },
                "securitySBMQTT": {
                    "securityScheme": "nosec",
                    "username": None,
                    "password": None
                },
                "securitySBCOAP": {
                    "securityScheme": "nosec",
                    "username": None,
                    "password": None,
                    "token": None
                }
            }
        },
        "databaseConfig": {
            "timeseriesDB": {
                "influxDB": "disabled",
                "address": "http://localhost:8086",
                "dbUser": "my-username",
                "dbPass": "my-password",
                "dbToken": "my-token"
            },
            "persistentDB": {
                "SQLite": "enabled",
                "dbFilePath": None
            }
        }
    }

    def __init__(self, config):
        self._logr = logging.getLogger(__name__)

        default_config = dict(self.DEFAULT_CONFIG)
        dict_merge(default_config, config)
        self.config = default_config

        vo_name = self.config["name"]

        servers = []
        server_bindings_north = self.config["bindingNB"]
        hostname = server_bindings_north["hostname"]
        binding_modes_north = server_bindings_north["bindingModeNB"]
        security_north = server_bindings_north["securityNB"]
        security_scheme = {"scheme": security_north["securityScheme"]}
        username_north = security_north["username"]
        password_north = security_north["password"]
        token_north = security_north["token"]

        credentials_dict_north = {vo_name: {}}
        if username_north is not None and password_north is not None:
            credentials_dict_north[vo_name]["username"] = username_north
            credentials_dict_north[vo_name]["password"] = password_north

        if token_north is not None:
            credentials_dict_north[vo_name]["token"] = token_north

        if "H" in binding_modes_north:
            from wotpy.protocols.http.server import HTTPServer

            port = int(server_bindings_north["ports"]["httpPort"])
            proxy_port = None
            if "httpProxyPort" in server_bindings_north["ports"]:
                proxy_port = int(server_bindings_north["ports"]["httpProxyPort"])

            ssl_context = None

            if server_bindings_north["serverCert"] is not None and\
                    server_bindings_north["serverKey"] is not None:
                certfile = server_bindings_north["serverCert"]
                keyfile = server_bindings_north["serverKey"]

                ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                ssl_context.load_cert_chain(certfile=certfile, keyfile=keyfile)

            servers.append(HTTPServer(
                port=port, security_scheme=security_scheme,
                ssl_context=ssl_context, form_port=proxy_port,
                externalCertificate=server_bindings_north["externalCertificate"]
            ))

        if "U" in binding_modes_north:
            from wotpy.protocols.coap.server import CoAPServer

            port = int(server_bindings_north["ports"]["coapPort"])

            oscore_credentials_map_north = None
            if server_bindings_north["OSCORECredentialsMap"] is not None:
                oscore_credentials_map_north = server_bindings_north["OSCORECredentialsMap"]

            servers.append(CoAPServer(
                port=port,
                security_scheme=security_scheme,
                oscore_credentials_map=oscore_credentials_map_north))

        if "M" in binding_modes_north:
            from wotpy.protocols.mqtt.server import MQTTServer

            broker_url = server_bindings_north["brokerIP"]

            mqtt_ca_file_north = None
            if server_bindings_north["mqttCAFile"] is not None:
                mqtt_ca_file_north = server_bindings_north["mqttCAFile"]

            servers.append(MQTTServer(broker_url, ca_file=mqtt_ca_file_north, username=username_north, password=password_north))

        if "WS" in binding_modes_north:
            from wotpy.protocols.ws.server import WebsocketServer

            port = int(server_bindings_north["ports"]["websocketPort"])

            ssl_context = None
            if server_bindings_north["serverCert"] is not None and\
                    server_bindings_north["serverKey"] is not None:
                certfile = server_bindings_north["serverCert"]
                keyfile = server_bindings_north["serverKey"]

                ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                ssl_context.load_cert_chain(certfile=certfile, keyfile=keyfile)

            servers.append(WebsocketServer(
                port=port, ssl_context=ssl_context
            ))

        if "Z" in binding_modes_north:
            from wotpy.protocols.zenoh.server import ZenohServer

            router_url = server_bindings_north["routerURL"]

            servers.append(ZenohServer(router_url))

        if "RTSP" in binding_modes_north:
            from wotpy.protocols.rtsp.server import RTSPServer

            port = int(server_bindings_north["ports"]["rtspPort"])

            if "proxy" in self.config and "videoProperty" in self.config["proxy"]:
                video_property_source_url = self.config["proxy"]["videoProperty"]

                servers.append(
                    RTSPServer(source_url=video_property_source_url, port=port)
                )

        catalogue_port = int(self.config["catalogue"])
        server_bindings_south = self.config["bindingSB"]
        binding_modes_south = server_bindings_south["bindingModeSB"]\
            if server_bindings_south["bindingModeSB"] is not None else []

        security_south = server_bindings_south["securitySB"]
        security_south_http = security_south["securitySBHTTP"]
        security_south_mqtt = security_south["securitySBMQTT"]
        security_south_coap = security_south["securitySBCOAP"]

        clients = []
        if "H" in binding_modes_south:
            from wotpy.protocols.http.client import HTTPClient

            http_client = HTTPClient()
            credentials_dict_south = {}
            security_scheme_dict = {
                "scheme": security_south_http["securityScheme"]
            }

            if security_south_http["securityScheme"] == "basic":
                credentials_dict_south["username"] = security_south_http["username"]
                credentials_dict_south["password"] = security_south_http["password"]
            elif security_south_http["securityScheme"] == "bearer":
                credentials_dict_south["token"] = security_south_http["token"]
            elif security_south_http["securityScheme"] == "oidc4vp":
                credentials_dict_south["holder_url"] = security_south_http["holderUrl"]
                credentials_dict_south["requester"] = security_south_http["requester"]

            http_client.set_security(security_scheme_dict, credentials_dict_south)
            clients.append(http_client)

        if "U" in binding_modes_south:
            from wotpy.protocols.coap.client import CoAPClient

            oscore_credentials_map_south = None
            if server_bindings_south["OSCORECredentialsMap"] is not None:
                oscore_credentials_map_south = server_bindings_south["OSCORECredentialsMap"]
            coap_client = CoAPClient(credentials=oscore_credentials_map_south)

            credentials_dict_south = {}
            security_scheme_dict = {
                "scheme": security_south_coap["securityScheme"]
            }

            if security_south_coap["securityScheme"] == "basic":
                credentials_dict_south["username"] = security_south_coap["username"]
                credentials_dict_south["password"] = security_south_coap["password"]
            elif security_south_coap["securityScheme"] == "bearer":
                credentials_dict_south["token"] = security_south_coap["token"]

            coap_client.set_security(security_scheme_dict, credentials_dict_south)
            clients.append(coap_client)

        if "M" in binding_modes_south:
            from wotpy.protocols.mqtt.client import MQTTClient

            mqtt_ca_file_south = username_south = password_south = None
            if security_south_mqtt["securityScheme"] == "basic":
                username_south = security_south_mqtt["username"]
                password_south = security_south_mqtt["password"]
            if server_bindings_south["mqttCAFile"] is not None:
                mqtt_ca_file_south = server_bindings_south["mqttCAFile"]

            clients.append(MQTTClient(ca_file=mqtt_ca_file_south, username=username_south, password=password_south))

        if "WS" in binding_modes_south:
            from wotpy.protocols.ws.client import WebsocketClient

            ws_client = WebsocketClient()
            clients.append(ws_client)

        if "Z" in binding_modes_south:
            from wotpy.protocols.zenoh.client import ZenohClient

            clients.append(ZenohClient())

        database_config = self.config["databaseConfig"]

        timeseries_db = database_config["timeseriesDB"]
        influxdb_enabled = (timeseries_db["influxDB"] == "enabled")
        influxdb_url = timeseries_db["address"]
        influxdb_token = timeseries_db["dbToken"]

        persistent_db = database_config["persistentDB"]
        sqlite_enabled = (persistent_db["SQLite"] == "enabled")
        sqlite_db_path = persistent_db["dbFilePath"]

        self._logr.info("Creating servient with TD catalogue on: %s", catalogue_port)
        super().__init__(hostname=hostname, clients=clients, catalogue_port=catalogue_port,
            influxdb_enabled=influxdb_enabled, influxdb_token=influxdb_token,
            influxdb_url=influxdb_url, sqlite_db_path=sqlite_db_path)

        for server in servers:
            self.add_server(server)

        self.add_credentials(credentials_dict_north)
