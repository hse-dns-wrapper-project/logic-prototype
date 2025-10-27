from typing import Any

from libknot.control import KnotCtl, KnotCtlError

from .error.base_error import KnotBaseError

def get_records(
	ctl: KnotCtl,
	zone_domain: str,
	subdomain: str,
	record_type: str,
	data: str
):
	try:
		ctl.send_block(
			cmd = "zone-read",
			zone = zone_domain,
			owner = subdomain,
			rtype = record_type,
			data = data
		)
		output_data: dict[str, dict[str, dict[str, Any]]] = ctl.receive_block()
		data_dict: list[str] = next(iter(next(iter(output_data.values())).values()))

		return data_dict
	except KnotCtlError as raw_error:
		error = KnotBaseError.from_raw_error(raw_error)
		raise error

def set_record(
	ctl: KnotCtl,
	zone_domain: str,
	subdomain: str,
	record_type: str,
	data: str,
	ttl: int
):
	try:
		ttl_str = str(ttl)
		ctl.send_block(
			cmd = "zone-set",
			zone = zone_domain,
			owner = subdomain,
			rtype = record_type,
			ttl = ttl_str,
			data = data
		)
		ctl.receive_block()
	except KnotCtlError as raw_error:
		error = KnotBaseError.from_raw_error(raw_error)
		raise error

def remove_record(
	ctl: KnotCtl,
	zone_domain: str,
	subdomain: str,
	record_type: str,
	data: str
):
	try:
		ctl.send_block(
			cmd = "zone-unset",
			zone = zone_domain,
			owner = subdomain,
			rtype = record_type,
			data = data
		)
		ctl.receive_block()
	except KnotCtlError as raw_error:
		error = KnotBaseError.from_raw_error(raw_error)
		raise error
