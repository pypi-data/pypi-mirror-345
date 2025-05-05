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


class GetGroupParticipants(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``181``
        - ID: ``C558D8AB``

    Parameters:
        call (:obj:`InputGroupCall <pylogram.raw.base.InputGroupCall>`):
            N/A

        ids (List of :obj:`InputPeer <pylogram.raw.base.InputPeer>`):
            N/A

        sources (List of ``int`` ``32-bit``):
            N/A

        offset (``str``):
            N/A

        limit (``int`` ``32-bit``):
            N/A

    Returns:
        :obj:`phone.GroupParticipants <pylogram.raw.base.phone.GroupParticipants>`
    """

    __slots__: List[str] = ["call", "ids", "sources", "offset", "limit"]

    ID = 0xc558d8ab
    QUALNAME = "functions.phone.GetGroupParticipants"

    def __init__(self, *, call: "raw.base.InputGroupCall", ids: List["raw.base.InputPeer"], sources: List[int], offset: str, limit: int) -> None:
        self.call = call  # InputGroupCall
        self.ids = ids  # Vector<InputPeer>
        self.sources = sources  # Vector<int>
        self.offset = offset  # string
        self.limit = limit  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GetGroupParticipants":
        # No flags
        
        call = TLObject.read(b)
        
        ids = TLObject.read(b)
        
        sources = TLObject.read(b, Int)
        
        offset = String.read(b)
        
        limit = Int.read(b)
        
        return GetGroupParticipants(call=call, ids=ids, sources=sources, offset=offset, limit=limit)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.call.write())
        
        b.write(Vector(self.ids))
        
        b.write(Vector(self.sources, Int))
        
        b.write(String(self.offset))
        
        b.write(Int(self.limit))
        
        return b.getvalue()
