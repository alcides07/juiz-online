from typing import Any
from models.user import User
from sqlalchemy.orm import Session


def user_autenthicated(token: str, db: Session):
    from dependencies.authenticated_user import get_authenticated_user
    return get_authenticated_user(token, db)


async def has_authorization_user(
    model: Any,
    db: Session,
    db_object: Any,
    token: str,
    model_has_user_key: Any,
):
    """Indica se o usuário autenticado possui ou não autorização para manipular um objeto de um modelo qualquer do banco de dados.

    Args:
        model (Any): Modelo do banco de dados o qual se deseja manipular
        db (Session): Sessão de banco de dados
        db_object (Any): Objeto específico do modelo que se deseja manipular
        token (str): Token do usuário autenticado
        model_has_user_key (Any): Modelo que realmente armazena a chave estrangeira do usuário. A fim de verificar se o usuário autenticado tem permissão para operar em um objeto específico, mas essa verificação é feita a partir de um objeto pai ao qual o objeto específico pertence.

    Returns:
        bool: Retorna True ou False conforme a autorização do usuário para efetuar a ação desejada.
    """

    obj_model_has_user_key = db_object

    if (model != model_has_user_key and hasattr(db_object, model_has_user_key.__name__.lower())):
        obj_model_has_user_key = getattr(
            db_object, model_has_user_key.__name__.lower())

    user = await user_autenthicated(token, db)

    if (
        isinstance(obj_model_has_user_key,
                   User) and user.id == obj_model_has_user_key.id
        or
            hasattr(obj_model_has_user_key, "usuario_id") and obj_model_has_user_key.usuario_id == user.id):
        return True

    return False