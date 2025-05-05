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


class ClickSponsoredMessage(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``181``
        - ID: ``18AFBC93``

    Parameters:
        channel (:obj:`InputChannel <pylogram.raw.base.InputChannel>`):
            N/A

        random_id (``bytes``):
            N/A

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["channel", "random_id"]

    ID = 0x18afbc93
    QUALNAME = "functions.channels.ClickSponsoredMessage"

    def __init__(self, *, channel: "raw.base.InputChannel", random_id: bytes) -> None:
        self.channel = channel  # InputChannel
        self.random_id = random_id  # bytes

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ClickSponsoredMessage":
        # No flags
        
        channel = TLObject.read(b)
        
        random_id = Bytes.read(b)
        
        return ClickSponsoredMessage(channel=channel, random_id=random_id)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.channel.write())
        
        b.write(Bytes(self.random_id))
        
        return b.getvalue()
