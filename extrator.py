from modelo import Danfe
import re


# ======================================================
# FUNÇÕES AUXILIARES
# ======================================================

def limpar_linha(texto: str) -> str:
    """Remove espaços duplicados."""
    return " ".join(texto.split())


def obter_linhas(texto: str):
    """Retorna todas as linhas não vazias."""
    return [linha.strip() for linha in texto.splitlines() if linha.strip()]


def linha_apos(texto, marcador):
    """
    Retorna a primeira linha após um marcador.
    Exemplo:
        ENDEREÇO
        RUA XPTO...
    """
    linhas = obter_linhas(texto)

    for i, linha in enumerate(linhas):
        if marcador.upper() in linha.upper():

            if i + 1 < len(linhas):
                return linhas[i + 1]

    return ""


# ======================================================
# IDENTIFICAÇÃO
# ======================================================

def identificar_inicio_danfe(texto):

    return bool(
        re.search(r"fl\.\s*1\s*/\s*\d+", texto, re.IGNORECASE)
    )


# ======================================================
# DANFE
# ======================================================

def extrair_danfe(texto):

    return Danfe(
        cidade=extrair_cidade(texto),
        data_emissao=extrair_data(texto),
        cnpj=extrair_cnpj(texto),
        codigo_cliente=extrair_codigo_cliente(texto),
        razao_social=f"{extrair_razao(texto)} {extrair_codigo_cliente(texto)}",
        endereco=extrair_endereco(texto),
        numero_notas=1,
        numero_nf=extrair_numero_nf(texto),
        numero_embarque="",
        peso_bruto=extrair_peso(texto),
        valor_total=extrair_valor(texto)
    )

# ======================================================
# NÚMERO CNPJ
# ======================================================

def extrair_cnpj(texto):

    resultado = re.search(
        r"DESTINATÁRIO\s*/\s*REMETENTE.*?"
        r"NOME\s*/\s*RAZÃO SOCIAL.*?"
        r"(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})",
        texto,
        re.DOTALL
    )

    if resultado:
        return resultado.group(1)

    return ""

# ======================================================
# COD CLIENTE
# ======================================================

def extrair_codigo_cliente(texto):

    resultado = re.search(
        r"Codigo Cliente:\s*(\d+)",
        texto,
        re.IGNORECASE
    )

    if resultado:
        return resultado.group(1)

    return ""

# ======================================================
# NÚMERO NF
# ======================================================

def extrair_numero_nf(texto):

    resultado = re.search(
        r"Nº\s+(\d{3}\.\d{3}\.\d{3})",
        texto
    )

    if resultado:
        numero = resultado.group(1).replace(".", "")
        return str(int(numero))

    return ""


# ======================================================
# DATA
# ======================================================

def extrair_data(texto):

    resultado = re.search(
        r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\s+(\d{2}/\d{2}/\d{4})",
        texto
    )

    return resultado.group(1) if resultado else ""


# ======================================================
# RAZÃO SOCIAL
# ======================================================

def extrair_razao(texto):

    resultado = re.search(
        r"NOME\s*/\s*RAZÃO SOCIAL.*?\n(.*?)\s+\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}",
        texto,
        re.DOTALL
    )

    if resultado:
        return limpar_linha(resultado.group(1))

    return ""


# ======================================================
# ENDEREÇO
# ======================================================

def extrair_endereco(texto):

    endereco = linha_apos(texto, "ENDEREÇO")

    if not endereco:
        return ""

    endereco = limpar_linha(endereco)

    # Remove CEP
    endereco = re.sub(r"\d{5}-\d{3}.*", "", endereco)

    # Remove data
    endereco = re.sub(r"\d{2}/\d{2}/\d{4}.*", "", endereco)

    # Remove número da residência
    endereco = re.sub(r",\s*\d+.*", "", endereco)

    # Remove caso venha KM
    endereco = re.sub(r",?\s*KM\s*\d+.*", "", endereco, flags=re.IGNORECASE)

    return endereco.strip()


# ======================================================
# CIDADE
# ======================================================

def extrair_cidade(texto):

    cidade = linha_apos(texto, "MUNICÍPIO")

    if cidade:

        cidade = cidade.split("(")[0]

        cidade = cidade.split("SP")[0]

        cidade = cidade.strip()

    return cidade


# ======================================================
# PESO
# ======================================================

def extrair_peso(texto):

    linhas = obter_linhas(texto)

    for i, linha in enumerate(linhas):

        if "PESO BRUTO" in linha.upper():

            print(">>> ENCONTREI PESO BRUTO")
            print(f">>> Linha: {linha}")

            for proxima_linha in linhas[i + 1:i + 6]:

                print(f">>> Procurando em: {proxima_linha}")

                resultado = re.search(
                    r"\b\d+(?:\.\d{3})*,\d+\b",
                    proxima_linha
                )

                if resultado:

                    print(
                        f">>> PESO ENCONTRADO: "
                        f"{resultado.group(0)}"
                    )

                    return resultado.group(0)

    print(">>> PESO BRUTO NÃO ENCONTRADO")

    return ""

# ======================================================
# VALOR
# ======================================================

def extrair_valor(texto):

    resultado = re.search(
        r"VALOR TOTAL:\s*R\$\s*([\d.,]+)",
        texto,
        re.IGNORECASE
    )

    if not resultado:

        resultado = re.search(
            r"V\s*ALOR TOTAL DA NOTA.*?(\d{1,3}(?:\.\d{3})*,\d{2})",
            texto,
            re.DOTALL | re.IGNORECASE
        )

    if resultado:

        valor = resultado.group(1)

        valor = valor.replace(".", "")
        valor = valor.replace(",", ".")

        valor = f"{float(valor):.2f}"

        return valor.replace(".", ",")

    return ""