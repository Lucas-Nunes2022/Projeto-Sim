import wx
import client
import constantes
import pathlib

APPDATA = pathlib.Path.home() / "AppData" / "Roaming" / "lucas_producoes" / "simbus"
ROUTES_DIR = APPDATA / "routes"
VEHICLES_DIR = APPDATA / "vehicles"
ROUTES_DIR.mkdir(parents=True, exist_ok=True)
VEHICLES_DIR.mkdir(parents=True, exist_ok=True)

class SyncDialog(wx.Dialog):
    def __init__(self, parent=None, file_type="routes"):
        super().__init__(parent, title="Sincronização", size=(500, 400))
        self.file_type = file_type

        self.notebook = wx.Notebook(self)
        self.panel_login = wx.Panel(self.notebook)
        self.panel_register = wx.Panel(self.notebook)
        self.panel_files = wx.Panel(self.notebook)

        self.build_login()
        self.build_register()
        self.build_files()

        self.notebook.AddPage(self.panel_login, "Login")
        self.notebook.AddPage(self.panel_register, "Criar Conta")
        self.notebook.AddPage(self.panel_files, "Arquivos")

        self.panel_files.Disable()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)

    def build_login(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.login_email = wx.TextCtrl(self.panel_login)
        self.login_password = wx.TextCtrl(self.panel_login, style=wx.TE_PASSWORD)
        btn_login = wx.Button(self.panel_login, label="Login")
        sizer.Add(wx.StaticText(self.panel_login, label="E-mail"), 0, wx.ALL, 5)
        sizer.Add(self.login_email, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(wx.StaticText(self.panel_login, label="Senha"), 0, wx.ALL, 5)
        sizer.Add(self.login_password, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(btn_login, 0, wx.ALL | wx.EXPAND, 5)
        self.panel_login.SetSizer(sizer)
        btn_login.Bind(wx.EVT_BUTTON, self.on_login)

    def build_register(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.register_email = wx.TextCtrl(self.panel_register)
        self.register_password = wx.TextCtrl(self.panel_register, style=wx.TE_PASSWORD)
        btn_register = wx.Button(self.panel_register, label="Criar Conta")
        sizer.Add(wx.StaticText(self.panel_register, label="E-mail"), 0, wx.ALL, 5)
        sizer.Add(self.register_email, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(wx.StaticText(self.panel_register, label="Senha"), 0, wx.ALL, 5)
        sizer.Add(self.register_password, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(btn_register, 0, wx.ALL | wx.EXPAND, 5)
        self.panel_register.SetSizer(sizer)
        btn_register.Bind(wx.EVT_BUTTON, self.on_register)

    def build_files(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.list_ctrl = wx.ListBox(self.panel_files, choices=[])
        btn_download = wx.Button(self.panel_files, label="Baixar selecionado")
        sizer.Add(self.list_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(btn_download, 0, wx.ALL | wx.EXPAND, 5)
        if constantes.SESSION.get("role") == "admin" and self.file_type == "routes":
            btn_upload = wx.Button(self.panel_files, label="Enviar rota local")
            sizer.Add(btn_upload, 0, wx.ALL | wx.EXPAND, 5)
            btn_upload.Bind(wx.EVT_BUTTON, self.on_upload)
        btn_close = wx.Button(self.panel_files, label="Fechar")
        sizer.Add(btn_close, 0, wx.ALL | wx.EXPAND, 5)
        self.panel_files.SetSizer(sizer)
        btn_download.Bind(wx.EVT_BUTTON, self.on_download)
        btn_close.Bind(wx.EVT_BUTTON, lambda evt: self.Close())

    def on_login(self, event):
        email = self.login_email.GetValue().strip()
        senha = self.login_password.GetValue().strip()
        result = client.login(email, senha)
        if not result.get("success"):
            wx.MessageBox(f"Erro no login: {result.get('message')}", "Erro")
            return
        constantes.SESSION.update({
            "logged_in": True,
            "user_id": result.get("user_id"),
            "role": result.get("role"),
            "email": email
        })
        wx.MessageBox("Login bem-sucedido", "Sucesso")
        self.panel_files.Enable()
        self.notebook.ChangeSelection(2)
        self.load_files()

    def on_register(self, event):
        email = self.register_email.GetValue().strip()
        senha = self.register_password.GetValue().strip()
        result = client.register(email, senha)
        if result.get("success"):
            login_result = client.login(email, senha)
            if login_result.get("success"):
                constantes.SESSION.update({
                    "logged_in": True,
                    "user_id": login_result.get("user_id"),
                    "role": login_result.get("role"),
                    "email": email
                })
                wx.MessageBox("Conta criada e login bem-sucedido", "Sucesso")
                self.panel_files.Enable()
                self.notebook.ChangeSelection(2)
                self.load_files()
            else:
                wx.MessageBox("Conta criada, mas erro no login. Faça login manual.", "Aviso")
                self.notebook.ChangeSelection(0)
        else:
            wx.MessageBox(f"Erro ao criar conta: {result.get('message')}", "Erro")

    def load_files(self):
        result = client.list_files(self.file_type)
        if not result.get("success"):
            wx.MessageBox(f"Erro ao listar arquivos: {result.get('message')}", "Erro")
            return
        files = result.get("files", [])
        if isinstance(files, dict) and "files" in files:
            files = files["files"]
        self.list_ctrl.Set(files if isinstance(files, list) else [])

    def on_download(self, event):
        selection = self.list_ctrl.GetSelection()
        if selection == wx.NOT_FOUND:
            wx.MessageBox("Nenhum arquivo selecionado!", "Erro")
            return
        file_name = self.list_ctrl.GetString(selection)
        save_dir = ROUTES_DIR if self.file_type == "routes" else VEHICLES_DIR
        save_path = str(save_dir)
        result = client.download(file_name, save_path)
        if result.get("success"):
            wx.MessageBox(f"{file_name} baixado com sucesso em {save_path}", "Sucesso")
        else:
            wx.MessageBox(f"Erro ao baixar: {result.get('message')}", "Erro")

    def on_upload(self, event):
        with wx.FileDialog(
            self,
            "Selecione arquivos de rota",
            wildcard="Arquivos de rota (*.rou)|*.rou",
            defaultDir=str(ROUTES_DIR),
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE
        ) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            paths = fileDialog.GetPaths()
            for path in paths:
                result = client.upload(path, constantes.SESSION["user_id"])
                if result.get("success"):
                    wx.MessageBox(f"{path} enviado com sucesso!", "Servidor")
                else:
                    wx.MessageBox(f"Erro ao enviar {path}: {result.get('message')}", "Erro")
            self.load_files()
