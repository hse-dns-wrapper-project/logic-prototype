from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

"""
@app.get("/")
def read_root():
    html_content = "<h2>Hello METANIT.COM!</h2>"
    return HTMLResponse(content=html_content)
"""

from fastapi.responses import JSONResponse

from .knot.transactions import open_socket, zone_transaction
from .knot.dns_zone import get_zone, get_zones_list

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
