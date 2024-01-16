import json
from typing import Annotated
from fastapi import APIRouter, Body, Depends, File, HTTPException, Path, UploadFile, status
from fastapi.encoders import jsonable_encoder
from schemas.arquivo import ArquivoCreate, SecaoSchema
from schemas.declaracao import DeclaracaoCreate
from schemas.idioma import IdiomaSchema
from schemas.validador import ValidadorCreate
from schemas.verificador import VerificadorCreate
from utils.bytes_to_megabytes import bytes_to_megabytes
from utils.language_parser import languages_parser
from utils.errors import errors
from models.problema import Problema
from orm.common.index import get_all, get_by_id
from dependencies.authenticated_user import get_authenticated_user
from schemas.problema import ProblemaCreate, ProblemaReadFull, ProblemaReadSimple, ProblemaUpdatePartial
from schemas.common.pagination import PaginationSchema
from dependencies.database import get_db
from sqlalchemy.orm import Session
from orm.problema import create_problema, update_problema
from schemas.common.response import ResponsePaginationSchema, ResponseUnitSchema
import zipfile
import tempfile
import xml.etree.ElementTree as ET

PROBLEMA_ID_DESCRIPTION = "Identificador do problema"


router = APIRouter(
    prefix="/problemas",
    tags=["problema"],
    dependencies=[Depends(get_authenticated_user)],
)


@router.get("/", response_model=ResponsePaginationSchema[ProblemaReadSimple], summary="Lista problemas")
def read(db: Session = Depends(get_db), common: PaginationSchema = Depends()):
    problemas, metadata = get_all(db, Problema, common)

    return ResponsePaginationSchema(
        data=problemas,
        metadata=metadata
    )


@router.get("/{id}/",
            response_model=ResponseUnitSchema[ProblemaReadFull],
            summary="Lista um problema",
            dependencies=[Depends(get_authenticated_user)],
            responses={
                404: errors[404]
            }
            )
def read_id(
        id: int = Path(description=PROBLEMA_ID_DESCRIPTION),
        db: Session = Depends(get_db)
):
    problema = get_by_id(
        db, Problema, id)
    return ResponseUnitSchema(
        data=problema
    )


@router.post("/",
             response_model=ResponseUnitSchema[ProblemaReadFull],
             status_code=201,
             summary="Cadastra problema",
             responses={
                 422: errors[422]
             }
             )
def create(
    problema: ProblemaCreate = Body(description="Problema a ser criado"),
    db: Session = Depends(get_db)
):
    data = create_problema(db=db, problema=problema)
    print("response: ", jsonable_encoder(data))

    return ResponseUnitSchema(data=data)


@router.post("/upload/",
             response_model=ResponseUnitSchema[ProblemaReadFull],
             status_code=201,
             summary="Importa problema do Polygon via pacote",
             responses={
                 422: errors[422]
             }
             )
def upload(
    pacote: Annotated[UploadFile, File(description="Pacote .zip gerado pelo Polygon")],
    db: Session = Depends(get_db),
):
    if (pacote.content_type not in ["application/zip"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Erro. Formato de pacote inválido!")

    temp_file = tempfile.TemporaryFile()
    temp_file.write(pacote.file.read())
    temp_file.seek(0)

    problema = ProblemaCreate(
        nome="",
        nome_arquivo_entrada="",
        nome_arquivo_saida="",
        tempo_limite=1000,
        memoria_limite=256,
        tags=[],
        declaracoes=[],
        arquivos=[],
        verificador=VerificadorCreate(
            nome="", linguagem="", corpo="", testes=[]),
        validador=ValidadorCreate(
            nome="", linguagem="", corpo="", testes=[]),
    )

    def process_files(path: str | None, secao: SecaoSchema, status: str | None = None):
        if (path != None):
            with zip.open(path) as file:
                nome = file.name.split("/")[-1]
                corpo = file.read().decode()

                arquivo = ArquivoCreate(
                    nome=nome, corpo=corpo, secao=secao, status=status)

                problema.arquivos.append(arquivo)

    def process_verificador_and_validador(path: str | None, linguagem: str | None, tipo: str):
        if path is not None:
            with zip.open(path) as file:
                nome = file.name.split("/")[-1]
                corpo = file.read().decode()

                if tipo == "verificador":
                    verificador = VerificadorCreate(
                        nome=nome, corpo=corpo, linguagem=linguagem or "", testes=[])

                    problema.verificador = verificador

                elif tipo == "validador":
                    validador = ValidadorCreate(
                        nome=nome, corpo=corpo, linguagem=linguagem or "", testes=[])

                    problema.validador = validador

    def process_tempo_limite(data: ET.Element):
        tempo_limite = data.find('.//time-limit')
        if tempo_limite is not None and tempo_limite.text is not None:
            problema.tempo_limite = int(tempo_limite.text)

    def process_memoria_limite(data: ET.Element):
        memoria_limite = data.find('.//memory-limit')
        if memoria_limite is not None and memoria_limite.text is not None:
            memoria_converted = bytes_to_megabytes(int(
                (memoria_limite.text)))

            problema.memoria_limite = memoria_converted

    def process_name(data: ET.Element):
        if (data != None):
            problema.nome = str(data.get("short-name"))

    def process_xml(zip, filename):
        with zip.open(filename) as xml:
            content = xml.read().decode()
            data = ET.fromstring(content)

            # Atribui o tempo limite
            process_tempo_limite(data)

            # Atribui a memória limite
            process_memoria_limite(data)

            # Atribui o nome do problema
            process_name(data)

            # Atribui todos os arquivos de recursos
            for file in data.findall('.//resources/file'):
                process_files(file.get("path"), SecaoSchema.RECURSO)

            # Atribui todos os arquivos de solução
            for solution in data.findall('.//solutions/solution'):
                status = str(solution.get("tag"))
                source = solution.find('source')
                if source is not None:
                    path = source.get("path")
                    process_files(path, SecaoSchema.SOLUCAO, status)

            # Atribui o verificador
            checker = data.find('.//checker/source')
            if (checker != None):
                path = checker.get(
                    "path")
                linguagem = checker.get("type")
                process_verificador_and_validador(
                    path, linguagem, "verificador")

            # Atribui o validador
            validator = data.find(".//validator/source")
            if (validator != None):
                path = validator.get("path")
                linguagem = validator.get("type")
                process_verificador_and_validador(path, linguagem, "validador")

            # Atribui todas as tags
            for tag in data.findall('.//tags/tag'):
                name = str(tag.get("value"))
                problema.tags.append(name)

    def process_statements(zip, filename):
        with zip.open(filename) as statement:
            content = statement.read().decode()
            data = json.loads(content)

            declaracao = DeclaracaoCreate(
                titulo=data["name"],
                contextualizacao=data["legend"],
                formatacao_entrada=data["input"],
                formatacao_saida=data["output"],
                tutorial=data["tutorial"],
                observacao=data["notes"],
                idioma=IdiomaSchema[languages_parser.get(
                    data["language"].capitalize(), "OT")]
            )

            problema.declaracoes.append(declaracao)

# try:
    with zipfile.ZipFile(temp_file, 'r') as zip:
        for filename in zip.namelist():

            # Processa o xml global do problema
            if filename.lower() == "problem.xml":
                process_xml(zip, filename)

            # Processa o statement de cada idioma
            if filename.startswith("statements/") and filename.endswith("problem-properties.json"):
                process_statements(zip, filename)

    data = create_problema(db=db, problema=problema)
    return ResponseUnitSchema(data=data)

    # except:
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #                         detail="Erro. Ocorreu uma falha no processamento do pacote!")


@router.put("/{id}/",
            response_model=ResponseUnitSchema[ProblemaReadFull],
            summary="Atualiza um problema por completo",
            responses={
                404: errors[404]
            },
            dependencies=[Depends(get_authenticated_user)],
            )
def total_update(
        id: int = Path(description=PROBLEMA_ID_DESCRIPTION),
        db: Session = Depends(get_db),
        data: ProblemaCreate = Body(
            description="Problema a ser atualizado por completo"),
):
    response = update_problema(db, id, data)
    return ResponseUnitSchema(
        data=response
    )


@router.patch("/{id}/",
              response_model=ResponseUnitSchema[ProblemaReadFull],
              summary="Atualiza um problema parcialmente",
              responses={
                  404: errors[404]
              },
              dependencies=[Depends(get_authenticated_user)],
              )
def parcial_update(
        id: int = Path(description=PROBLEMA_ID_DESCRIPTION),
        db: Session = Depends(get_db),
        data: ProblemaUpdatePartial = Body(
            description="Problema a ser atualizado parcialmente"),
):
    response = update_problema(db, id, data)
    return ResponseUnitSchema(
        data=response
    )
