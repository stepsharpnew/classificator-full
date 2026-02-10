from fastapi import FastAPI,Request
from uvicorn import run
from fastapi.middleware.cors import CORSMiddleware
from app.settings import get_settings
from app.libs.routers.classificator_router import classificator_router
from app.libs.routers.equipment_type_router import equipment_type_router
from app.libs.routers.account_routes import account_router
from app.libs.routers.equipment_router import equipment_router
from app.libs.routers.notes_router import notes_router
settings = get_settings()


app = FastAPI(
    title="ssius",
    description="",
)


app.add_middleware(CORSMiddleware,
                   allow_origins=[settings.origin],
                   allow_credentials=True,
                   allow_methods=['*'],
                   allow_headers=['*'])

app.include_router(classificator_router, tags=['classificator'])
app.include_router(equipment_type_router, tags=['equipment type'])
app.include_router(account_router, tags=['account'])
app.include_router(equipment_router, tags=['equipment'])
app.include_router(notes_router, tags=['notes'])

def main() -> None:
    run(
        app,
        host='0.0.0.0',
        port=8080
    )
