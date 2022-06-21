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
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.  You should have received a copy of the GNU General Public License
# along with NAV. If not, see <http://www.gnu.org/licenses/>.
#
"""
ipdevpoll plugin to collect information about Juniper virtual chassis members from
JUNIPER-VIRTUALCHASSIS-MIB.
"""
from __future__ import annotations
from pprint import pformat
from typing import List

from twisted.internet import defer

from nav.enterprise.ids import VENDOR_ID_JUNIPER_NETWORKS_INC
from nav.ipdevpoll import Plugin, shadows
from nav.mibs.juniper_vc_mib import JuniperVCMib, VirtualChassisMember
from nav.models import manage
from nav.models.manage import NetboxEntity

SOURCE = JuniperVCMib.mib.get("moduleName")


class JuniperVC(Plugin):
    """Plugin to collect chassis members from a Juniper virtual chassis"""

    RESTRICT_TO_VENDORS = (VENDOR_ID_JUNIPER_NETWORKS_INC,)

    @defer.inlineCallbacks
    def handle(self):
        self._logger.debug("Collecting Juniper VC members")
        mib = JuniperVCMib(self.agent)
        members = yield mib.get_virtual_chassis_members()
        if members:
            self._logger.debug("Got members:\n%s", pformat(members))
            self._process_members(members)

    def _process_members(self, members: List[VirtualChassisMember]):
        stack = self._get_faked_stack_entity()
        for member in members:
            self._process_member(member, stack)

    def _get_faked_stack_entity(self):
        """Returns a 'fake' stack entity to which stack members can be attached.
        Although the concept comes from the ENTITY-MIB, parts of NAV require this
        parent entity to be present to properly process stack member chassis.
        """
        netbox = self.containers.factory(None, shadows.Netbox)
        stack_key = "{}:VC".format(SOURCE)
        return self.containers.factory(
            stack_key,
            shadows.NetboxEntity,
            netbox=netbox,
            index=-1,
            source=SOURCE,
            physical_class=NetboxEntity.CLASS_STACK,
            descr="Juniper Virtual Chassis Stack",
        )

    def _process_member(
        self, member: VirtualChassisMember, stack: shadows.NetboxEntity
    ):
        """Processes an individual stack member into data containers for db storage"""
        device: shadows.Device = self.containers.factory(
            member.serial_number, shadows.Device
        )
        device.active = True
        device.serial = member.serial_number
        device.software_revision = member.sw_version

        netbox = self.containers.factory(None, shadows.Netbox)

        key = "{}:{}".format(SOURCE, member.id)
        entity: shadows.NetboxEntity = self.containers.factory(
            key, shadows.NetboxEntity
        )
        entity.source = SOURCE
        entity.netbox = netbox
        entity.device = device
        entity.index = member.id
        entity.name = member.id
        entity.descr = member.alias or f"VC member {member.id}"
        entity.physical_class = manage.NetboxEntity.CLASS_CHASSIS
        entity.model_name = member.model
        entity.software_revision = member.sw_version
        entity.contained_in = stack
        entity.data = {
            "role": member.role,
            "fabric_mode": member.fabric_mode,
            "mixed_mode": member.mixed_mode,
            "priority": member.priority,
            "location": member.location,
            "mac_address_base": str(member.mac_address_base),
        }

        return entity
