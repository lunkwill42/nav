#
# Copyright (C) 2020 UNINETT
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
from nav.models import manage
from nav.portadmin.config import CONFIG
from nav.portadmin.cnaas_nms.lowlevel import get_api
from nav.portadmin.handlers import ManagementHandler


class CNaaSNMSMixIn(ManagementHandler):
    """MixIn to override all write-operations from
    nav.portadmin.snmp.base.SnmpHandler and instead direct them through a CNaaS NMS
    instance's REST API.

    """

    def __init__(self, netbox: manage.Netbox, **kwargs):
        super().__init__(netbox, **kwargs)
        config = CONFIG.get_cnaas_nms_config()
        self._api = get_api(config.url, config.token)

    def set_if_alias(self, if_index, if_alias):
        iface = self._interface_name_from_index(if_index)
        data = {"description": if_alias}
        payload = {"interfaces": {iface: data}}
        self._api.interfaces.configure(self.netbox.sysname, body=payload)

    def set_if_down(self, if_index):
        self._set_interface_enabled(if_index, enabled=False)

    def set_if_up(self, if_index):
        self._set_interface_enabled(if_index, enabled=True)

    def _set_interface_enabled(self, if_index, enabled=True):
        iface = self._interface_name_from_index(if_index)
        data = {"enabled": enabled}
        payload = {"interfaces": {iface: data}}
        self._api.interfaces.configure(self.netbox.sysname, body=payload)

    def _get_device_record(self):
        response = self._api.devices.retrieve(self.netbox.ip)
        payload = response.body
        if response.status_code == 200 and payload.get("status") == "success":
            data = payload.get("data", {})
            if len(data.get("devices", [])) < 0:
                raise CNaaSNMSApiError(
                    "No devices matched {} in CNaaS-NMS".format(self.netbox.ip)
                )
            device = data["devices"][0]
            return device
        else:
            raise CNaaSNMSApiError(
                "Unknown failure when talking to CNaaS-NMS (code={}, status={})".format(
                    response.status_code, payload.get("status")
                )
            )

    def write_mem(self):
        """Implements the 'write_mem' step as a configuration commit/sync command"""
        payload = {"hostname": self.netbox.sysname, "dry_run": False, "auto_push": True}
        self._api.device_sync.syncto(body=payload)
        # TODO: Get a job number from the syncto call
        # TODO: Poll the job API for "status": "FINISHED"

    def _interface_name_from_index(self, if_index):
        """Translates an ifIndex value to an interface name for this device.

        The PortAdmin API uses ifIndex values exclusively, originally being
        SNMP-centric, wheres the CNaaS API only cares about interface names.
        """
        # TODO: Verify the assumption that CNaaS NMS uses the ifDescr value.
        ifc = self.netbox.interface_set.only("ifdescr").get(ifindex=if_index)
        return ifc.ifdescr


class CNaaSNMSApiError(Exception):
    """An exception raised whenever there is a problem with the responses from the
    CNaaS NMS API
    """

    pass
