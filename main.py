from leitor_pdf import listar_pdfs, ler_pdf, mover_para_importados
from extrator import identificar_inicio_danfe, extrair_danfe
from excel import abrir_planilha, adicionar_danfe, salvar_planilha
from config import CAMINHO_ROTA, PASTA_DANFES, PASTA_IMPORTADOS


# ============================================================
# ABRIR ROTA
# ============================================================

try:

    wb, ws, clientes = abrir_planilha(
        CAMINHO_ROTA
    )

    print(
        f"{len(clientes)} clientes carregados."
    )

except Exception as erro:

    print()
    print("=" * 60)
    print("ERRO AO ABRIR A ROTA.XLSX")
    print("=" * 60)
    print(erro)
    print()

    exit()


# ============================================================
# LISTAR PDFs
# ============================================================

pdfs = listar_pdfs(
    PASTA_DANFES
)


quantidade = 0


# ============================================================
# PROCESSAR PDFs
# ============================================================

for pdf in pdfs:

    try:

        print()
        print("=" * 60)
        print(f"Processando: {pdf}")
        print("=" * 60)

        paginas = ler_pdf(pdf)

        danfes_encontradas = 0

        for indice, texto in enumerate(
            paginas,
            start=1
        ):

            if identificar_inicio_danfe(texto):

                print(
                    f"DANFE encontrada "
                    f"na página {indice}"
                )

                danfe = extrair_danfe(
                    texto
                )

                print(
                    f"NF: {danfe.numero_nf}"
                )

                print(
                    f"CNPJ: {danfe.cnpj}"
                )

                adicionar_danfe(
                    ws,
                    danfe,
                    clientes
                )

                danfes_encontradas += 1
                quantidade += 1

        # ====================================================
        # SÓ MOVE O PDF DEPOIS DE TERMINAR O PROCESSAMENTO
        # ====================================================

        if danfes_encontradas > 0:

            novo_caminho = mover_para_importados(
                pdf,
                PASTA_IMPORTADOS
            )

            print()
            print(
                "PDF importado com sucesso."
            )

            print(
                f"Movido para: {novo_caminho}"
            )

        else:

            print()
            print(
                "ATENÇÃO: nenhuma DANFE "
                "foi encontrada neste PDF."
            )

            print(
                "O arquivo NÃO será movido."
            )

    except Exception as erro:

        print()
        print("=" * 60)
        print("ERRO AO PROCESSAR PDF")
        print("=" * 60)

        print(
            f"Arquivo: {pdf}"
        )

        print(
            f"Erro: {erro}"
        )

        print(
            "O arquivo NÃO será movido."
        )

        print("=" * 60)


# ============================================================
# SALVAR ROTA
# ============================================================

try:

    salvar_planilha(
        wb,
        CAMINHO_ROTA
    )

    print()
    print("=" * 60)
    print(
        f"{quantidade} DANFE(s) "
        f"importada(s) com sucesso."
    )

    print(
        "Processamento finalizado."
    )

    print("=" * 60)

except PermissionError as erro:

    print()
    print("=" * 60)
    print("ERRO AO SALVAR A ROTA")
    print("=" * 60)

    print(erro)

    print("=" * 60)