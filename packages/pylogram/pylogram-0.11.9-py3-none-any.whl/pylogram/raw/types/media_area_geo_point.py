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


class MediaAreaGeoPoint(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pylogram.raw.base.MediaArea`.

    Details:
        - Layer: ``181``
        - ID: ``DF8B3B22``

    Parameters:
        coordinates (:obj:`MediaAreaCoordinates <pylogram.raw.base.MediaAreaCoordinates>`):
            N/A

        geo (:obj:`GeoPoint <pylogram.raw.base.GeoPoint>`):
            N/A

    """

    __slots__: List[str] = ["coordinates", "geo"]

    ID = 0xdf8b3b22
    QUALNAME = "types.MediaAreaGeoPoint"

    def __init__(self, *, coordinates: "raw.base.MediaAreaCoordinates", geo: "raw.base.GeoPoint") -> None:
        self.coordinates = coordinates  # MediaAreaCoordinates
        self.geo = geo  # GeoPoint

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "MediaAreaGeoPoint":
        # No flags
        
        coordinates = TLObject.read(b)
        
        geo = TLObject.read(b)
        
        return MediaAreaGeoPoint(coordinates=coordinates, geo=geo)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.coordinates.write())
        
        b.write(self.geo.write())
        
        return b.getvalue()
