import pdfplumber
import os
import shutil
from datetime import datetime


# ============================================================
# LISTAR PDFs
# ============================================================

def listar_pdfs(pasta):
    """
    Retorna todos os PDFs encontrados na pasta.
    """

    arquivos = []

    if not os.path.exists(pasta):
        return arquivos

    for arquivo in os.listdir(pasta):

        if arquivo.lower().endswith(".pdf"):

            arquivos.append(
                os.path.join(pasta, arquivo)
            )

    return arquivos


# ============================================================
# LER PDF
# ============================================================

def ler_pdf(caminho_pdf):
    """
    Lê todas as páginas do PDF.

    Retorna uma lista contendo o texto
    de cada página.
    """

    paginas = []

    with pdfplumber.open(caminho_pdf) as pdf:

        for pagina in pdf.pages:

            texto = pagina.extract_text()

            if texto:
                paginas.append(texto)

            else:
                paginas.append("")

    return paginas


# ============================================================
# MOVER PDF PARA IMPORTADOS
# ============================================================

def mover_para_importados(caminho_pdf, pasta_importados):
    """
    Move o PDF processado para a pasta IMPORTADOS.

    O arquivo recebe automaticamente um nome
    com data e hora para evitar substituição
    de arquivos existentes.
    """

    # --------------------------------------------------------
    # Cria a pasta IMPORTADOS caso ela não exista
    # --------------------------------------------------------

    os.makedirs(
        pasta_importados,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Obtém o nome original do arquivo
    # --------------------------------------------------------

    nome_original = os.path.basename(
        caminho_pdf
    )

    nome, extensao = os.path.splitext(
        nome_original
    )

    # --------------------------------------------------------
    # Cria data e hora
    # --------------------------------------------------------

    data_hora = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    # --------------------------------------------------------
    # Primeiro nome que será tentado
    #
    # Exemplo:
    # NF.pdf
    #
    # vira:
    #
    # NF_20260814_153025.pdf
    # --------------------------------------------------------

    novo_nome = (
        f"{nome}_{data_hora}{extensao}"
    )

    destino = os.path.join(
        pasta_importados,
        novo_nome
    )

    # --------------------------------------------------------
    # Garante que nunca haverá substituição
    # --------------------------------------------------------

    contador = 1

    while os.path.exists(destino):

        novo_nome = (
            f"{nome}_{data_hora}_{contador}{extensao}"
        )

        destino = os.path.join(
            pasta_importados,
            novo_nome
        )

        contador += 1

    # --------------------------------------------------------
    # Move o arquivo
    # --------------------------------------------------------

    shutil.move(
        caminho_pdf,
        destino
    )

    return destino