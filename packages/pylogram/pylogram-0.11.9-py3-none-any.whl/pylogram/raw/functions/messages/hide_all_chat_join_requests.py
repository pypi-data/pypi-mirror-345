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


class HideAllChatJoinRequests(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``181``
        - ID: ``E085F4EA``

    Parameters:
        peer (:obj:`InputPeer <pylogram.raw.base.InputPeer>`):
            N/A

        approved (``bool``, *optional*):
            N/A

        link (``str``, *optional*):
            N/A

    Returns:
        :obj:`Updates <pylogram.raw.base.Updates>`
    """

    __slots__: List[str] = ["peer", "approved", "link"]

    ID = 0xe085f4ea
    QUALNAME = "functions.messages.HideAllChatJoinRequests"

    def __init__(self, *, peer: "raw.base.InputPeer", approved: Optional[bool] = None, link: Optional[str] = None) -> None:
        self.peer = peer  # InputPeer
        self.approved = approved  # flags.0?true
        self.link = link  # flags.1?string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "HideAllChatJoinRequests":
        
        flags = Int.read(b)
        
        approved = True if flags & (1 << 0) else False
        peer = TLObject.read(b)
        
        link = String.read(b) if flags & (1 << 1) else None
        return HideAllChatJoinRequests(peer=peer, approved=approved, link=link)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.approved else 0
        flags |= (1 << 1) if self.link is not None else 0
        b.write(Int(flags))
        
        b.write(self.peer.write())
        
        if self.link is not None:
            b.write(String(self.link))
        
        return b.getvalue()
