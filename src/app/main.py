from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

from app.routes.dns_record import router as dns_record_router
from app.routes.dns_zone import router as dns_record_zone

app.include_router(dns_record_router)
app.include_router(dns_record_zone)

@app.get("/")
def read_root():
    html_content = "Check"
    return HTMLResponse(content=html_content)
