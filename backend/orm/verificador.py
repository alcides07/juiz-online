from dependencies.authorization_user import is_user
from fastapi import HTTPException, status
from models.administrador import Administrador
from models.user import User
from models.verificador import Verificador
from orm.common.index import delete_object
from schemas.verificador import VerificadorCreateSingle
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.problema import Problema


async def create_verificador(
    db: Session,
    verificador: VerificadorCreateSingle,
    user: User | Administrador
):
    db_problema = db.query(Problema).filter(
        Problema.id == verificador.problema_id
    ).first()

    if (db_problema == None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Problema não encontrado!")

    try:
        if (is_user(user) and db_problema.usuario_id != user.id):  # type: ignore
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        db_verificador = Verificador(
            **verificador.model_dump(exclude=set(["problema"])))

        if (db_problema.verificador != None):
            await delete_object(
                db=db,
                model=Verificador,
                id=db_problema.verificador_id,  # type: ignore
                model_has_user_key=Problema
            )

        db.add(db_verificador)
        db_verificador.problema = db_problema
        db_problema.verificador = db_verificador

        db.commit()
        db.refresh(db_verificador)
        db.refresh(db_problema)

        return db_verificador

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)