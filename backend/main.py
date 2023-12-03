from fastapi import FastAPI
from routers import user
from database import engine, Base
from fastapi.openapi.utils import get_openapi

Base.metadata.create_all(bind=engine)

app = FastAPI(swagger_ui_parameters={"syntaxHighlight.theme": "nord"})
app.include_router(user.router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="API Juiz Online",
        version="0.0.1",
        summary="",
        description="API em desenvolvimento",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
