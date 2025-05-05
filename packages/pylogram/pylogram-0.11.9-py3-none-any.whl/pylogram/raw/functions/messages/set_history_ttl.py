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


class SetHistoryTTL(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``181``
        - ID: ``B80E5FE4``

    Parameters:
        peer (:obj:`InputPeer <pylogram.raw.base.InputPeer>`):
            N/A

        period (``int`` ``32-bit``):
            N/A

    Returns:
        :obj:`Updates <pylogram.raw.base.Updates>`
    """

    __slots__: List[str] = ["peer", "period"]

    ID = 0xb80e5fe4
    QUALNAME = "functions.messages.SetHistoryTTL"

    def __init__(self, *, peer: "raw.base.InputPeer", period: int) -> None:
        self.peer = peer  # InputPeer
        self.period = period  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SetHistoryTTL":
        # No flags
        
        peer = TLObject.read(b)
        
        period = Int.read(b)
        
        return SetHistoryTTL(peer=peer, period=period)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.peer.write())
        
        b.write(Int(self.period))
        
        return b.getvalue()
