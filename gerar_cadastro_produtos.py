import csv
import re
import unicodedata
from pathlib import Path

import pdfplumber


PASTA = Path(__file__).parent
PDF = PASTA / "PRODUTOS CADASTRADOS.pdf"
CSV_ORIGINAL = PASTA / "INVENT.CSV"
CSV_SAIDA = PASTA / "cadastro_produtos.csv"
RELATORIO = PASTA / "relatorio_cadastro.txt"

MAPEAMENTO = {
    "PLF": "SAFRA",
    "M DIAS BRANCO": "MDIAS",
    "M. DIAS BRANCO": "MDIAS",
    "M DIAS": "MDIAS",
    "M. DIAS": "MDIAS",
    "BIMBO": "BIMBO",
    "XANDO": "XANDO",
    "TIROLEZ": "TIROLEZ",
    "ZINHO LEITE": "LEITE",
    "ZINHO": "ZINHO",
    "LEITE": "LEITE",
}

# Exceções confirmadas pelo usuário. Use apenas quando a categoria do
# código já tiver sido conferida no cadastro interno.
CATEGORIAS_CONFIRMADAS_POR_CODIGO = {
    "128069": "MDIAS",
}

UNIDADES = {
    "UN", "BJ", "PT", "PK", "CX", "KG", "LT", "FD",
    "PC", "RL", "SC", "GL", "BD", "FR", "PCT", "DZ",
    "TB", "AM", "GF", "VD", "DP", "JG", "PAR", "BL",
    "TP", "GR", "ML", "L", "G",
}


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", str(texto or ""))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", texto).strip().upper()


def identificar_categoria(secao):
    nome = normalizar(secao)
    # Correspondência exata primeiro, para evitar classificar por trecho errado.
    for nome_pdf, categoria in MAPEAMENTO.items():
        if nome == normalizar(nome_pdf):
            return categoria

    # Alguns PDFs quebram ou abreviam o cabeçalho da seção.
    if re.fullmatch(r"M\.?\s*DIAS(?:\s+BRANCO)?", nome):
        return "MDIAS"
    if "TIROLEZ" in nome:
        return "TIROLEZ"
    if "BIMBO" in nome:
        return "BIMBO"
    if "XANDO" in nome:
        return "XANDO"
    if "ZINHO" in nome and "LEITE" in nome:
        return "LEITE"
    if nome == "PLF":
        return "SAFRA"

    return "REVISAR"


def ler_produtos_pdf():
    if not PDF.exists():
        raise FileNotFoundError(f"PDF não encontrado: {PDF}")

    produtos = {}
    secoes_sem_mapeamento = set()
    categoria_atual = "REVISAR"
    secao_atual = ""

    with pdfplumber.open(PDF) as documento:
        for numero_pagina, pagina in enumerate(documento.pages, start=1):
            texto = pagina.extract_text() or ""

            for linha_original in texto.splitlines():
                linha = re.sub(r"\s+", " ", linha_original).strip()
                if not linha:
                    continue

                normalizada = normalizar(linha)

                # Cabeçalhos/rodapés que se repetem em todas as páginas.
                if any(marcador in normalizada for marcador in (
                    "CODIGO DENOMINACAO",
                    "ESTOQUE FISICO",
                    "FORNECEDOR:",
                    "SAFRA DIST DE ALIMENTOS",
                )):
                    continue

                correspondencia = re.match(r"^(\d{1,10})\s+(.+?)\s*$", linha)
                if not correspondencia:
                    continue

                codigo, descricao = correspondencia.group(1), correspondencia.group(2).strip()
                partes = descricao.rsplit(" ", 1)
                unidade_final = normalizar(partes[-1]) if len(partes) == 2 else ""
                eh_produto = unidade_final in UNIDADES

                if not eh_produto:
                    # A categoria atual fica fora do loop de páginas de propósito:
                    # a seção continua valendo até outro cabeçalho ser encontrado.
                    secao_atual = descricao
                    nova_categoria = identificar_categoria(secao_atual)
                    categoria_atual = nova_categoria
                    if nova_categoria == "REVISAR":
                        secoes_sem_mapeamento.add(
                            f"Página {numero_pagina}: {secao_atual}"
                        )
                    continue

                descricao_produto = descricao.rsplit(" ", 1)[0].strip()
                categoria = CATEGORIAS_CONFIRMADAS_POR_CODIGO.get(
                    codigo, categoria_atual
                )
                registro = {
                    "codigo": codigo,
                    "descricao": descricao_produto,
                    "categoria": categoria,
                }

                if codigo not in produtos:
                    produtos[codigo] = registro
                    continue

                anterior = produtos[codigo]
                cat_ant = anterior["categoria"]
                cat_nova = registro["categoria"]

                # Um registro REVISAR não deve apagar uma categoria conhecida.
                if cat_ant == "REVISAR" and cat_nova != "REVISAR":
                    anterior["categoria"] = cat_nova
                elif cat_nova == "REVISAR" and cat_ant != "REVISAR":
                    pass
                elif cat_ant != cat_nova:
                    # Duas categorias conhecidas conflitantes são sinalizadas.
                    anterior["categoria"] = "REVISAR"
                    anterior["conflito"] = True

                # Diferenças de descrição, sozinhas, não tornam a categoria
                # conflitante; preserva a primeira descrição não vazia.
                if not anterior.get("descricao") and descricao_produto:
                    anterior["descricao"] = descricao_produto

    # Aplica as categorias confirmadas novamente, inclusive a códigos repetidos.
    for codigo, categoria in CATEGORIAS_CONFIRMADAS_POR_CODIGO.items():
        if codigo in produtos:
            produtos[codigo]["categoria"] = categoria

    return produtos, secoes_sem_mapeamento


def inspecionar_csv_original():
    if not CSV_ORIGINAL.exists():
        return "INVENT.CSV não encontrado; cruzamento secundário não realizado."

    conteudo = None
    codificacao = None
    for tentativa in ("utf-8-sig", "utf-16", "utf-16-le", "cp1252", "latin-1"):
        try:
            conteudo = CSV_ORIGINAL.read_text(encoding=tentativa)
            codificacao = tentativa
            break
        except (UnicodeError, LookupError):
            continue

    if conteudo is None:
        return "Não foi possível ler o INVENT.CSV."

    linhas = conteudo.splitlines()
    return (
        f"Codificação interpretada: {codificacao}\n"
        f"Linhas lidas: {len(linhas)}\n"
        "Amostra das primeiras linhas do INVENT.CSV:\n"
        f"{chr(10).join(linhas[:3])}\n"
        "Observação: a amostra é apenas para conferência; "
        "não altera as categorias extraídas do PDF."
    )


def salvar_resultados(produtos, secoes_sem_mapeamento):
    with CSV_SAIDA.open("w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.DictWriter(
            arquivo, fieldnames=["codigo", "descricao", "categoria"], delimiter=";"
        )
        escritor.writeheader()
        for codigo in sorted(produtos, key=lambda c: (len(c), c)):
            registro = produtos[codigo]
            escritor.writerow({
                "codigo": registro["codigo"],
                "descricao": registro["descricao"],
                "categoria": registro["categoria"],
            })

    contagem = {}
    for registro in produtos.values():
        categoria = registro["categoria"]
        contagem[categoria] = contagem.get(categoria, 0) + 1

    with RELATORIO.open("w", encoding="utf-8") as arquivo:
        arquivo.write("RELATÓRIO DO CADASTRO DE PRODUTOS\n\n")
        arquivo.write(f"Produtos únicos extraídos: {len(produtos)}\n\n")
        arquivo.write("Produtos por categoria:\n")
        for categoria, quantidade in sorted(contagem.items()):
            arquivo.write(f"- {categoria}: {quantidade}\n")
        arquivo.write("\nSeções que precisam de mapeamento:\n")
        if secoes_sem_mapeamento:
            for secao in sorted(secoes_sem_mapeamento):
                arquivo.write(f"- {secao}\n")
        else:
            arquivo.write("- Nenhuma seção desconhecida identificada.\n")
        arquivo.write("\n" + inspecionar_csv_original() + "\n\nATENÇÃO:\n")
        arquivo.write(
            "Confira seções desconhecidas e produtos REVISAR antes de usar "
            "o cadastro na automação de faturamento.\n"
        )

    print(f"Cadastro criado: {CSV_SAIDA}")
    print(f"Relatório criado: {RELATORIO}")
    print(f"Total de códigos únicos: {len(produtos)}")
    print(f"Seções sem mapeamento: {len(secoes_sem_mapeamento)}")


def main():
    produtos, secoes_sem_mapeamento = ler_produtos_pdf()
    salvar_resultados(produtos, secoes_sem_mapeamento)


if __name__ == "__main__":
    main()
