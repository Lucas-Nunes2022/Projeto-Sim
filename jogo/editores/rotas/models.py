from dataclasses import dataclass, asdict, field

@dataclass
class Elemento:
    tipo: str = ''
    distancia_p0: float = 0.0
    superficie: str = ''
    ordem: int = 0
    nome: str = ''
    direcao: str = ''
    angulacao: float = 0.0
    rua_direita: str = ''
    rua_esquerda: str = ''
    tipo_semaforo: str = ''
    rua_principal: str = ''   # "Direita" ou "Esquerda"

@dataclass
class Rota:
    id_rota: str = ''
    nome_rota: str = ''
    operador: str = ''
    tipo_via: str = ''
    tipo_rota: str = ''
    ponto_inicial: str = ''
    ponto_final: str = ''
    distancia_p0_pf: float = 0
    veiculos: list[str] = field(default_factory=list)
    tmp_estimado: int = 0
    tipo_trafego: str = ''
    intervalo_min: int = 0
    elementos: list[Elemento] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)
