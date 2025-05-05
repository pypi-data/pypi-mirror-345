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


class PublicForwardStory(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pylogram.raw.base.PublicForward`.

    Details:
        - Layer: ``181``
        - ID: ``EDF3ADD0``

    Parameters:
        peer (:obj:`Peer <pylogram.raw.base.Peer>`):
            N/A

        story (:obj:`StoryItem <pylogram.raw.base.StoryItem>`):
            N/A

    """

    __slots__: List[str] = ["peer", "story"]

    ID = 0xedf3add0
    QUALNAME = "types.PublicForwardStory"

    def __init__(self, *, peer: "raw.base.Peer", story: "raw.base.StoryItem") -> None:
        self.peer = peer  # Peer
        self.story = story  # StoryItem

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "PublicForwardStory":
        # No flags
        
        peer = TLObject.read(b)
        
        story = TLObject.read(b)
        
        return PublicForwardStory(peer=peer, story=story)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.peer.write())
        
        b.write(self.story.write())
        
        return b.getvalue()
