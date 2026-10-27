
from classificador_produtos import (
    normalizar_codigo,
    classificar_categorias,
    extrair_codigos_danfe,
    carregar_cadastro,
)

cadastro = carregar_cadastro()

print("Produtos carregados:", len(cadastro))

print("Código 050773:", normalizar_codigo("050773"))
print("Código 50773:", normalizar_codigo("50773"))

print(
    "Somente BIMBO:",
    classificar_categorias(["BIMBO"])
)

print(
    "LEITE + XANDO:",
    classificar_categorias(["LEITE", "XANDO"])
)

print(
    "BIMBO + MDIAS:",
    classificar_categorias(["BIMBO", "MDIAS"])
)

texto_teste = """
DADOS DOS PRODUTO / SERVIÇOS
050773 PRODUTO DE TESTE
DADOS ADICIONAIS
"""

codigos = extrair_codigos_danfe(texto_teste)
print("Códigos extraídos:", codigos)
