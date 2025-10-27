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
from app.knot.dns_record import set_record, remove_record, get_records

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
def set_new_record(
    zone_domain,
    subdomain,
    record_type,
    data
):
    global standard_ttl
    ttl = standard_ttl

    with open_socket() as ctl:
        with zone_transaction(ctl, zone_domain):
            set_record(
                ctl,
                zone_domain,
                subdomain,
                record_type,
                data,
                ttl
            )

@app.delete("/zone/{zone_domain}/record")
def remove_old_record(
    zone_domain,
    subdomain,
    record_type,
    unique_key_data = ""
):
    with open_socket() as ctl:
        with zone_transaction(ctl, zone_domain):
            remove_record(
                ctl,
                zone_domain,
                subdomain,
                record_type,
                unique_key_data
            )

@app.get("/zone/{zone_domain}/record")
def get_records_info(
    zone_domain,
    subdomain,
    record_type,
    unique_key_data = ""
):
    with open_socket() as ctl:
        record = get_records(
            ctl,
            zone_domain,
            subdomain,
            record_type,
            unique_key_data
        )
        return JSONResponse(record)