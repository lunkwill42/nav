# python version 1.0						DO NOT EDIT
#
# Generated by smidump version 0.4.8:
#
#   smidump -f python POWERSUPPLY-MIB

FILENAME = "POWERSUPPLY-MIB.mib"

MIB = {
    "moduleName" : "POWERSUPPLY-MIB",

    "POWERSUPPLY-MIB" : {
        "nodetype" : "module",
        "language" : "SMIv2",
        "organization" :    
            """Hewitt-Packard""",
        "contact" : 
            """k-p-rama.murthy@hp.com""",
        "description" :
            """This MIB module is for representing 
switch power supply entity.""",
        "revisions" : (
            {
                "date" : "2008-08-27 10:00",
                "description" :
                    """Initial Version of Power Supply MIB, Version 1""",
            },
        ),
        "identity node" : "hpicfPsMIB",
    },

    "imports" : (
        {"module" : "SNMPv2-SMI", "name" : "MODULE-IDENTITY"},
        {"module" : "SNMPv2-SMI", "name" : "OBJECT-TYPE"},
        {"module" : "SNMPv2-SMI", "name" : "Integer32"},
        {"module" : "SNMPv2-SMI", "name" : "Unsigned32"},
        {"module" : "SNMPv2-SMI", "name" : "Counter32"},
        {"module" : "SNMPv2-CONF", "name" : "MODULE-COMPLIANCE"},
        {"module" : "SNMPv2-CONF", "name" : "OBJECT-GROUP"},
        {"module" : "SNMP-FRAMEWORK-MIB", "name" : "SnmpAdminString"},
        {"module" : "SNMPv2-TC", "name" : "TEXTUAL-CONVENTION"},
        {"module" : "HP-ICF-OID", "name" : "hpSwitch"},
    ),

    "typedefs" : {
        "HpicfDcPsIndex" : {
            "basetype" : "Unsigned32",
            "status" : "current",
            "format" : "d",
            "description" :
                """A unique value that serves as index to identify the power supply.""",
        },
        "HpicfDcPsState" : {
            "basetype" : "Enumeration",
            "status" : "current",
            "psNotPresent" : {
                "nodetype" : "namednumber",
                "number" : "1"
            },
            "psNotPlugged" : {
                "nodetype" : "namednumber",
                "number" : "2"
            },
            "psPowered" : {
                "nodetype" : "namednumber",
                "number" : "3"
            },
            "psFailed" : {
                "nodetype" : "namednumber",
                "number" : "4"
            },
            "psPermFailure" : {
                "nodetype" : "namednumber",
                "number" : "5"
            },
            "psMax" : {
                "nodetype" : "namednumber",
                "number" : "6"
            },
            "description" :
                """An enumerated value which provides the state of the 
switch power supply entity.""",
        },
    }, # typedefs

    "nodes" : {
        "hpicfPsMIB" : {
            "nodetype" : "node",
            "moduleName" : "POWERSUPPLY-MIB",
            "oid" : "1.3.6.1.4.1.11.2.14.11.5.1.55",
            "status" : "current",
        }, # node
        "hpicfEntityPs" : {
            "nodetype" : "node",
            "moduleName" : "POWERSUPPLY-MIB",
            "oid" : "1.3.6.1.4.1.11.2.14.11.5.1.55.1",
        }, # node
        "hpicfPsTable" : {
            "nodetype" : "table",
            "moduleName" : "POWERSUPPLY-MIB",
            "oid" : "1.3.6.1.4.1.11.2.14.11.5.1.55.1.1",
            "status" : "current",
            "description" :
                """This table contains one row per switch power supply entity.""",
        }, # table
        "hpicfPsEntry" : {
            "nodetype" : "row",
            "moduleName" : "POWERSUPPLY-MIB",
            "oid" : "1.3.6.1.4.1.11.2.14.11.5.1.55.1.1.1",
            "status" : "current",
            "linkage" : [
                "hpicfPsBayNum",
            ],
            "description" :
                """Information about the power supply physical entity
table.""",
        }, # row
        "hpicfPsBayNum" : {
            "nodetype" : "column",
            "moduleName" : "POWERSUPPLY-MIB",
            "oid" : "1.3.6.1.4.1.11.2.14.11.5.1.55.1.1.1.1",
            "status" : "current",
            "syntax" : {
                "type" : { "module" :"POWERSUPPLY-MIB", "name" : "HpicfDcPsIndex"},
            },
            "access" : "noaccess",
            "description" :
                """The index of switch power supply entity.""",
        }, # column
        "hpicfPsState" : {
            "nodetype" : "column",
            "moduleName" : "POWERSUPPLY-MIB",
            "oid" : "1.3.6.1.4.1.11.2.14.11.5.1.55.1.1.1.2",
            "status" : "current",
            "syntax" : {
                "type" : { "module" :"POWERSUPPLY-MIB", "name" : "HpicfDcPsState"},
            },
            "access" : "readonly",
            "description" :
                """The physial state of the switch power supply entity.""",
        }, # column
        "hpicfPsFailures" : {
            "nodetype" : "column",
            "moduleName" : "POWERSUPPLY-MIB",
            "oid" : "1.3.6.1.4.1.11.2.14.11.5.1.55.1.1.1.3",
            "status" : "current",
            "syntax" : {
                "type" : { "module" :"SNMPv2-SMI", "name" : "Counter32"},
            },
            "access" : "readonly",
            "description" :
                """Number of times power supply has failed.""",
        }, # column
        "hpicfPsTemp" : {
            "nodetype" : "column",
            "moduleName" : "POWERSUPPLY-MIB",
            "oid" : "1.3.6.1.4.1.11.2.14.11.5.1.55.1.1.1.4",
            "status" : "current",
            "syntax" : {
                "type" : { "module" :"", "name" : "Integer32"},
            },
            "access" : "readonly",
            "description" :
                """The temperature of the power supply in celsius""",
        }, # column
        "hpicfPsVoltageInfo" : {
            "nodetype" : "column",
            "moduleName" : "POWERSUPPLY-MIB",
            "oid" : "1.3.6.1.4.1.11.2.14.11.5.1.55.1.1.1.5",
            "status" : "current",
            "syntax" : {
                "type" :                 {
                    "basetype" : "OctetString",
                    "parent module" : {
                        "name" : "SNMP-FRAMEWORK-MIB",
                        "type" : "SnmpAdminString",
                    },
                    "ranges" : [
                    {
                        "min" : "0",
                        "max" : "32"
                    },
                    ],
                    "range" : {
                        "min" : "0",
                        "max" : "32"
                    },
                },
            },
            "access" : "readonly",
            "description" :
                """The voltage info and max current of power supply.
e.g. AC 120V/220V. """,
        }, # column
        "hpicfPsWattageCur" : {
            "nodetype" : "column",
            "moduleName" : "POWERSUPPLY-MIB",
            "oid" : "1.3.6.1.4.1.11.2.14.11.5.1.55.1.1.1.6",
            "status" : "current",
            "syntax" : {
                "type" : { "module" :"", "name" : "Integer32"},
            },
            "access" : "readonly",
            "description" :
                """The present power supply wattage information""",
        }, # column
        "hpicfPsWattageMax" : {
            "nodetype" : "column",
            "moduleName" : "POWERSUPPLY-MIB",
            "oid" : "1.3.6.1.4.1.11.2.14.11.5.1.55.1.1.1.7",
            "status" : "current",
            "syntax" : {
                "type" : { "module" :"", "name" : "Integer32"},
            },
            "access" : "readonly",
            "description" :
                """The maximum wattage of the power supply.""",
        }, # column
        "hpicfPsLastCall" : {
            "nodetype" : "column",
            "moduleName" : "POWERSUPPLY-MIB",
            "oid" : "1.3.6.1.4.1.11.2.14.11.5.1.55.1.1.1.8",
            "status" : "current",
            "syntax" : {
                "type" : { "module" :"SNMPv2-SMI", "name" : "Counter32"},
            },
            "access" : "readonly",
            "description" :
                """The number of seconds since the switch power supply is up.""",
        }, # column
        "hpicfPsConformance" : {
            "nodetype" : "node",
            "moduleName" : "POWERSUPPLY-MIB",
            "oid" : "1.3.6.1.4.1.11.2.14.11.5.1.55.2",
        }, # node
        "hpicfPsCompliance" : {
            "nodetype" : "node",
            "moduleName" : "POWERSUPPLY-MIB",
            "oid" : "1.3.6.1.4.1.11.2.14.11.5.1.55.2.1",
        }, # node
        "hpicfPsGroups" : {
            "nodetype" : "node",
            "moduleName" : "POWERSUPPLY-MIB",
            "oid" : "1.3.6.1.4.1.11.2.14.11.5.1.55.2.2",
        }, # node
    }, # nodes

    "groups" : {
        "hpicfPsGroup" : {
            "nodetype" : "group",
            "moduleName" : "POWERSUPPLY-MIB",
            "oid" : "1.3.6.1.4.1.11.2.14.11.5.1.55.2.2.1",
            "status" : "current",
            "members" : {
                "hpicfPsState" : {
                    "nodetype" : "member",
                    "module" : "POWERSUPPLY-MIB"
                },
                "hpicfPsFailures" : {
                    "nodetype" : "member",
                    "module" : "POWERSUPPLY-MIB"
                },
                "hpicfPsTemp" : {
                    "nodetype" : "member",
                    "module" : "POWERSUPPLY-MIB"
                },
                "hpicfPsVoltageInfo" : {
                    "nodetype" : "member",
                    "module" : "POWERSUPPLY-MIB"
                },
                "hpicfPsWattageCur" : {
                    "nodetype" : "member",
                    "module" : "POWERSUPPLY-MIB"
                },
                "hpicfPsWattageMax" : {
                    "nodetype" : "member",
                    "module" : "POWERSUPPLY-MIB"
                },
                "hpicfPsLastCall" : {
                    "nodetype" : "member",
                    "module" : "POWERSUPPLY-MIB"
                },
            }, # members
            "description" :
                """POWER SUPPLY parameters """,
        }, # group
    }, # groups

    "compliances" : {
        "hpicfDcPsCompliance" : {
            "nodetype" : "compliance",
            "moduleName" : "POWERSUPPLY-MIB",
            "oid" : "1.3.6.1.4.1.11.2.14.11.5.1.55.2.1.1",
            "status" : "current",
            "description" :
                """The compliance statement for entries which implement the
POWER SUPPLY MIB.""",
            "requires" : {
                "hpicfPsGroup" : {
                    "nodetype" : "mandatory",
                    "module" : "POWERSUPPLY-MIB"
                },
                "hpicfPsGroup" : {
                    "nodetype" : "optional",
                    "module" : "POWERSUPPLY-MIB",
                    "description" :
                        """Objects associated with Entity POWER SUPPLY.""",
                },
            }, # requires
        }, # compliance
    }, # compliances

}