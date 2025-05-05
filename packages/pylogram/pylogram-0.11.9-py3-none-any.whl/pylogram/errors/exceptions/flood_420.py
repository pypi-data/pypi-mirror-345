# Pylogram - Telegram MTProto API Client Library for Python
# Copyright (C) 2017-2023 Dan <https://github.com/delivrance>
# Copyright (C) 2023-2024 Pylakey <https://github.com/pylakey>
#
# This file is part of Pylogram.
#
# Pylogram is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pylogram is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Pylogram.  If not, see <http://www.gnu.org/licenses/>.

from ..rpc_error import RPCError


class Flood(RPCError):
    """Flood"""
    CODE = 420
    """``int``: RPC Error Code"""
    NAME = __doc__


class TwoFaConfirmWait(Flood):
    """A wait of {value} seconds is required because this account is active and protected by a 2FA password"""
    ID = "2FA_CONFIRM_WAIT_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FloodTestPhoneWait(Flood):
    """A wait of {value} seconds is required in the test servers"""
    ID = "FLOOD_TEST_PHONE_WAIT_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FloodWait(Flood):
    """A wait of {value} seconds is required"""
    ID = "FLOOD_WAIT_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class SlowmodeWait(Flood):
    """A wait of {value} seconds is required to send messages in this chat."""
    ID = "SLOWMODE_WAIT_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TakeoutInitDelay(Flood):
    """You have to confirm the data export request using one of your mobile devices or wait {value} seconds"""
    ID = "TAKEOUT_INIT_DELAY_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FrozenMethodInvalid(Flood):
    """You have to confirm the data export request using one of your mobile devices or wait {value} seconds"""
    ID = "FROZEN_METHOD_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


