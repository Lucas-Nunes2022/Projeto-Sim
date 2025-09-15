import wx
import json
import constantes
from cryptography.fernet import Fernet
import pathlib
import os
from dataclasses import dataclass, asdict

APPDATA = pathlib.Path(os.getenv("APPDATA")) / "lucas_producoes" / "simbus"
VEHICLES_DIR = APPDATA / "vehicles"

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

@dataclass
class Veiculo:
    id: str = ''
    nome: str = ''
    tipo: str = ''
    comprimento_m: float = 0
    portas: int = 0
    capacidade: int = 0
    motor: Motor = Motor()
    sons: Sons = Sons()
    def to_dict(self):
        return asdict(self)

class Editor(wx.App):
    def OnInit(self):
        choices = ("Criar novo veículo", "Editar veículo existente")
        dlg = wx.SingleChoiceDialog(None, "Escolha uma opção:", "Editor de Veículos", choices)
        action = None
        if dlg.ShowModal() == wx.ID_OK:
            action = dlg.GetStringSelection()
        dlg.Destroy()
        if action == "Criar novo veículo":
            frame = EditorFrame(None, title="Criar veículo", dados=Veiculo())
        elif action == "Editar veículo existente":
            with wx.DirDialog(
                None,
                "Escolha a pasta do veículo",
                defaultPath=str(VEHICLES_DIR),
                style=wx.DD_DIR_MUST_EXIST
            ) as dirDialog:
                if dirDialog.ShowModal() == wx.ID_CANCEL:
                    return False
                pasta = pathlib.Path(dirDialog.GetPath())
                vel_files = list(pasta.glob("*.vel"))
                if not vel_files:
                    wx.MessageBox("Nenhum arquivo .vel encontrado na pasta!", "Erro")
                    return False
                caminho = vel_files[0]
                dados_enc = caminho.read_text(encoding="utf-8")
                fernet = Fernet(constantes.FERNET_KEY)
                dados_json = fernet.decrypt(dados_enc.encode()).decode()
                d = json.loads(dados_json)
                v = Veiculo(
                    id=d.get("id",""),
                    nome=d.get("nome",""),
                    tipo=d.get("tipo",""),
                    comprimento_m=d.get("comprimento_m",0),
                    portas=d.get("portas",0),
                    capacidade=d.get("capacidade",0),
                    motor=Motor(**d.get("motor",{})),
                    sons=Sons(**d.get("sons",{}))
                )
                pasta_sons = pasta / "sounds"
                if pasta_sons.exists():
                    if v.sons.motor: v.sons.motor = str(pasta_sons / v.sons.motor)
                    if v.sons.porta_abrir: v.sons.porta_abrir = str(pasta_sons / v.sons.porta_abrir)
                    if v.sons.porta_fechar: v.sons.porta_fechar = str(pasta_sons / v.sons.porta_fechar)
                    if v.sons.seta: v.sons.seta = str(pasta_sons / v.sons.seta)
                    if v.sons.freio_ar: v.sons.freio_ar = str(pasta_sons / v.sons.freio_ar)
                frame = EditorFrame(None, title=f"Editar {v.nome}", dados=v)
        else:
            return False
        frame.Show()
        return True

class EditorFrame(wx.Frame):
    def __init__(self, *args, dados: Veiculo, **kwargs):
        super().__init__(*args, **kwargs)
        self.dados = dados
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.id = wx.TextCtrl(panel, value=self.dados.id)
        self.nome = wx.TextCtrl(panel, value=self.dados.nome)
        self.tipo = wx.ComboBox(panel, choices=["micro", "padrao", "biarticulado", "super_articulado"],
                                style=wx.CB_READONLY, value=self.dados.tipo)
        self.comprimento = wx.TextCtrl(panel, value=str(self.dados.comprimento_m))
        self.portas = wx.SpinCtrl(panel, min=0, max=5, initial=self.dados.portas)
        self.capacidade = wx.SpinCtrl(panel, min=0, max=300, initial=self.dados.capacidade)

        self.motor_posicao = wx.ComboBox(panel, choices=["frontal", "traseiro"],
                                         style=wx.CB_READONLY, value=self.dados.motor.posicao)
        self.motor_potencia = wx.SpinCtrl(panel, min=0, max=2000, initial=self.dados.motor.potencia_cv)
        self.motor_combustivel = wx.ComboBox(panel, choices=["diesel", "eletrico", "bateria"],
                                             style=wx.CB_READONLY, value=self.dados.motor.combustivel)
        self.motor_vel = wx.SpinCtrl(panel, min=0, max=200, initial=self.dados.motor.velocidade_max_kmh)

        self.som_motor = wx.TextCtrl(panel, value=self.dados.sons.motor)
        btn_motor = wx.Button(panel, label="Selecionar Som Motor")
        btn_motor.Bind(wx.EVT_BUTTON, lambda evt: self.escolher_arquivo(self.som_motor))

        self.som_porta_abrir = wx.TextCtrl(panel, value=self.dados.sons.porta_abrir)
        btn_porta_abrir = wx.Button(panel, label="Selecionar Som Porta Abrir")
        btn_porta_abrir.Bind(wx.EVT_BUTTON, lambda evt: self.escolher_arquivo(self.som_porta_abrir))

        self.som_porta_fechar = wx.TextCtrl(panel, value=self.dados.sons.porta_fechar)
        btn_porta_fechar = wx.Button(panel, label="Selecionar Som Porta Fechar")
        btn_porta_fechar.Bind(wx.EVT_BUTTON, lambda evt: self.escolher_arquivo(self.som_porta_fechar))

        self.som_seta = wx.TextCtrl(panel, value=self.dados.sons.seta)
        btn_seta = wx.Button(panel, label="Selecionar Som Seta")
        btn_seta.Bind(wx.EVT_BUTTON, lambda evt: self.escolher_arquivo(self.som_seta))

        self.som_freio_ar = wx.TextCtrl(panel, value=self.dados.sons.freio_ar)
        btn_freio_ar = wx.Button(panel, label="Selecionar Som Freio Ar")
        btn_freio_ar.Bind(wx.EVT_BUTTON, lambda evt: self.escolher_arquivo(self.som_freio_ar))

        salvar_btn = wx.Button(panel, label="Salvar")
        salvar_btn.Bind(wx.EVT_BUTTON, self.salvar)

        campos = [
            ("ID:", self.id),
            ("Nome:", self.nome),
            ("Tipo:", self.tipo),
            ("Comprimento (m):", self.comprimento),
            ("Portas:", self.portas),
            ("Capacidade:", self.capacidade),
            ("Motor - Posição:", self.motor_posicao),
            ("Motor - Potência (CV):", self.motor_potencia),
            ("Motor - Combustível:", self.motor_combustivel),
            ("Motor - Velocidade Máx (km/h):", self.motor_vel),
        ]
        for label, widget in campos:
            sizer.Add(wx.StaticText(panel, label=label), 0, wx.ALL, 5)
            sizer.Add(widget, 0, wx.EXPAND | wx.ALL, 5)

        for label, ctrl, btn in [
            ("Som Motor:", self.som_motor, btn_motor),
            ("Som Porta Abrir:", self.som_porta_abrir, btn_porta_abrir),
            ("Som Porta Fechar:", self.som_porta_fechar, btn_porta_fechar),
            ("Som Seta:", self.som_seta, btn_seta),
            ("Som Freio Ar:", self.som_freio_ar, btn_freio_ar)
        ]:
            sizer.Add(wx.StaticText(panel, label=label), 0, wx.ALL, 5)
            sizer.Add(ctrl, 0, wx.EXPAND | wx.ALL, 5)
            sizer.Add(btn, 0, wx.ALL, 5)

        sizer.Add(salvar_btn, 0, wx.ALL | wx.CENTER, 10)
        panel.SetSizer(sizer)
        self.SetSize((450, 800))

    def escolher_arquivo(self, ctrl):
        with wx.FileDialog(None, "Escolha um som", wildcard="Arquivos WAV (*.wav)|*.wav",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                ctrl.SetValue(dlg.GetPath())

    def salvar(self, event):
        if not self.id.GetValue().strip() or not self.nome.GetValue().strip():
            wx.MessageBox("ID e Nome não podem estar vazios!", "Erro")
            return

        v = Veiculo(
            id=self.id.GetValue().strip(),
            nome=self.nome.GetValue().strip(),
            tipo=self.tipo.GetValue().strip(),
            comprimento_m=float(self.comprimento.GetValue()),
            portas=self.portas.GetValue(),
            capacidade=self.capacidade.GetValue(),
            motor=Motor(
                posicao=self.motor_posicao.GetValue(),
                potencia_cv=self.motor_potencia.GetValue(),
                combustivel=self.motor_combustivel.GetValue(),
                velocidade_max_kmh=self.motor_vel.GetValue()
            ),
            sons=Sons(
                motor=pathlib.Path(self.som_motor.GetValue()).name if self.som_motor.GetValue() else "",
                porta_abrir=pathlib.Path(self.som_porta_abrir.GetValue()).name if self.som_porta_abrir.GetValue() else "",
                porta_fechar=pathlib.Path(self.som_porta_fechar.GetValue()).name if self.som_porta_fechar.GetValue() else "",
                seta=pathlib.Path(self.som_seta.GetValue()).name if self.som_seta.GetValue() else "",
                freio_ar=pathlib.Path(self.som_freio_ar.GetValue()).name if self.som_freio_ar.GetValue() else ""
            )
        )

        pasta_veiculo = VEHICLES_DIR / v.id
        pasta_sons = pasta_veiculo / "sounds"

        if pasta_veiculo.exists() and not self.dados.id:
            wx.MessageBox("Já existe um veículo com esse ID!", "Erro")
            return

        pasta_veiculo.mkdir(parents=True, exist_ok=True)
        pasta_sons.mkdir(parents=True, exist_ok=True)

        for src, dest in [
            (self.som_motor.GetValue(), pasta_sons / v.sons.motor),
            (self.som_porta_abrir.GetValue(), pasta_sons / v.sons.porta_abrir),
            (self.som_porta_fechar.GetValue(), pasta_sons / v.sons.porta_fechar),
            (self.som_seta.GetValue(), pasta_sons / v.sons.seta),
            (self.som_freio_ar.GetValue(), pasta_sons / v.sons.freio_ar),
        ]:
            if src and pathlib.Path(src).exists():
                pathlib.Path(dest).write_bytes(pathlib.Path(src).read_bytes())

        dados_json = json.dumps(v.to_dict(), indent=2, ensure_ascii=False)
        fernet = Fernet(constantes.FERNET_KEY)
        dados_enc = fernet.encrypt(dados_json.encode()).decode()
        arquivo_vel = pasta_veiculo / f"{v.id}.vel"
        arquivo_vel.write_text(dados_enc, encoding="utf-8")

        wx.MessageBox(f"Veículo salvo em {arquivo_vel}", "Sucesso")

app = Editor(False)
app.MainLoop()
