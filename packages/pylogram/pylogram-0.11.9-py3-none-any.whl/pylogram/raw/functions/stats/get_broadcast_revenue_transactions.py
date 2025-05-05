#  Pylogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-2023 Dan <https://github.com/delivrance>
#  Copyright (C) 2023-2024 Pylakey <https://github.com/pylakey>
#
#  This file is part of Pylogram.
#
#  Pylogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pylogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pylogram.  If not, see <http://www.gnu.org/licenses/>.

from io import BytesIO

from pylogram.raw.core.primitives import Int, Long, Int128, Int256, Bool, Bytes, String, Double, Vector
from pylogram.raw.core import TLObject
from pylogram import raw
from typing import List, Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


class GetBroadcastRevenueTransactions(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``181``
        - ID: ``69280F``

    Parameters:
        channel (:obj:`InputChannel <pylogram.raw.base.InputChannel>`):
            N/A

        offset (``int`` ``32-bit``):
            N/A

        limit (``int`` ``32-bit``):
            N/A

    Returns:
        :obj:`stats.BroadcastRevenueTransactions <pylogram.raw.base.stats.BroadcastRevenueTransactions>`
    """

    __slots__: List[str] = ["channel", "offset", "limit"]

    ID = 0x69280f
    QUALNAME = "functions.stats.GetBroadcastRevenueTransactions"

    def __init__(self, *, channel: "raw.base.InputChannel", offset: int, limit: int) -> None:
        self.channel = channel  # InputChannel
        self.offset = offset  # int
        self.limit = limit  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GetBroadcastRevenueTransactions":
        # No flags
        
        channel = TLObject.read(b)
        
        offset = Int.read(b)
        
        limit = Int.read(b)
        
        return GetBroadcastRevenueTransactions(channel=channel, offset=offset, limit=limit)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.channel.write())
        
        b.write(Int(self.offset))
        
        b.write(Int(self.limit))
        
        return b.getvalue()
