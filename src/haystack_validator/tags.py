"""Small bundled tag vocabulary. It is a subset chosen for HVAC point lists."""

import re

ENTITY_TAGS = {"site", "space", "equip", "point"}
FUNCTION_TAGS = {"sensor", "cmd", "sp"}
KINDS = {"Number", "Bool", "Str"}

KNOWN_TAGS = ENTITY_TAGS | FUNCTION_TAGS | {
    # equipment
    "ahu", "vav", "rtu", "fcu", "chiller", "boiler", "pump", "fan", "meter",
    "elecMeter", "coolingTower", "damper", "valve",
    # substances
    "air", "water", "steam", "elec", "gas",
    # quantities
    "temp", "pressure", "flow", "humidity", "co2", "power", "energy", "speed",
    "level", "freq", "current", "volt",
    # position and role
    "discharge", "return", "supply", "exhaust", "outside", "zone", "mixed",
    "entering", "leaving", "cool", "heat", "run", "enable", "fault", "status",
    "occupied", "effective", "limit", "min", "max", "position", "chilled",
    "hot", "condenser", "filter", "differential", "load", "cur", "his",
}

TAG_NAME = re.compile(r"^[a-z][a-zA-Z0-9_]*$")
