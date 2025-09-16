from dataclasses import dataclass, asdict, field

@dataclass
class Motor:
    posicao: str = ''
    potencia_cv: int = 0
    combustivel: str = ''
    velocidade_max_kmh: int = 0
    t_consumo: float = 0.0
    torque: int = 0

@dataclass
class Sons:
    motor: str = ''
    start: str = ''
    buzina: str = ''
    motor_ext: str = ''
    porta_abrir: str = ''
    porta_fechar: str = ''
    seta: str = ''
    freio_ar: str = ''
    freio_emergencia: str = ''
    freio_mao: str = ''
    campainha: str = ''
    ventilacao: str = ''
    catraca: str = ''
    som_re: str = ''
    som_rodas: str = ''
    
@dataclass
class Veiculo:
    id: str = ''
    nome: str = ''
    fabricante: str = ''
    ano: int = 0
    tipo: str = ''
    cambio: str = ''
    qtd_marchas: int = 0
    comprimento_m: float = 0
    portas: int = 0
    capacidade: int = 0
    peso: int = 0
    altura: int = 0
    largura: int = 0
    cap_tanque: int = 0
    qtd_eixos: int = 0

    motor: Motor = field(default_factory=Motor)
    sons: Sons = field(default_factory=Sons)

    @property
    def autonomia(self) -> float:
        if self.motor.t_consumo and self.cap_tanque > 0:
            return self.cap_tanque * float(self.motor.t_consumo)
        return 0.0

    def to_dict(self):
        d = asdict(self)
        d["autonomia"] = self.autonomia
        return d
