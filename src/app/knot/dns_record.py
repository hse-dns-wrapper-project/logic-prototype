from typing import Any
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

from .error.base_error import KnotBaseError

from libknot.control import KnotCtl, KnotCtlError

type_names_registry: dict[str, "RecordData"] = dict()

UNIQUE_KEY_DATA_NONE = ""

def get_record_data_type(name: str):
	global type_names_registry

	if name not in type_names_registry:
		cls = None
	else:
		cls = type_names_registry[name]
	return cls

@dataclass(frozen=True)
class RecordData(ABC):
	def __init_subclass__(cls, **kwargs):
		global type_names_registry
		type_str = cls.get_type_to_str()
		type_names_registry[type_str] = cls
	
	@classmethod
	def get_type_from_str(cls, type_str: str):
		global type_names_registry
		return type_names_registry[type_str]
	
	def is_unique_key_equal(self, unique_key_data: str):
		return self.get_data_unique_key() == unique_key_data
	
	@classmethod
	@abstractmethod
	def get_type_to_str(cls):
		raise NotImplementedError

	@abstractmethod
	def get_data_to_str(self):
		raise NotImplementedError
	
	@abstractmethod
	def get_data_unique_key(self):
		return UNIQUE_KEY_DATA_NONE
	
	@classmethod
	@abstractmethod
	def get_data_from_str(cls, data_str: str) -> "RecordData":
		raise NotImplementedError

@dataclass(frozen=True)
class ARecord(RecordData):
	ipv4: str

	@classmethod
	def get_type_to_str(cls):
		return "A"
	
	def get_data_to_str(self):
		return self.ipv4
	
	@classmethod
	def get_data_from_str(cls, data_str: str):
		return ARecord(data_str)
	
	def get_data_unique_key(self):
		return self.ipv4

@dataclass(frozen=True)
class AAAARecord(RecordData):
	ipv6: str

	@classmethod
	def get_type_to_str(cls):
		return "AAAA"
	
	def get_data_to_str(self):
		return self.ipv6
	
	@classmethod
	def get_data_from_str(cls, data_str: str):
		return AAAARecord(data_str)
	
	def get_data_unique_key(self):
		return self.ipv6

@dataclass(frozen=True)
class RecordUniqueKey:
	zone_domain: str
	subdomain: str
	record_type: type["RecordData"]
	unique_key_data: str = UNIQUE_KEY_DATA_NONE

@dataclass(frozen=True)
class Record:
	zone_domain: str
	subdomain: str
	data: RecordData
		
	def to_dict(self):
		return {
			'zone_domain': self.zone_domain,
			'subdomain': self.subdomain,
			'record_type': self.data.get_type_to_str(),
			'data': asdict(self.data)
		}
	
	def get_unique_key(self):
		return RecordUniqueKey(
			self.zone_domain,
			self.subdomain,
			type(self.data),
			self.data.get_data_unique_key()
		)

def get_records_data(
	ctl: KnotCtl,
	key: RecordUniqueKey
):
	try:
		ctl.send_block(
			cmd = "zone-read",
			zone = key.zone_domain,
			owner = key.subdomain,
			rtype = key.record_type.get_type_to_str(),
			data = key.unique_key_data
		)
		data: dict[str, dict[str, dict[str, Any]]] = ctl.receive_block()
		data_list: list[str] = next(iter(next(iter(data.values())).values()))[key.record_type.get_type_to_str()]['data']

		return list((key.record_type.get_data_from_str(data_str) for data_str in data_list))
	except KnotCtlError as raw_error:
		error = KnotBaseError.from_raw_error(raw_error)
		raise error
	
def get_record_data(
	ctl: KnotCtl,
	key: RecordUniqueKey
):
	data_list = get_records_data(ctl, key)

	for data in data_list:
		if data.is_unique_key_equal(key.unique_key_data):
			return data
	return None
	
def get_record(
	ctl: KnotCtl,
	key: RecordUniqueKey
):
	data = get_record_data(ctl, key)
	if data is None:
		return None
	
	record = Record(key.zone_domain, key.subdomain, data)
	return record

def get_records(
	ctl: KnotCtl,
	key: RecordUniqueKey
):
	data_list = get_records_data(ctl, key)
	if data_list is None:
		return None
	
	records = list((Record(key.zone_domain, key.subdomain, data) for data in data_list))
	return records

def add_record_raw(
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

def add_record(
	ctl: KnotCtl,
	record: Record,
	ttl: int
):
	return add_record_raw(
		ctl,
		record.zone_domain,
		record.subdomain,
		record.data.get_type_to_str(),
		record.data.get_data_to_str(),
		ttl
	)

def remove_record(
	ctl: KnotCtl,
	key: RecordUniqueKey
):
	try:
		ctl.send_block(
			cmd = "zone-unset",
			zone = key.zone_domain,
			owner = key.subdomain,
			rtype = key.record_type.get_type_to_str(),
			data = key.unique_key_data
		)
		ctl.receive_block()
	except KnotCtlError as raw_error:
		error = KnotBaseError.from_raw_error(raw_error)
		raise error

def update_record(
	ctl: KnotCtl,
	key: RecordUniqueKey,
	new_data: RecordData,
	ttl: int
):
	try:
		if not isinstance(new_data, key.record_type):
			raise TypeError(f"New_data must be type {key.record_type.__name__}")
		
		ttl_str = str(ttl)
		ctl.send_block(
			cmd = "zone-set",
			zone = key.zone_domain,
			owner = key.subdomain,
			rtype = key.record_type.get_type_to_str(),
			ttl = ttl_str,
			data = new_data.get_data_to_str()
		)
		ctl.receive_block()
	except KnotCtlError as raw_error:
		error = KnotBaseError.from_raw_error(raw_error)
		raise error
