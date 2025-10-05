from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
def read_root():
    html_content = "Check"
    return HTMLResponse(content=html_content)

from fastapi.responses import JSONResponse

from app.knot.transactions import open_socket, zone_transaction, conf_transaction
from app.knot.dns_zone import get_zone_by_name, get_zones_list, add_zone, remove_zone
from app.knot.dns_record import get_record_data_type, Record, ARecord, AAAARecord, RecordUniqueKey, add_record_raw, add_record, remove_record, get_records_data

standard_ttl = 300

@app.get("/zone")
def get_all_zones():
    with open_socket() as ctl:
        zones = get_zones_list(ctl)
        return JSONResponse(zones)

@app.get("/zone/{zone_domain}")
def get_zone_info_by_name(zone_domain):
    with open_socket() as ctl:
        zones = get_zone_by_name(ctl, zone_domain)
        return JSONResponse(zones)

@app.post("/zone")
def add_new_zone(
    zone_domain: str
):
    with open_socket() as ctl:
        with conf_transaction(ctl):
            add_zone(ctl, zone_domain)

@app.delete("/zone")
def remove_old_zone(
    zone_domain: str
):
    with open_socket() as ctl:
        with conf_transaction(ctl):
            remove_zone(ctl, zone_domain)

@app.post("/zone/{zone_domain}/record")
def add_new_record_raw(
    zone_domain,
    subdomain,
    record_type,
    data
):
    global standard_ttl
    ttl = standard_ttl

    with open_socket() as ctl:
        with zone_transaction(ctl, zone_domain):
            add_record_raw(ctl, zone_domain, subdomain, record_type, data, ttl)

@app.post("/zone/{zone_domain}/record/type/A")
def add_record_A(
    zone_domain,
    subdomain,
    ipv4
):
    global standard_ttl
    ttl = standard_ttl

    with open_socket() as ctl:
        with zone_transaction(ctl, zone_domain):
            add_record(
                ctl,
                Record(
                    RecordUniqueKey(
                        zone_domain,
                        subdomain,
                        ARecord
                    ),
                    ARecord(ipv4)
                ), ttl)

@app.post("/zone/{zone_domain}/record/type/AAAA")
def add_record_AAAA(
    zone_domain,
    subdomain,
    ipv6
):
    global standard_ttl
    ttl = standard_ttl

    with open_socket() as ctl:
        with zone_transaction(ctl, zone_domain):
            add_record(
                ctl,
                Record(
                    RecordUniqueKey(
                        zone_domain,
                        subdomain,
                        AAAARecord
                    ),
                    ARecord(ipv6)
                ), ttl)

@app.delete("/zone/{zone_domain}/record")
def remove_old_record(
    zone_domain,
    subdomain,
    record_type
):
    with open_socket() as ctl:
        with zone_transaction(ctl, zone_domain):
            record_type_cls = get_record_data_type(record_type)
            key = RecordUniqueKey(zone_domain, subdomain, record_type_cls)
            remove_record(ctl, key)

@app.get("/zone/{zone_domain}/record")
def get_records_info(
    zone_domain,
    subdomain,
    record_type
):
    with open_socket() as ctl:
        record_type_cls = get_record_data_type(record_type)
        key = RecordUniqueKey(zone_domain, subdomain, record_type_cls)
        data_list = get_records_data(ctl, key)
        return JSONResponse(list((data.to_dict() for data in data_list)))