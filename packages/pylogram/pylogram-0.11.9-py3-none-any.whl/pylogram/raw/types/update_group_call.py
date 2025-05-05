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


class UpdateGroupCall(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pylogram.raw.base.Update`.

    Details:
        - Layer: ``181``
        - ID: ``14B24500``

    Parameters:
        chat_id (``int`` ``64-bit``):
            N/A

        call (:obj:`GroupCall <pylogram.raw.base.GroupCall>`):
            N/A

    """

    __slots__: List[str] = ["chat_id", "call"]

    ID = 0x14b24500
    QUALNAME = "types.UpdateGroupCall"

    def __init__(self, *, chat_id: int, call: "raw.base.GroupCall") -> None:
        self.chat_id = chat_id  # long
        self.call = call  # GroupCall

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdateGroupCall":
        # No flags
        
        chat_id = Long.read(b)
        
        call = TLObject.read(b)
        
        return UpdateGroupCall(chat_id=chat_id, call=call)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.chat_id))
        
        b.write(self.call.write())
        
        return b.getvalue()
