from .error.base_error import KnotBaseError

from libknot.control import KnotCtl, KnotCtlError

def add_record(ctl: KnotCtl, zone, name, rtype, ttl, data):
	try:
		ttl_str = str(ttl)
		ctl.send_block(cmd="zone-set", zone=zone, owner=name, rtype=rtype, ttl=ttl_str, data=data)
		ctl.receive_block()
	except KnotCtlError as raw_error:
		error = KnotBaseError.from_raw_error(raw_error)
		raise error

def remove_record(ctl: KnotCtl, zone, owner, rtype, ttl, data):
	try:
		ctl.send_block(
			cmd = "zone-unset",
			zone = zone,
			owner = owner,
			rtype = rtype,
			data = data
		)
		ctl.receive_block()
	except KnotCtlError as raw_error:
		error = KnotBaseError.from_raw_error(raw_error)
		raise error

def update_record(
	ctl: KnotCtl,
	zone,
	owner, rtype, ttl, data,
	new_owner, new_rtype, new_ttl, new_data
):
	remove_record(ctl, zone, owner, rtype, ttl, data)
	add_record(ctl, zone, new_owner, new_rtype, new_ttl, new_data)
