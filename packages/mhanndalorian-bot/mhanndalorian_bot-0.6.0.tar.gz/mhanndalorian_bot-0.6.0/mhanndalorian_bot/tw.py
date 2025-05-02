# coding=utf-8
"""
Data objects and methods for Territory War
"""
from __future__ import annotations

from typing import Optional
import logging

from api import API
from api import EndPoint
from globals import *

logger = logging.getLogger(__name__)


class ZoneMap:
    """
    Data object to represent the zone map for Territory War

    Args:
        zone_map (dict, optional): A dictionary containing the mapping of zone IDs to zone names.
                                    Defaults to a default mapping in the form of:

                                               (phase, zone) = name

                                                ('01', '01'): "T1"
                                                ('01', '02'): "B1"
                                                ('02', '01'): "T2"
                                                ('02', '02'): "B2"
                                                ('03', '01'): "T3"
                                                ('03', '02'): "M1"
                                                ('03', '03'): "B3"
                                                ('04', '01'): "T4"
                                                ('04', '02'): "M2"
                                                ('04', '03'): "B4"

    """

    # (phase, zone) = name
    DEFAULT_MAP = {
            ('01', '01'): "T1",
            ('01', '02'): "B1",
            ('02', '01'): "T2",
            ('02', '02'): "B2",
            ('03', '01'): "T3",
            ('03', '02'): "M1",
            ('03', '03'): "B3",
            ('04', '01'): "T4",
            ('04', '02'): "M2",
            ('04', '03'): "B4"
            }

    def __init__(self, zone_map: Optional[dict] = None):
        if zone_map is None:
            zone_map = self.DEFAULT_MAP
        self.zone_map = zone_map

    def get_zone_name(self, zone_id: tuple[str, str]) -> str:
        """
        Retrieves the name of a zone based on the given zone ID.

        This method tries to fetch the zone name from the internal `zone_map` dictionary
        using the provided zone ID. If the zone ID does not exist in the map, it returns
        "N/A" as the default value.

        Args:
            zone_id (tuple[str, str]): A tuple representing the zone ID, where the tuple
                contains identifiers corresponding to the zone.

        Returns:
            str: The name of the zone corresponding to the given zone ID, or "N/A" if
            the zone ID is not found in the `zone_map`.
        """
        return self.zone_map.get(zone_id, "N/A")

    def set_zone_name(self, zone_id: tuple[str, str], zone_name: str = "N/A"):
        """
        Sets the name for a given zone identified by a unique zone_id.

        This method updates the mapping of zone identifiers to their corresponding
        names within the object. If not provided, the name defaults to "N/A".

        Args:
            zone_id (tuple[str, str]): A unique identifier for the zone as a tuple
                of strings.
            zone_name (str, optional): The name to assign to the zone. Defaults to "N/A".
        """
        self.zone_map[zone_id] = zone_name

    @staticmethod
    def extract_zone_info_from_channel_id(channel_id: str) -> tuple[str, str]:
        """
        Extract specific zone information from a given channel ID.

        The method processes a 'channelId' string from a TW log message entry to extract
        the phase and conflict information based on the structured format of the input.
        The channel ID must be in a pre-defined format where the key fragment containing
        this information is located precisely after splitting the string and isolating
        specific segments. This function is designed to ensure proper validation and parsing
        of the input channel ID.

        Args:
            channel_id (str): The channel ID string from which phase and conflict
                information needs to be extracted.

        Returns:
            tuple[str, str]: A tuple containing the extracted phase and conflict
                information as strings.

        Raises:
            ValueError: If the provided channel_id is not of type string.
        """
        if not isinstance(channel_id, str):
            raise ValueError("Channel ID must be a string.")

        # Extract the relevant part of the channel ID
        channel_key_fragment = channel_id.split('-')[3]

        # Extract phase and conflict parts from the key fragment
        phase_info = channel_key_fragment.split('_')[2].replace('phase', '')
        conflict_info = channel_key_fragment.split('_')[3].replace('conflict', '')

        # Return cleaned phase and conflict data
        return phase_info, conflict_info


class TW:
    """
    Container class for Territory War data
    """

    members: list[str] = []

    def __init__(self, api: API, *, zone_map: Optional[dict] = None):
        self.api = api

        self.zone_map = ZoneMap(zone_map) if zone_map is not None else ZoneMap()

        tw_data = self.api.fetch_tw(enums=True)
        self.members = [m['memberId'] for m in tw_data['data']['optedInMember']]
        self.opponent_guild_id = tw_data['data']['awayGuild']['profile']['id']
        self.opponent_guild_url = f"{SWGOH_GG_BASE_URL}/{SWGOH_GG_GUILD_PATH}/{self.opponent_guild_id}/"
        self.opponent_guild_name = tw_data['data']['awayGuild']['profile']['name']

    def parse_tw_log_entry(self, log_entry: dict):
        """Dissect a TW log entry into its components"""
        ...
