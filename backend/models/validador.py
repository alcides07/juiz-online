from models.validadorTeste import ValidadorTeste
from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base


class Validador(Base):
    __tablename__ = "validadores"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    nome = Column(
        String(length=64),
        index=True,
        nullable=False,
    )

    corpo = Column(
        String(length=250000),
        nullable=False,
    )

    # Talvez Enum em breve
    linguagem = Column(
        String,
        nullable=False,
    )

    problema_id = Column(Integer, ForeignKey('problemas.id'))
    problema = relationship(
        "Problema",
        uselist=False,
        foreign_keys=[problema_id],
        post_update=True,
    )

    testes = relationship(
        ValidadorTeste,
        back_populates="validador"
    )

    __table_args__ = (
        UniqueConstraint('problema_id'),
    )
