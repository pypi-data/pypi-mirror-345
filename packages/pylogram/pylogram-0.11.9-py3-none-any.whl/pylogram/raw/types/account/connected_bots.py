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


class ConnectedBots(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pylogram.raw.base.account.ConnectedBots`.

    Details:
        - Layer: ``181``
        - ID: ``17D7F87B``

    Parameters:
        connected_bots (List of :obj:`ConnectedBot <pylogram.raw.base.ConnectedBot>`):
            N/A

        users (List of :obj:`User <pylogram.raw.base.User>`):
            N/A

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: pylogram.raw.functions

        .. autosummary::
            :nosignatures:

            account.GetConnectedBots
    """

    __slots__: List[str] = ["connected_bots", "users"]

    ID = 0x17d7f87b
    QUALNAME = "types.account.ConnectedBots"

    def __init__(self, *, connected_bots: List["raw.base.ConnectedBot"], users: List["raw.base.User"]) -> None:
        self.connected_bots = connected_bots  # Vector<ConnectedBot>
        self.users = users  # Vector<User>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ConnectedBots":
        # No flags
        
        connected_bots = TLObject.read(b)
        
        users = TLObject.read(b)
        
        return ConnectedBots(connected_bots=connected_bots, users=users)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Vector(self.connected_bots))
        
        b.write(Vector(self.users))
        
        return b.getvalue()
