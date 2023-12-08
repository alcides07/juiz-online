from fastapi import APIRouter, Depends
from schemas.problema import Problema_Create, Problema_Read
from schemas.common.pagination import pagination_schema
from dependencies.database import get_db
from sqlalchemy.orm import Session
from orm.problema import create_problema, read_problemas
from schemas.common.response import response_schema
from fastapi import Depends


router = APIRouter(
    prefix="/problemas",
    tags=["problema"],
)


@router.get("/", response_model=response_schema[Problema_Read], summary="Lista problemas")
def problemas(db: Session = Depends(get_db), common: pagination_schema = Depends()):
    problemas = read_problemas(db, common)

    return response_schema(
        data=problemas
    )


@router.post("/", response_model=response_schema[Problema_Read], status_code=201, summary="Cadastra problema")
def problema(
    problema: Problema_Create, db: Session = Depends(get_db)
):
    data = create_problema(db=db, problema=problema)

    return response_schema(data=data)
