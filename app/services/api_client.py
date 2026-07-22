import logging
import requests
from flask import current_app

logger = logging.getLogger(__name__)

CAMPOS_OBRIGATORIOS = [
    "medico",
    "especialidade",
    "data",
    "horario",
    "convenio"
]


class ApiIndisponivelError(Exception):
    """Levantada quando a API de agendamentos não responde corretamente."""


def _campos_faltando(registro):
    return [campo for campo in CAMPOS_OBRIGATORIOS if not registro.get(campo)]


def buscar_agendamentos(termo_busca=None, timeout=5):
    base_url = current_app.config["MOCK_API_URL"]
    url = f"{base_url}/agendamentos"
    params = {"q": termo_busca} if termo_busca else None

    try:
        resposta = requests.get(url, params=params, timeout=timeout)
    except requests.exceptions.ConnectionError as exc:
        logger.error("Falha de conexão com a API de agendamentos: %s", exc)
        raise ApiIndisponivelError(
            "Não foi possível conectar ao serviço de agendamentos."
        ) from exc
    except requests.exceptions.Timeout as exc:
        logger.error("Timeout ao consultar a API de agendamentos: %s", exc)
        raise ApiIndisponivelError(
            "O serviço de agendamentos demorou demais para responder."
        ) from exc
    except requests.exceptions.RequestException as exc:
        logger.error("Erro inesperado ao consultar a API de agendamentos: %s", exc)
        raise ApiIndisponivelError(
            "Ocorreu um erro ao consultar o serviço de agendamentos."
        ) from exc

    if resposta.status_code >= 500:
        logger.error("API de agendamentos retornou erro %s", resposta.status_code)
        raise ApiIndisponivelError("O serviço de agendamentos está indisponível no momento.")

    if resposta.status_code >= 400:
        logger.warning("API de agendamentos retornou status %s", resposta.status_code)
        return []

    try:
        dados = resposta.json()
    except ValueError as exc:
        logger.error("Resposta da API não é um JSON válido: %s", exc)
        raise ApiIndisponivelError(
            "O serviço de agendamentos retornou uma resposta inválida."
        ) from exc

    if dados is None:
        logger.warning("API de agendamentos retornou corpo vazio.")
        return []

    lista = dados.get("agendamentos") if isinstance(dados, dict) else dados

    if not isinstance(lista, list):
        logger.error("Formato inesperado retornado pela API: %s", type(lista))
        raise ApiIndisponivelError("O serviço de agendamentos retornou dados em formato inesperado.")

    validos = []
    for registro in lista:
        if not isinstance(registro, dict):
            logger.warning("Registro ignorado (não é um objeto válido): %r", registro)
            continue
        faltando = _campos_faltando(registro)
        if faltando:
            logger.warning("Registro ignorado por campos ausentes %s: %r", faltando, registro)
            continue
        validos.append(registro)

    return validos