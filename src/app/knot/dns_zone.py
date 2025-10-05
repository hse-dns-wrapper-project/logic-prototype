from typing import Any
from libknot.control import KnotCtl, KnotCtlError

from .error.base_error import KnotBaseError
def get_zones_list(ctl: KnotCtl):
    try:
        ctl.send_block(cmd="conf-read", section="zone")
        resp = ctl.receive_block()
        if len(resp) == 0:
            return tuple()
        zones_dict: dict[str, Any] = resp['zone']
        zones = tuple((name for name in zones_dict))
        return zones
    except KnotCtlError as raw_error:
        error = KnotBaseError.from_raw_error(raw_error)
        raise error

def get_zone_by_name(ctl: KnotCtl, zone: str):
    try:
        ctl.send_block(cmd="zone-read", zone=zone)
        resp = ctl.receive_block()
        return resp
    except KnotCtlError as raw_error:
        error = KnotBaseError.from_raw_error(raw_error)
        raise error

def add_zone(ctl: KnotCtl, zone: str):
    try:
        ctl.send_block(cmd="conf-set", section="zone", identifier=zone)
        ctl.receive_block()
    except KnotCtlError as raw_error:
        error = KnotBaseError.from_raw_error(raw_error)
        raise error

def remove_zone(ctl: KnotCtl, zone: str):
    try:
        ctl.send_block(cmd="conf-unset", section="zone", identifier=zone)
        ctl.receive_block()
    except KnotCtlError as raw_error:
        error = KnotBaseError.from_raw_error(raw_error)
        raise error