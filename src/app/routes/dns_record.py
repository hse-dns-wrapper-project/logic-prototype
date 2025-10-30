from fastapi import Request, Response, APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

from app.knot.transactions import open_socket, zone_transaction
from app.knot.dns_record import set_record, remove_record, get_records

router = APIRouter(prefix='')
templates = Jinja2Templates(directory='app/templates')

standard_ttl = 300

@router.post("/zone/{zone_domain}/record")
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

@router.delete("/zone/{zone_domain}/record")
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

@router.get("/zone/{zone_domain}/record")
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
