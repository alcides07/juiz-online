from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum
from schemas.common.compilers import CompilersEnum

ARQUIVO_ID_DESCRIPTION = "Identificador do arquivo"
PROBLEMA_ID_DESCRIPTION = "Identificador do problema associado ao arquivo"


class SecaoEnum(Enum):
    RECURSO = "recursos"
    FONTE = "arquivos_fonte"
    ANEXO = "anexo"
    SOLUCAO = "solucao"
    GERADOR = "gerador"


class ArquivoBase(BaseModel):

    nome: str = Field(
        max_length=64,
        description="Nome do arquivo do problema"
    )

    secao: SecaoEnum = Field(
        description="Grupo o qual o arquivo faz parte"
    )

    status: Optional[str] = Field(
        default=None,
        description="Tipos de status de veredíto para arquivos de solução"
    )

    linguagem: Optional[CompilersEnum] = Field(
        default=None,
        description="Linguagem de programação em que o arquivo está escrito"
    )


class ArquivoBaseFull(ArquivoBase):
    corpo: str = Field(
        max_length=250000,
        description="Conteúdo do arquivo"
    )


class ArquivoReadFull(ArquivoBaseFull):
    id: int = Field(description=ARQUIVO_ID_DESCRIPTION)
    problema_id: int = Field(
        description=PROBLEMA_ID_DESCRIPTION)


class ArquivoReadSimple(ArquivoBase):
    id: int = Field(description=ARQUIVO_ID_DESCRIPTION)
    problema_id: int = Field(
        description=PROBLEMA_ID_DESCRIPTION)


class ArquivoCreate(ArquivoBaseFull):
    pass


class ArquivoCreateSingle(ArquivoBaseFull):
    problema_id: int = Field(
        description=PROBLEMA_ID_DESCRIPTION)


class ArquivoUpdateTotal(ArquivoBaseFull):
    pass


class ArquivoUpdatePartial(BaseModel):
    nome: Optional[str] = Field(
        default=None,
        max_length=64,
        description="Nome do arquivo do problema"
    )

    secao: Optional[SecaoEnum] = Field(
        default=None,
        description="Grupo o qual o arquivo faz parte"
    )

    status: Optional[str] = Field(
        default=None,
        description="Tipos de status de veredíto para arquivos de solução"
    )

    corpo: Optional[str] = Field(
        default=None,
        max_length=250000,
        description="Conteúdo do arquivo"
    )
