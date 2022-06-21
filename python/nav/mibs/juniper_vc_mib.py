#
# Copyright (C) 2022 Sikt
#
# This file is part of Network Administration Visualized (NAV).
#
# NAV is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.  You should have received a copy of the GNU General Public
# License along with NAV. If not, see <http://www.gnu.org/licenses/>.
#
from dataclasses import dataclass

from twisted.internet import defer

from nav.mibs import mibretriever, reduce_index
from nav.smidumps import get_mib
from nav.macaddress import MacAddress


class JuniperVCMib(mibretriever.MibRetriever):
    """MibRetriever for the JUNIPER-VIRTUALCHASSIS-MIB"""

    mib = get_mib("JUNIPER-VIRTUALCHASSIS-MIB")

    @defer.inlineCallbacks
    def get_virtual_chassis_members(self):
        """Retrieves a list of virtual chassis members, if any.

        :returns: A Deferred whose result is a list of VirtualChassisMember instances.
        """
        table = (
            yield self.retrieve_table("jnxVirtualChassisMemberTable")
            .addCallback(reduce_index)
            .addCallback(self.translate_result)
        )
        members = [
            VirtualChassisMember(
                id=index,
                serial_number=row.get("jnxVirtualChassisMemberSerialnumber"),
                role=row.get("jnxVirtualChassisMemberRole"),
                mac_address_base=MacAddress.from_octets(
                    row.get("jnxVirtualChassisMemberMacAddBase")
                )
                if row.get("jnxVirtualChassisMemberMacAddBase")
                else None,
                sw_version=row.get("jnxVirtualChassisMemberSWVersion"),
                priority=row.get("jnxVirtualChassisMemberPriority"),
                uptime=row.get("jnxVirtualChassisMemberUptime"),
                model=row.get("jnxVirtualChassisMemberModel"),
                location=row.get("jnxVirtualChassisMemberLocation"),
                alias=row.get("jnxVirtualChassisMemberAlias"),
                fabric_mode=row.get("jnxVirtualChassisMemberFabricMode"),
                mixed_mode=row.get("jnxVirtualChassisMemberMixedMode"),
            )
            for index, row in table.items()
        ]
        defer.returnValue(members)


@dataclass
class VirtualChassisMember:
    """Describes a member of a Juniper Virtual Chassis"""

    id: int
    serial_number: str
    role: str
    mac_address_base: str
    sw_version: str
    priority: int
    uptime: int
    model: str
    location: str
    alias: str
    fabric_mode: str
    mixed_mode: str
