from orm.verificador import create_verificador
from routers.auth import oauth2_scheme
from dependencies.authenticated_user import get_authenticated_user
from dependencies.database import get_db
from fastapi import APIRouter, Depends, Path
from models.problema import Problema
from models.verificador import Verificador
from orm.common.index import get_all, get_by_id
from schemas.common.pagination import PaginationSchema
from schemas.common.response import ResponsePaginationSchema, ResponseUnitSchema
from schemas.verificador import VerificadorCreateSingle, VerificadorReadFull, VerificadorReadSimple
from sqlalchemy.orm import Session
from utils.errors import errors

router = APIRouter(
    prefix="/verificadores",
    tags=["verificador"],
    dependencies=[Depends(get_authenticated_user)],
)


@router.get("/",
            response_model=ResponsePaginationSchema[VerificadorReadSimple],
            summary="Lista verificadores",
            )
async def read(
        db: Session = Depends(get_db),
        pagination: PaginationSchema = Depends(),
        token: str = Depends(oauth2_scheme)
):
    verificadores, metadata = await get_all(
        db=db,
        model=Verificador,
        pagination=pagination,
        token=token
    )

    return ResponsePaginationSchema(
        data=verificadores,
        metadata=metadata
    )


@router.get("/{id}/",
            response_model=ResponseUnitSchema[VerificadorReadFull],
            summary="Lista um verificador",
            responses={
                404: errors[404]
            }
            )
async def read_id(
        id: int = Path(description="Identificador do verificador"),
        db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    verificador = await get_by_id(
        db=db,
        model=Verificador,
        id=id,
        token=token,
        model_has_user_key=Problema
    )

    return ResponseUnitSchema(
        data=verificador
    )


@router.post("/",
             response_model=ResponseUnitSchema[VerificadorReadFull],
             status_code=201,
             summary="Cadastra um verificador",
             responses={
                 422: errors[422],
                 404: errors[404]
             }
             )
async def create(
    verificador: VerificadorCreateSingle,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    user = await get_authenticated_user(token=token, db=db)

    verificador = await create_verificador(
        db=db,
        verificador=verificador,
        user=user,
    )

    return ResponseUnitSchema(data=verificador)
