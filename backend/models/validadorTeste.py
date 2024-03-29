from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class ValidadorTeste(Base):
    __tablename__ = "validador_testes"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    numero = Column(
        Integer,
        CheckConstraint('numero >= 1'),
        CheckConstraint('numero <= 1000'),
        nullable=False,
    )

    entrada = Column(
        String(length=250000),
        nullable=False,
    )

    veredito = Column(
        String,
        nullable=False
    )

    validador_id = Column(
        Integer,
        ForeignKey(
            'validadores.id',
            name="validador_testes_validador_id_fkey",
            ondelete='CASCADE'
        )
    )
    validador = relationship(
        "Validador",
        uselist=False,
        foreign_keys=[validador_id],
        post_update=True,
    )
