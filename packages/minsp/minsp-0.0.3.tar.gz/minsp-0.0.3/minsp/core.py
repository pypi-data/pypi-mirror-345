"""
The `minsp.core` module provides the package core functions and classes.
"""

from dataclasses import dataclass
from enum import Enum
import struct

from .pus import PUSHeader
from .mo import MALHeader

class PacketType(int, Enum):
    """
    Enum to represent a space packet type: telemetry (TM) or telecommand (TC).

    Attributes:
        TM = 0
        TC = 1
    """
    TM = 0b0
    TC = 0b1

@dataclass
class SpacePacket:
    """
    Represents a CCSDS Space Packet (including primary header, optional secondary
    header, and data field).

    According to the CCSDS standard:
    * The primary header is 6 bytes long and contains version, packet type, APID,
    sequence info, and length.
    * The secondary header can be an custom stream of bytes, and instance of `PUSheader`
    or an instance of `MALHeader`.
    * The data length field (data_length) defines the number of bytes after the primary
    header minus one.
    * This class allows serialization to and from byte streams.

    :param version: Packet version, default is `0` (3 bits).
    :type version: int
    :param type: Packet type, default is `PacketType.TM` (1 bit).
    :type type: PacketType
    :param secondary_header_flag: Secondary header flag, default is `0` (1 bit).
    :type secondary_header_flag: int
    :param apid: Application process identifier, default is `0` (11 bits).
    :type apid: int
    :param sequence_flags: Sequence flags, default is `0b11` (2 bits).
    :type sequence_flags: int
    :param sequence_count: Sequence count, default is `0` (14 bits).
    :type sequence_count: int
    :param data_length: Packet data field length of the data following
    the primary header minus one, defaults is `0` (16 bits).
    :param secondary_header: Secondary header.
    :type secondary_header: bytes|`PUSHeader`|`MALHeader`
    :param data_field: Packet data.
    :type data_field: bytes
    """
    version: int = 0
    type: PacketType = PacketType.TM
    secondary_header_flag: int = 0
    apid: int = 0
    sequence_flags: int = 0b11
    sequence_count: int = 0
    data_length: int = 0

    secondary_header: bytes|PUSHeader|MALHeader = b''
    data_field: bytes = b''

    def __post_init__(self):

        # update data length
        size = 0
        if isinstance(self.secondary_header, (PUSHeader, MALHeader)):
            size += len(self.secondary_header.as_bytes())
        else:
            size += len(self.secondary_header)

        self.data_length = size + len(self.data_field) - 1

        # update secondary header flag
        if self.secondary_header:
            self.secondary_header_flag = 1

    def as_bytes(self) -> bytes:
        """
        Packs the space packet into a byte stream, including:
        - Primary header (6 bytes)
        - Optional secondary header
        - Data field

        :return: Space packet bytes.
        :rtype: bytes
        """
        if isinstance(self.secondary_header, bytes):
            sec_hdr = self.secondary_header
        elif isinstance(self.secondary_header, PUSHeader):
            sec_hdr = self.secondary_header.as_bytes()
        elif isinstance(self.secondary_header, MALHeader):
            sec_hdr = self.secondary_header.as_bytes()
        else:
            sec_hdr = b''

        payload = sec_hdr + self.data_field
        self.data_length = len(payload) - 1
        if self.data_length <= 0:
            raise ValueError("Can't generate packet as bytes, data length is 0 or negative.")

        first_word = ((self.version & 0x07) << 13) | \
                     ((self.type & 0x01) << 12) | \
                     ((self.secondary_header_flag & 0x01) << 11) | \
                     (self.apid & 0x07FF)
        second_word = ((self.sequence_flags & 0x03) << 14) | (self.sequence_count & 0x3FFF)

        header = struct.pack(">HHH", first_word, second_word, self.data_length)

        return header + payload


    # pylint: disable=R0914,R1720
    @classmethod
    def from_bytes(cls, data: bytes, secondary_header_length: int = 0, \
        pus: bool = False, mal: bool = False) -> "SpacePacket":
        """
        Unpacks a byte stream into a `SpacePacket` instance.

        :param data: The byte stream.
        :type data: bytes
        :param secondary_header_length: Secondary header length if present, default is `0`.
        :type secondary_header_length: int
        :param pus: Secondary header is a PUS header.
        :type pus: bool
        :param pus: Secondary header is a MAL header.
        :type pus: bool

        :raises ValueError: Insufficient data for space packet primary header.
        :raises ValueError: Secondary header flag bit is set to 1, but secondary header length is 0.

        :return: A new `SpacePacket`.
        :rtype: SpacePacket
        """
        if len(data) < 6:
            raise ValueError("Insufficient data for space packet primary header.")

        first_word, second_word, pkt_length = struct.unpack(">HHH", data[:6])

        version = (first_word >> 13) & 0x07
        pkt_type = (first_word >> 12) & 0x01
        sec_hdr_flag = (first_word >> 11) & 0x01
        apid = first_word & 0x07FF
        seq_flags = (second_word >> 14) & 0x03
        seq_count = second_word & 0x3FFF

        if sec_hdr_flag == 1:
            if pus:
                sec_hdr = PUSHeader.from_bytes(data[6:])
                data_field = data[6+len(sec_hdr.as_bytes()):]
            elif mal:
                sec_hdr = MALHeader.from_bytes(data[6:])
                data_field =data[6+len(sec_hdr.as_bytes()):]
            else:
                if secondary_header_length == 0:
                    raise ValueError("Secondary header flag bit is set to 1, \
                                     but secondary header length is 0.")
                else:
                    sec_hdr = data[6:6+secondary_header_length]
                    data_field = data[6+secondary_header_length:]
        else:
            sec_hdr = b''
            data_field = data[6:]

        return cls(
            version=version,
            type=pkt_type,
            secondary_header_flag=sec_hdr_flag,
            apid=apid,
            sequence_flags=seq_flags,
            sequence_count=seq_count,
            secondary_header=sec_hdr,
            data_length=pkt_length,
            data_field=data_field
        )
