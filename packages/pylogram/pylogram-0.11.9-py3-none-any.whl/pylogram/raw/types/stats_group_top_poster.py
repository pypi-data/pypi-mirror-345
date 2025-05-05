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


class StatsGroupTopPoster(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pylogram.raw.base.StatsGroupTopPoster`.

    Details:
        - Layer: ``181``
        - ID: ``9D04AF9B``

    Parameters:
        user_id (``int`` ``64-bit``):
            N/A

        messages (``int`` ``32-bit``):
            N/A

        avg_chars (``int`` ``32-bit``):
            N/A

    """

    __slots__: List[str] = ["user_id", "messages", "avg_chars"]

    ID = 0x9d04af9b
    QUALNAME = "types.StatsGroupTopPoster"

    def __init__(self, *, user_id: int, messages: int, avg_chars: int) -> None:
        self.user_id = user_id  # long
        self.messages = messages  # int
        self.avg_chars = avg_chars  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "StatsGroupTopPoster":
        # No flags
        
        user_id = Long.read(b)
        
        messages = Int.read(b)
        
        avg_chars = Int.read(b)
        
        return StatsGroupTopPoster(user_id=user_id, messages=messages, avg_chars=avg_chars)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.user_id))
        
        b.write(Int(self.messages))
        
        b.write(Int(self.avg_chars))
        
        return b.getvalue()
