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


class UpdateBusinessIntro(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``181``
        - ID: ``A614D034``

    Parameters:
        intro (:obj:`InputBusinessIntro <pylogram.raw.base.InputBusinessIntro>`, *optional*):
            N/A

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["intro"]

    ID = 0xa614d034
    QUALNAME = "functions.account.UpdateBusinessIntro"

    def __init__(self, *, intro: "raw.base.InputBusinessIntro" = None) -> None:
        self.intro = intro  # flags.0?InputBusinessIntro

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdateBusinessIntro":
        
        flags = Int.read(b)
        
        intro = TLObject.read(b) if flags & (1 << 0) else None
        
        return UpdateBusinessIntro(intro=intro)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.intro is not None else 0
        b.write(Int(flags))
        
        if self.intro is not None:
            b.write(self.intro.write())
        
        return b.getvalue()
