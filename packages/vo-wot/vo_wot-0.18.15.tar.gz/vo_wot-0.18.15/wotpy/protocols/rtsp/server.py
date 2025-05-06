#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Class that implements the RTSP server.
"""

import logging
import subprocess

from wotpy.protocols.enums import InteractionVerbs, Protocols
from wotpy.protocols.rtsp.enums import RTSPSchemes
from wotpy.protocols.server import BaseProtocolServer
from wotpy.wot.enums import InteractionTypes
from wotpy.codecs.enums import MediaTypes
from wotpy.wot.form import Form


class RTSPServer(BaseProtocolServer):
    """RTSP binding server implementation."""

    DEFAULT_PORT = 8554

    def __init__(self, source_url, port=DEFAULT_PORT, form_port=None):
        super().__init__(port=port, form_port=form_port)
        self._source_url = source_url
        self._scheme = RTSPSchemes.RTSP
        self._logr = logging.getLogger(__name__)

    @property
    def protocol(self):
        """Protocol of this server instance.
        A member of the Protocols enum."""

        return Protocols.RTSP

    @property
    def scheme(self):
        """Returns the URL scheme for this server."""

        return self._scheme

    def _build_forms_property(self, proprty, hostname):
        """Builds and returns the RTSP Form instance for the video Property."""

        href_read = "{}://{}:{}/property/video".format(
            RTSPSchemes.RTSP, hostname.rstrip("/").lstrip("/"), self.form_port)

        form_read = Form(
            interaction=proprty,
            protocol=Protocols.RTSP,
            href=href_read,
            content_type=MediaTypes.H264,
            op=[InteractionVerbs.READ_PROPERTY])

        return [form_read]

    def build_forms(self, hostname, interaction):
        """Builds and returns a list with all Forms that are
        linked to this server for the given Interaction."""

        if interaction.interaction_type == InteractionTypes.PROPERTY \
                and interaction.name == "video":
            return self._build_forms_property(interaction, hostname)
        else:
            return []

    def build_base_url(self, hostname, thing):
        """Returns the base URL for the given Thing in the context of this server."""

        if not self.exposed_thing_set.find_by_thing_name(thing.title):
            raise ValueError("Unknown Thing")

        return "{}://{}:{}/".format(
            self.scheme, hostname.rstrip("/").lstrip("/"),
            self.form_port)

    async def start(self, servient=None):
        """Forwards the stream to the RTSP server."""

        self._servient = servient

        target_url = f"{self.scheme}://localhost:{self.port}/property/video"
        args = [
            "/usr/bin/ffmpeg",
            "-rtsp_transport", "tcp",
            "-i", self._source_url,
            "-rtsp_transport", "tcp",
            "-c:v", "copy",
            "-f", "rtsp", target_url
        ]
        self._ffmpeg_process = subprocess.Popen(args)

        self._logr.info("Sending RTSP stream from: {} to: {}".format(self.port, self._source_url))

    async def stop(self):
        """Stops the RTSP server."""

        self._ffmpeg_process.kill()
