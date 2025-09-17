import wx
import pathlib
import json
from cryptography.fernet import Fernet
from models import Rota, Elemento
import constantes

APPDATA = pathlib.Path.home() / "AppData" / "Roaming" / "lucas_producoes" / "simbus"
ROUTES_DIR = APPDATA / "routes"
VEHICLES_DIR = APPDATA / "vehicles"

class LabelAccessible(wx.Accessible):
    def __init__(self, text):
        super().__init__()
        self.text = text
    def GetName(self, childId):
        return (wx.ACC_OK, self.text)

class EditorRotaFrame(wx.Frame):
    def __init__(self, *args, dados: Rota, pasta: pathlib.Path | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.dados = dados
        self.pasta = pasta
        self.notebook = wx.Notebook(self)
        self.page1 = wx.Panel(self.notebook)
        self.page2 = wx.Panel(self.notebook)
        self.page3 = wx.Panel(self.notebook)
        self.notebook.AddPage(self.page1, "Informações Gerais")
        self.notebook.AddPage(self.page2, "Elementos")
        self.notebook.AddPage(self.page3, "Veículos")
        self.build_page1()
        self.build_page2()
        self.build_page3()
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        sizer_main.Add(self.notebook, 1, wx.EXPAND)
        self.SetSizer(sizer_main)
        self.SetSize((600, 700))

    def build_page1(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        campos = [
            ("ID da Rota:", wx.TextCtrl, {"value": self.dados.id_rota}, "id_rota"),
            ("Nome da Rota:", wx.TextCtrl, {"value": self.dados.nome_rota}, "nome_rota"),
            ("Operador:", wx.TextCtrl, {"value": self.dados.operador}, "operador"),
            ("Tipo de Via:", wx.ComboBox, {"choices": ["Urbana", "Rodovia"], "style": wx.CB_READONLY, "value": self.dados.tipo_via}, "tipo_via"),
            ("Tipo de Rota:", wx.ComboBox, {"choices": ["Municipal", "Intermunicipal", "Circular"], "style": wx.CB_READONLY, "value": self.dados.tipo_rota}, "tipo_rota"),
            ("Ponto Inicial:", wx.TextCtrl, {"value": self.dados.ponto_inicial}, "ponto_inicial"),
            ("Ponto Final:", wx.TextCtrl, {"value": self.dados.ponto_final}, "ponto_final"),
            ("Distância total (km):", wx.TextCtrl, {"value": str(self.dados.distancia_p0_pf)}, "distancia"),
            ("Tempo Estimado (min):", wx.SpinCtrl, {"min": 0, "max": 600, "initial": self.dados.tmp_estimado}, "tmp_estimado"),
            ("Intervalo (min):", wx.SpinCtrl, {"min": 0, "max": 120, "initial": self.dados.intervalo_min}, "intervalo_min"),
        ]
        for label, widget, kwargs, attr in campos:
            lbl = wx.StaticText(self.page1, label=label)
            ctrl = widget(self.page1, **kwargs)
            label_text = label.rstrip(":")
            ctrl.SetAccessible(LabelAccessible(label_text))
            setattr(self, attr, ctrl)
            sizer.Add(lbl, 0, wx.ALL, 5)
            sizer.Add(ctrl, 0, wx.EXPAND | wx.ALL, 5)
        btn_proximo = wx.Button(self.page1, label="&Próximo")
        btn_proximo.Bind(wx.EVT_BUTTON, lambda evt: self.notebook.SetSelection(1))
        sizer.AddStretchSpacer(1)
        sizer.Add(btn_proximo, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        self.page1.SetSizer(sizer)

    def build_page2(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.tipo_elem = wx.ComboBox(self.page2, choices=["Rua", "Curva", "Semáforo", "Parada", "Esquina"], style=wx.CB_READONLY)
        self.nome_elem = wx.TextCtrl(self.page2)
        self.superficie_elem = wx.ComboBox(self.page2, choices=["Asfalto liso", "Asfalto com buracos", "Estrada de chão", "Grama"], style=wx.CB_READONLY)
        self.dist_elem = wx.TextCtrl(self.page2)
        self.direcao_elem = wx.ComboBox(self.page2, choices=["Direita", "Esquerda"], style=wx.CB_READONLY)
        self.angulacao_elem = wx.TextCtrl(self.page2)
        self.rua_dir_elem = wx.TextCtrl(self.page2)
        self.rua_esq_elem = wx.TextCtrl(self.page2)
        self.tipo_semaforo_elem = wx.ComboBox(self.page2, choices=["Veicular", "Pedestre", "Inteligente"], style=wx.CB_READONLY)
        self.rua_principal = wx.ComboBox(self.page2, choices=["Direita", "Esquerda", "Reto"], style=wx.CB_READONLY)
        pairs = [
            ("Tipo do Elemento:", "tipo_elem", self.tipo_elem),
            ("Nome (Rua/Parada):", "nome_elem", self.nome_elem),
            ("Superfície:", "superficie_elem", self.superficie_elem),
            ("Distância de P0 (km):", "dist_elem", self.dist_elem),
            ("Direção da curva:", "direcao_elem", self.direcao_elem),
            ("Ângulo da curva (graus):", "angulacao_elem", self.angulacao_elem),
            ("Rua à Direita:", "rua_dir_elem", self.rua_dir_elem),
            ("Rua à Esquerda:", "rua_esq_elem", self.rua_esq_elem),
            ("Tipo de Semáforo:", "tipo_semaforo_elem", self.tipo_semaforo_elem),
        ]
        self.labels_page2 = {}
        self.controls_page2 = {}
        for text, key, ctrl in pairs:
            lbl = wx.StaticText(self.page2, label=text)
            label_text = text.rstrip(":")
            ctrl.SetAccessible(LabelAccessible(label_text))
            self.labels_page2[key] = lbl
            self.controls_page2[key] = ctrl
            sizer.Add(lbl, 0, wx.ALL, 5)
            sizer.Add(ctrl, 0, wx.EXPAND | wx.ALL, 5)
        self.rua_principal.SetAccessible(LabelAccessible("Rota segue por"))
        sizer.Add(self.rua_principal, 0, wx.ALL | wx.EXPAND, 5)
        self.tipo_elem.Bind(wx.EVT_COMBOBOX, self.on_tipo_elem_changed)
        btn_add_elem = wx.Button(self.page2, label="Adicionar Elemento")
        btn_add_elem.Bind(wx.EVT_BUTTON, self.add_elemento)
        sizer.Add(btn_add_elem, 0, wx.ALL, 5)
        self.lista_elementos = wx.ListBox(self.page2, choices=[self._format_elem(e) for e in self.dados.elementos])
        sizer.Add(self.lista_elementos, 1, wx.EXPAND | wx.ALL, 5)
        btn_edit_elem = wx.Button(self.page2, label="Editar")
        btn_edit_elem.Bind(wx.EVT_BUTTON, self.edit_elemento)
        sizer.Add(btn_edit_elem, 0, wx.ALL, 5)
        btn_remove_elem = wx.Button(self.page2, label="Remover")
        btn_remove_elem.Bind(wx.EVT_BUTTON, self.remove_elemento)
        sizer.Add(btn_remove_elem, 0, wx.ALL, 5)
        self.page2.SetSizer(sizer)
        self.on_tipo_elem_changed(None)

    def on_tipo_elem_changed(self, event):
        for key in self.labels_page2:
            self.labels_page2[key].Hide()
            self.controls_page2[key].Hide()
        self.rua_principal.Hide()
        tipo = self.tipo_elem.GetValue()
        show = ["tipo_elem", "dist_elem"]
        if tipo == "Rua":
            show += ["nome_elem", "superficie_elem"]
            self.controls_page2["nome_elem"].SetAccessible(LabelAccessible("Nome da Rua"))
        if tipo == "Parada":
            show += ["nome_elem"]
            self.controls_page2["nome_elem"].SetAccessible(LabelAccessible("Nome da Parada"))
        if tipo == "Curva":
            show += ["direcao_elem", "angulacao_elem", "superficie_elem"]
        if tipo == "Esquina":
            show += ["rua_dir_elem", "rua_esq_elem"]
        if tipo == "Semáforo":
            show += ["tipo_semaforo_elem"]
        for key in show:
            self.labels_page2[key].Show()
            self.controls_page2[key].Show()
        if tipo == "Esquina":
            self.rua_principal.Show()
        self.page2.Layout()

    def build_page3(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.lista_veiculos = wx.ListBox(self.page3, choices=self._carregar_veiculos())
        sizer.Add(self.lista_veiculos, 1, wx.EXPAND | wx.ALL, 5)
        btn_add = wx.Button(self.page3, label="Adicionar à rota")
        btn_add.Bind(wx.EVT_BUTTON, self.add_veiculo)
        sizer.Add(btn_add, 0, wx.ALL, 5)
        btn_salvar = wx.Button(self.page3, label="&Salvar Rota")
        btn_salvar.Bind(wx.EVT_BUTTON, self.salvar)
        sizer.Add(btn_salvar, 0, wx.ALL, 5)
        btn_cancelar = wx.Button(self.page3, label="&Cancelar")
        btn_cancelar.Bind(wx.EVT_BUTTON, lambda evt: self.Close())
        sizer.Add(btn_cancelar, 0, wx.ALL, 5)
        self.page3.SetSizer(sizer)

    def _carregar_veiculos(self):
        disponiveis = []
        for pasta in VEHICLES_DIR.iterdir():
            if pasta.is_dir():
                vel = list(pasta.glob("*.vel"))
                if vel:
                    disponiveis.append(pasta.name)
        return disponiveis

    def add_veiculo(self, event):
        selecionado = self.lista_veiculos.GetStringSelection()
        if selecionado and selecionado not in self.dados.veiculos:
            self.dados.veiculos.append(selecionado)
            wx.MessageBox(f"Veículo {selecionado} adicionado à rota!", "Sucesso")

    def _format_elem(self, e: Elemento) -> str:
        d = f"{e.distancia_p0} km"
        if e.tipo == "Rua":
            base = f"Rua {e.nome}" if e.nome else "Rua"
            sup = f" ({e.superficie})" if e.superficie else ""
            return f"{base}{sup} - {d}"
        if e.tipo == "Parada":
            base = f"Parada {e.nome}" if e.nome else "Parada"
            return f"{base} - {d}"
        if e.tipo == "Curva":
            dir_ = f" {e.direcao}" if e.direcao else ""
            ang = f" {e.angulacao:g}°" if e.angulacao else ""
            sup = f" ({e.superficie})" if e.superficie else ""
            return f"Curva{dir_}{ang}{sup} - {d}"
        if e.tipo == "Semáforo":
            t = f" {e.tipo_semaforo}" if e.tipo_semaforo else ""
            return f"Semáforo{t} - {d}"
        if e.tipo == "Esquina":
            segue = getattr(e, "rua_principal", "")
            segestr = f" (segue pela {segue})" if segue else ""
            return f"Esquina{segestr} - {d}"
        return f"{e.tipo} - {d}"

    def add_elemento(self, event):
        tipo = self.tipo_elem.GetValue()
        try:
            distancia = float(self.dist_elem.GetValue())
        except ValueError:
            distancia = 0.0
        elem = Elemento(
            tipo=tipo,
            distancia_p0=distancia,
            superficie=self.superficie_elem.GetValue(),
            ordem=len(self.dados.elementos) + 1,
            nome=self.nome_elem.GetValue() if tipo in ("Rua", "Parada") else "",
            direcao=self.direcao_elem.GetValue(),
            angulacao=float(self.angulacao_elem.GetValue() or 0),
            rua_direita=self.rua_dir_elem.GetValue(),
            rua_esquerda=self.rua_esq_elem.GetValue(),
            tipo_semaforo=self.tipo_semaforo_elem.GetValue()
        )
        if tipo == "Esquina":
            if not self.rua_principal.GetValue():
                wx.MessageBox("Selecione por qual rua a rota segue!", "Erro")
                return
            elem.rua_principal = self.rua_principal.GetValue()
        self.dados.elementos.append(elem)
        self.lista_elementos.Append(self._format_elem(elem))

    def edit_elemento(self, event):
        idx = self.lista_elementos.GetSelection()
        if idx == wx.NOT_FOUND:
            return
        elem = self.dados.elementos[idx]
        self.tipo_elem.SetValue(elem.tipo)
        self.nome_elem.SetValue(elem.nome)
        self.superficie_elem.SetValue(elem.superficie)
        self.dist_elem.SetValue(str(elem.distancia_p0))
        self.direcao_elem.SetValue(elem.direcao)
        self.angulacao_elem.SetValue(str(elem.angulacao))
        self.rua_dir_elem.SetValue(elem.rua_direita)
        self.rua_esq_elem.SetValue(elem.rua_esquerda)
        self.tipo_semaforo_elem.SetValue(elem.tipo_semaforo)
        if getattr(elem, "tipo", "") == "Esquina" and hasattr(elem, "rua_principal"):
            self.rua_principal.SetValue(elem.rua_principal)
        self.dados.elementos.pop(idx)
        self.lista_elementos.Delete(idx)
        self.on_tipo_elem_changed(None)

    def remove_elemento(self, event):
        idx = self.lista_elementos.GetSelection()
        if idx != wx.NOT_FOUND:
            self.lista_elementos.Delete(idx)
            del self.dados.elementos[idx]

    def salvar(self, event):
        self.dados.id_rota = self.id_rota.GetValue().strip()
        self.dados.nome_rota = self.nome_rota.GetValue().strip()
        self.dados.operador = self.operador.GetValue().strip()
        self.dados.tipo_via = self.tipo_via.GetValue().strip()
        self.dados.tipo_rota = self.tipo_rota.GetValue().strip()
        self.dados.ponto_inicial = self.ponto_inicial.GetValue().strip()
        self.dados.ponto_final = self.ponto_final.GetValue().strip()
        self.dados.distancia_p0_pf = float(self.distancia.GetValue() or 0)
        self.dados.tmp_estimado = self.tmp_estimado.GetValue()
        self.dados.intervalo_min = self.intervalo_min.GetValue()
        if not self.dados.id_rota or not self.dados.nome_rota:
            wx.MessageBox("ID e Nome da rota não podem estar vazios!", "Erro")
            return
        pasta_rota = ROUTES_DIR / self.dados.id_rota
        pasta_rota.mkdir(parents=True, exist_ok=True)
        arquivo_rou = pasta_rota / f"{self.dados.id_rota}.rou"
        dados_json = json.dumps(self.dados.to_dict(), indent=2, ensure_ascii=False)
        fernet = Fernet(constantes.FERNET_KEY)
        dados_enc = fernet.encrypt(dados_json.encode()).decode()
        arquivo_rou.write_text(dados_enc, encoding="utf-8")
        wx.MessageBox(f"Rota salva em {arquivo_rou}", "Sucesso")

    @staticmethod
    def carregar(pasta: pathlib.Path) -> Rota:
        rou_files = list(pasta.glob("*.rou"))
        if not rou_files:
            raise FileNotFoundError("Nenhum arquivo .rou encontrado na pasta da rota")
        caminho = rou_files[0]
        dados_enc = caminho.read_text(encoding="utf-8")
        fernet = Fernet(constantes.FERNET_KEY)
        dados_json = fernet.decrypt(dados_enc.encode()).decode()
        d = json.loads(dados_json)
        return Rota(**d)
