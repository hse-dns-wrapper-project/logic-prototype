from contextlib import contextmanager
from libknot.control import KnotCtl

@contextmanager
def open_socket(path: str = "/rundir/knot.sock", timeout: int = 300):
	try:
		ctl = KnotCtl()
		ctl.connect(path)
		if timeout:
			ctl.set_timeout(timeout)
		yield ctl
	finally:
		ctl.close()

@contextmanager
def zone_transaction(ctl : KnotCtl, zone):
	try:
		ctl.send_block(cmd="zone-begin", zone=zone)
		ctl.receive_block()
		yield
	except:
		ctl.send_block(cmd="zone-abort")
		ctl.receive_block()
		raise
	else:
		ctl.send_block(cmd="zone-commit")
		ctl.receive_block()

@contextmanager
def conf_transaction(ctl : KnotCtl):
	try:
		ctl.send_block(cmd="conf-begin")
		ctl.receive_block()
		yield
	except:
		ctl.send_block(cmd="conf-abort")
		ctl.receive_block()
		raise
	else:
		ctl.send_block(cmd="conf-commit")
		ctl.receive_block()