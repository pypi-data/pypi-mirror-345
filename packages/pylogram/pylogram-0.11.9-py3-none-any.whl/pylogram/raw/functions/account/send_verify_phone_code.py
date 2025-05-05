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


class SendVerifyPhoneCode(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``181``
        - ID: ``A5A356F9``

    Parameters:
        phone_number (``str``):
            N/A

        settings (:obj:`CodeSettings <pylogram.raw.base.CodeSettings>`):
            N/A

    Returns:
        :obj:`auth.SentCode <pylogram.raw.base.auth.SentCode>`
    """

    __slots__: List[str] = ["phone_number", "settings"]

    ID = 0xa5a356f9
    QUALNAME = "functions.account.SendVerifyPhoneCode"

    def __init__(self, *, phone_number: str, settings: "raw.base.CodeSettings") -> None:
        self.phone_number = phone_number  # string
        self.settings = settings  # CodeSettings

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SendVerifyPhoneCode":
        # No flags
        
        phone_number = String.read(b)
        
        settings = TLObject.read(b)
        
        return SendVerifyPhoneCode(phone_number=phone_number, settings=settings)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.phone_number))
        
        b.write(self.settings.write())
        
        return b.getvalue()
