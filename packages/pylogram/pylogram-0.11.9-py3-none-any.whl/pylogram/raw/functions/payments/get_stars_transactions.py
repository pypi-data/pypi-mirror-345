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


class GetStarsTransactions(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``181``
        - ID: ``673AC2F9``

    Parameters:
        peer (:obj:`InputPeer <pylogram.raw.base.InputPeer>`):
            N/A

        offset (``str``):
            N/A

        inbound (``bool``, *optional*):
            N/A

        outbound (``bool``, *optional*):
            N/A

    Returns:
        :obj:`payments.StarsStatus <pylogram.raw.base.payments.StarsStatus>`
    """

    __slots__: List[str] = ["peer", "offset", "inbound", "outbound"]

    ID = 0x673ac2f9
    QUALNAME = "functions.payments.GetStarsTransactions"

    def __init__(self, *, peer: "raw.base.InputPeer", offset: str, inbound: Optional[bool] = None, outbound: Optional[bool] = None) -> None:
        self.peer = peer  # InputPeer
        self.offset = offset  # string
        self.inbound = inbound  # flags.0?true
        self.outbound = outbound  # flags.1?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GetStarsTransactions":
        
        flags = Int.read(b)
        
        inbound = True if flags & (1 << 0) else False
        outbound = True if flags & (1 << 1) else False
        peer = TLObject.read(b)
        
        offset = String.read(b)
        
        return GetStarsTransactions(peer=peer, offset=offset, inbound=inbound, outbound=outbound)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.inbound else 0
        flags |= (1 << 1) if self.outbound else 0
        b.write(Int(flags))
        
        b.write(self.peer.write())
        
        b.write(String(self.offset))
        
        return b.getvalue()
