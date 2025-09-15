import wx
import pathlib
import json
from cryptography.fernet import Fernet
from models import Veiculo, Motor, Sons
import constantes

APPDATA = pathlib.Path.home() / "AppData" / "Roaming" / "lucas_producoes" / "simbus"
VEHICLES_DIR = APPDATA / "vehicles"

class EditorFrame(wx.Frame):
    def __init__(self, *args, dados: Veiculo, pasta: pathlib.Path | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.dados = dados
        self.pasta = pasta
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        lbl_id = wx.StaticText(panel, label="ID:")
        self.id = wx.TextCtrl(panel, value=self.dados.id)

        lbl_nome = wx.StaticText(panel, label="Nome:")
        self.nome = wx.TextCtrl(panel, value=self.dados.nome)

        lbl_tipo = wx.StaticText(panel, label="Tipo:")
        self.tipo = wx.ComboBox(panel, choices=["micro", "padrão", "biarticulado", "super_articulado"],
                                style=wx.CB_READONLY, value=self.dados.tipo)

        lbl_comprimento = wx.StaticText(panel, label="Comprimento (m):")
        self.comprimento = wx.TextCtrl(panel, value=str(self.dados.comprimento_m))

        lbl_portas = wx.StaticText(panel, label="Portas:")
        self.portas = wx.SpinCtrl(panel, min=0, max=5, initial=self.dados.portas)

        lbl_capacidade = wx.StaticText(panel, label="Capacidade:")
        self.capacidade = wx.SpinCtrl(panel, min=0, max=300, initial=self.dados.capacidade)

        lbl_motor_posicao = wx.StaticText(panel, label="Motor - Posição:")
        self.motor_posicao = wx.ComboBox(panel, choices=["frontal", "traseiro"],
                                         style=wx.CB_READONLY, value=self.dados.motor.posicao)

        lbl_motor_potencia = wx.StaticText(panel, label="Motor - Potência (CV):")
        self.motor_potencia = wx.SpinCtrl(panel, min=0, max=2000, initial=self.dados.motor.potencia_cv)

        lbl_motor_combustivel = wx.StaticText(panel, label="Motor - Combustível:")
        self.motor_combustivel = wx.ComboBox(panel, choices=["diesel", "eletrico", "bateria"],
                                             style=wx.CB_READONLY, value=self.dados.motor.combustivel)

        lbl_motor_vel = wx.StaticText(panel, label="Motor - Velocidade Máx (km/h):")
        self.motor_vel = wx.SpinCtrl(panel, min=0, max=200, initial=self.dados.motor.velocidade_max_kmh)

        lbl_som_motor = wx.StaticText(panel, label="Som Motor:")
        self.som_motor = wx.TextCtrl(panel, value=self._resolve_path(self.dados.sons.motor))
        btn_motor = wx.Button(panel, label="Selecionar Som Motor")
        btn_motor.Bind(wx.EVT_BUTTON, lambda evt: self.escolher_arquivo(self.som_motor))

        lbl_som_porta_abrir = wx.StaticText(panel, label="Som Porta Abrir:")
        self.som_porta_abrir = wx.TextCtrl(panel, value=self._resolve_path(self.dados.sons.porta_abrir))
        btn_porta_abrir = wx.Button(panel, label="Selecionar Som Porta Abrir")
        btn_porta_abrir.Bind(wx.EVT_BUTTON, lambda evt: self.escolher_arquivo(self.som_porta_abrir))

        lbl_som_porta_fechar = wx.StaticText(panel, label="Som Porta Fechar:")
        self.som_porta_fechar = wx.TextCtrl(panel, value=self._resolve_path(self.dados.sons.porta_fechar))
        btn_porta_fechar = wx.Button(panel, label="Selecionar Som Porta Fechar")
        btn_porta_fechar.Bind(wx.EVT_BUTTON, lambda evt: self.escolher_arquivo(self.som_porta_fechar))

        lbl_som_seta = wx.StaticText(panel, label="Som Seta:")
        self.som_seta = wx.TextCtrl(panel, value=self._resolve_path(self.dados.sons.seta))
        btn_seta = wx.Button(panel, label="Selecionar Som Seta")
        btn_seta.Bind(wx.EVT_BUTTON, lambda evt: self.escolher_arquivo(self.som_seta))

        lbl_som_freio_ar = wx.StaticText(panel, label="Som Freio Ar:")
        self.som_freio_ar = wx.TextCtrl(panel, value=self._resolve_path(self.dados.sons.freio_ar))
        btn_freio_ar = wx.Button(panel, label="Selecionar Som Freio Ar")
        btn_freio_ar.Bind(wx.EVT_BUTTON, lambda evt: self.escolher_arquivo(self.som_freio_ar))

        lbl_som_ventilacao = wx.StaticText(panel, label="Som Ventilação:")
        self.som_ventilacao = wx.TextCtrl(panel, value=self._resolve_path(self.dados.sons.ventilacao))
        btn_ventilacao = wx.Button(panel, label="Selecionar Som Ventilação")
        btn_ventilacao.Bind(wx.EVT_BUTTON, lambda evt: self.escolher_arquivo(self.som_ventilacao))

        lbl_som_catraca = wx.StaticText(panel, label="Som Catraca:")
        self.som_catraca = wx.TextCtrl(panel, value=self._resolve_path(self.dados.sons.catraca))
        btn_catraca = wx.Button(panel, label="Selecionar Som Catraca")
        btn_catraca.Bind(wx.EVT_BUTTON, lambda evt: self.escolher_arquivo(self.som_catraca))

        salvar_btn = wx.Button(panel, label="Salvar")
        salvar_btn.Bind(wx.EVT_BUTTON, self.salvar)

        for w in [
            lbl_id, self.id,
            lbl_nome, self.nome,
            lbl_tipo, self.tipo,
            lbl_comprimento, self.comprimento,
            lbl_portas, self.portas,
            lbl_capacidade, self.capacidade,
            lbl_motor_posicao, self.motor_posicao,
            lbl_motor_potencia, self.motor_potencia,
            lbl_motor_combustivel, self.motor_combustivel,
            lbl_motor_vel, self.motor_vel,
            lbl_som_motor, self.som_motor, btn_motor,
            lbl_som_porta_abrir, self.som_porta_abrir, btn_porta_abrir,
            lbl_som_porta_fechar, self.som_porta_fechar, btn_porta_fechar,
            lbl_som_seta, self.som_seta, btn_seta,
            lbl_som_freio_ar, self.som_freio_ar, btn_freio_ar,
            lbl_som_ventilacao, self.som_ventilacao, btn_ventilacao,
            lbl_som_catraca, self.som_catraca, btn_catraca,
            salvar_btn
        ]:
            sizer.Add(w, 0, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(sizer)
        self.SetSize((500, 1000))

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
                freio_ar=pathlib.Path(self.som_freio_ar.GetValue()).name if self.som_freio_ar.GetValue() else "",
                ventilacao=pathlib.Path(self.som_ventilacao.GetValue()).name if self.som_ventilacao.GetValue() else "",
                catraca=pathlib.Path(self.som_catraca.GetValue()).name if self.som_catraca.GetValue() else ""
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
            (self.som_ventilacao.GetValue(), pasta_sons / v.sons.ventilacao),
            (self.som_catraca.GetValue(), pasta_sons / v.sons.catraca),
        ]:
            if src and pathlib.Path(src).exists():
                pathlib.Path(dest).write_bytes(pathlib.Path(src).read_bytes())

        dados_json = json.dumps(v.to_dict(), indent=2, ensure_ascii=False)
        fernet = Fernet(constantes.FERNET_KEY)
        dados_enc = fernet.encrypt(dados_json.encode()).decode()
        arquivo_vel = pasta_veiculo / f"{v.id}.vel"
        arquivo_vel.write_text(dados_enc, encoding="utf-8")

        wx.MessageBox(f"Veículo salvo em {arquivo_vel}", "Sucesso")
