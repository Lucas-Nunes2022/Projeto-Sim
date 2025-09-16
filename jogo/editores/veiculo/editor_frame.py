import wx 
import pathlib
import json
from cryptography.fernet import Fernet
from models import Veiculo, Motor, Sons
import constantes

APPDATA = pathlib.Path.home() / "AppData" / "Roaming" / "lucas_producoes" / "simbus"
VEHICLES_DIR = APPDATA / "vehicles"

LABEL_SONS = {
    "motor": "Som do Motor",
    "start": "Som de Partida",
    "buzina": "Som da Buzina",
    "motor_ext": "Som do Motor Externo",
    "porta_abrir": "Som Abrir Porta",
    "porta_fechar": "Som Fechar Porta",
    "seta": "Som da Seta",
    "freio_ar": "Som do Freio a Ar",
    "freio_emergencia": "Som do Freio de Emergência",
    "freio_mao": "Som do Freio de Mão",
    "campainha": "Som da Campainha",
    "ventilacao": "Som da Ventilação",
    "catraca": "Som da Catraca",
    "som_re": "Som da Marcha Ré",
    "som_rodas": "Som das Rodas",
}

class EditorFrame(wx.Frame):
    def __init__(self, *args, dados: Veiculo, pasta: pathlib.Path | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.dados = dados
        self.pasta = pasta
        self.notebook = wx.Notebook(self)
        self.page1 = wx.Panel(self.notebook)
        self.page2 = wx.Panel(self.notebook)
        self.notebook.AddPage(self.page1, "Informações Gerais")
        self.notebook.AddPage(self.page2, "Sons")
        self.build_page1()
        self.build_page2()
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        sizer_main.Add(self.notebook, 1, wx.EXPAND)
        self.SetSizer(sizer_main)
        self.SetSize((500, 700))

    def build_page1(self):
        sizer1 = wx.BoxSizer(wx.VERTICAL)
        campos = [
            ("ID:", wx.TextCtrl, {"value": self.dados.id}, "id"),
            ("Nome:", wx.TextCtrl, {"value": self.dados.nome}, "nome"),
            ("Fabricante:", wx.TextCtrl, {"value": self.dados.fabricante}, "fabricante"),
            ("Ano:", wx.SpinCtrl, {"min": 1900, "max": 2100, "initial": self.dados.ano if 1900 <= self.dados.ano <= 2100 else 1900}, "ano"),
            ("Tipo:", wx.ComboBox, {"choices": ["Micro", "Padrão", "Biarticulado", "Super Articulado"], "style": wx.CB_READONLY, "value": self.dados.tipo}, "tipo"),
            ("Câmbio:", wx.ComboBox, {"choices": ["Manual", "Automático", "Automatizado"], "style": wx.CB_READONLY, "value": self.dados.cambio}, "cambio"),
            ("Quantidade de Marchas:", wx.SpinCtrl, {"min": 0, "max": 12, "initial": self.dados.qtd_marchas}, "qtd_marchas"),
            ("Comprimento (m):", wx.TextCtrl, {"value": str(self.dados.comprimento_m)}, "comprimento"),
            ("Número de Portas:", wx.SpinCtrl, {"min": 0, "max": 5, "initial": self.dados.portas}, "portas"),
            ("Capacidade de Passageiros:", wx.SpinCtrl, {"min": 0, "max": 300, "initial": self.dados.capacidade}, "capacidade"),
            ("Peso (kg):", wx.SpinCtrl, {"min": 0, "max": 100000, "initial": self.dados.peso}, "peso"),
            ("Altura (cm):", wx.SpinCtrl, {"min": 0, "max": 1000, "initial": self.dados.altura}, "altura"),
            ("Largura (cm):", wx.SpinCtrl, {"min": 0, "max": 1000, "initial": self.dados.largura}, "largura"),
            ("Capacidade do Tanque (L):", wx.SpinCtrl, {"min": 0, "max": 2000, "initial": self.dados.cap_tanque}, "cap_tanque"),
            ("Quantidade de Eixos:", wx.SpinCtrl, {"min": 0, "max": 10, "initial": self.dados.qtd_eixos}, "qtd_eixos"),
            ("Posição do Motor:", wx.ComboBox, {"choices": ["Frontal", "Traseiro"], "style": wx.CB_READONLY, "value": self.dados.motor.posicao}, "motor_posicao"),
            ("Potência do Motor (CV):", wx.SpinCtrl, {"min": 0, "max": 2000, "initial": self.dados.motor.potencia_cv}, "motor_potencia"),
            ("Combustível do Motor:", wx.ComboBox, {"choices": ["Diesel", "Elétrico", "Bateria"], "style": wx.CB_READONLY, "value": self.dados.motor.combustivel}, "motor_combustivel"),
            ("Velocidade Máxima (km/h):", wx.SpinCtrl, {"min": 0, "max": 200, "initial": self.dados.motor.velocidade_max_kmh}, "motor_vel"),
            ("Torque do Motor (Nm):", wx.SpinCtrl, {"min": 0, "max": 5000, "initial": self.dados.motor.torque}, "motor_torque"),
            ("Consumo Médio (L/km):", wx.TextCtrl, {"value": str(self.dados.motor.t_consumo)}, "motor_consumo")
        ]
        for label, widget, kwargs, attr in campos:
            lbl = wx.StaticText(self.page1, label=label)
            ctrl = widget(self.page1, **kwargs)
            setattr(self, attr, ctrl)
            sizer1.Add(lbl, 0, wx.EXPAND | wx.ALL, 5)
            sizer1.Add(ctrl, 0, wx.EXPAND | wx.ALL, 5)
        self.page1.SetSizer(sizer1)

    def build_page2(self):
        sizer2 = wx.BoxSizer(wx.VERTICAL)
        for attr in Sons().__dict__.keys():
            label = LABEL_SONS.get(attr, f"Som {attr}")
            lbl = wx.StaticText(self.page2, label=f"{label}:")
            ctrl = wx.TextCtrl(self.page2, value=self._resolve_path(getattr(self.dados.sons, attr)))
            btn = wx.Button(self.page2, label=f"Selecionar {label}")
            btn.Bind(wx.EVT_BUTTON, lambda evt, c=ctrl: self.escolher_arquivo(c))
            setattr(self, f"som_{attr}", ctrl)
            sizer2.Add(lbl, 0, wx.EXPAND | wx.ALL, 5)
            sizer2.Add(ctrl, 0, wx.EXPAND | wx.ALL, 5)
            sizer2.Add(btn, 0, wx.EXPAND | wx.ALL, 5)
        btn_salvar = wx.Button(self.page2, label="Salvar")
        btn_salvar.Bind(wx.EVT_BUTTON, self.salvar)
        btn_cancelar2 = wx.Button(self.page2, label="Cancelar")
        btn_cancelar2.Bind(wx.EVT_BUTTON, lambda evt: self.Close())
        sizer2.Add(btn_salvar, 0, wx.EXPAND | wx.ALL, 5)
        sizer2.Add(btn_cancelar2, 0, wx.EXPAND | wx.ALL, 5)
        self.page2.SetSizer(sizer2)

    def _resolve_path(self, filename: str) -> str:
        if not filename or not self.pasta:
            return filename or ""
        pasta_sons = self.pasta / "sounds"
        return str(pasta_sons / filename) if filename else ""

    def escolher_arquivo(self, ctrl):
        with wx.FileDialog(None, "Escolha um som", wildcard="Arquivos WAV (*.wav)|*.wav",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                ctrl.SetValue(dlg.GetPath())

    def salvar(self, event):
        if not self.id.GetValue().strip() or not self.nome.GetValue().strip():
            wx.MessageBox("ID e Nome não podem estar vazios!", "Erro")
            return
        sons_dict = {}
        for attr in Sons().__dict__.keys():
            val = getattr(self, f"som_{attr}").GetValue()
            sons_dict[attr] = pathlib.Path(val).name if val else ""
        v = Veiculo(
            id=self.id.GetValue().strip(),
            nome=self.nome.GetValue().strip(),
            fabricante=self.fabricante.GetValue().strip(),
            ano=self.ano.GetValue(),
            tipo=self.tipo.GetValue().strip(),
            cambio=self.cambio.GetValue().strip(),
            qtd_marchas=self.qtd_marchas.GetValue(),
            comprimento_m=float(self.comprimento.GetValue()),
            portas=self.portas.GetValue(),
            capacidade=self.capacidade.GetValue(),
            peso=self.peso.GetValue(),
            altura=self.altura.GetValue(),
            largura=self.largura.GetValue(),
            cap_tanque=self.cap_tanque.GetValue(),
            qtd_eixos=self.qtd_eixos.GetValue(),
            motor=Motor(
                posicao=self.motor_posicao.GetValue(),
                potencia_cv=self.motor_potencia.GetValue(),
                combustivel=self.motor_combustivel.GetValue(),
                velocidade_max_kmh=self.motor_vel.GetValue(),
                torque=self.motor_torque.GetValue(),
                t_consumo=float(self.motor_consumo.GetValue() or 0)
            ),
            sons=Sons(**sons_dict)
        )
        pasta_veiculo = VEHICLES_DIR / v.id
        pasta_sons = pasta_veiculo / "sounds"
        if pasta_veiculo.exists() and not self.dados.id:
            wx.MessageBox("Já existe um veículo com esse ID!", "Erro")
            return
        pasta_veiculo.mkdir(parents=True, exist_ok=True)
        pasta_sons.mkdir(parents=True, exist_ok=True)
        for attr, filename in sons_dict.items():
            src = getattr(self, f"som_{attr}").GetValue()
            if src and pathlib.Path(src).exists():
                dest = pasta_sons / filename
                pathlib.Path(dest).write_bytes(pathlib.Path(src).read_bytes())
        dados_json = json.dumps(v.to_dict(), indent=2, ensure_ascii=False)
        fernet = Fernet(constantes.FERNET_KEY)
        dados_enc = fernet.encrypt(dados_json.encode()).decode()
        arquivo_vel = pasta_veiculo / f"{v.id}.vel"
        arquivo_vel.write_text(dados_enc, encoding="utf-8")
        wx.MessageBox(f"Veículo salvo em {arquivo_vel}", "Sucesso")
