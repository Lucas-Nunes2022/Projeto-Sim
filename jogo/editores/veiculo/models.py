from dataclasses import dataclass, asdict, field

@dataclass
class Motor:
    posicao: str = ''
    potencia_cv: int = 0
    combustivel: str = ''
    velocidade_max_kmh: int = 0

@dataclass
class Sons:
    motor: str = ''
    porta_abrir: str = ''
    porta_fechar: str = ''
    seta: str = ''
    freio_ar: str = ''
    ventilacao: str = ''
    catraca: str = ''

@dataclass
class Veiculo:
    id: str = ''
    nome: str = ''
    tipo: str = ''
    comprimento_m: float = 0
    portas: int = 0
    capacidade: int = 0
    motor: Motor = field(default_factory=Motor)
    sons: Sons = field(default_factory=Sons)

    def to_dict(self):
        return asdict(self)
