from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
def read_root():
    html_content = "<h2>Hello METANIT.COM!</h2>"
    return HTMLResponse(content=html_content)

from fastapi.responses import JSONResponse

from app.knot.transactions import open_socket, zone_transaction, conf_transaction
from app.knot.dns_zone import get_zone, get_zones_list, add_zone, remove_zone

@app.get("/zone")
def get_all_zones():
    with open_socket() as ctl:
        zones = get_zones_list(ctl)
        return JSONResponse(zones)

@app.get("/zone/{zone}")
def get_zone_info(zone):
    with open_socket() as ctl:
        zones = get_zone(ctl, zone)
        return JSONResponse(zones)

@app.post("/zone")
def add_new_zone(
    zone: str
):
    with open_socket() as ctl:
        with conf_transaction(ctl):
            add_zone(ctl, zone)

@app.delete("/zone")
def remove_old_zone(
    zone: str
):
    with open_socket() as ctl:
        with conf_transaction() as ctl:
            remove_zone(ctl, zone)