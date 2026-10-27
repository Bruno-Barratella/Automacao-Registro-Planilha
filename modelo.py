from dataclasses import dataclass, field

@dataclass
class Danfe:
    cidade: str
    data_emissao: str
    razao_social: str
    endereco: str
    numero_notas: int
    numero_nf: str
    numero_embarque: str
    peso_bruto: str
    valor_total: str
    cnpj: str
    codigo_cliente: str

    # Novos campos usados pelo classificador.
    categoria_produtos: str = "REVISAR"

    codigos_produtos: list[str] = field(
        default_factory=list
    )

    codigos_nao_cadastrados: list[str] = field(
        default_factory=list
    )
