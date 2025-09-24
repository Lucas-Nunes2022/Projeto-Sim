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
        self.panel_main = wx.Panel(self)
        self.panel_login = wx.Panel(self)
        self.panel_register = wx.Panel(self)
        self.panel_files = wx.Panel(self)
        self.build_main()
        self.build_login()
        self.build_register()
        self.build_files()
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        for p in [self.panel_main, self.panel_login, self.panel_register, self.panel_files]:
            self.sizer.Add(p, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.show_panel(self.panel_main)

    def show_panel(self, panel):
        if panel is self.panel_files:
            if constantes.SESSION.get("role") == "admin" and self.file_type == "routes":
                self.btn_upload.Show()
                self.btn_delete.Show()
            else:
                self.btn_upload.Hide()
                self.btn_delete.Hide()
        for p in [self.panel_main, self.panel_login, self.panel_register, self.panel_files]:
            p.Hide()
        panel.Show()
        self.Layout()

    def build_main(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        btn_login = wx.Button(self.panel_main, label="Entrar")
        btn_register = wx.Button(self.panel_main, label="Criar Conta")
        btn_close = wx.Button(self.panel_main, label="Fechar")
        sizer.Add(wx.StaticText(self.panel_main, label="O que deseja fazer?"), 0, wx.ALL, 10)
        sizer.Add(btn_login, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(btn_register, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(btn_close, 0, wx.ALL | wx.EXPAND, 5)
        btn_login.Bind(wx.EVT_BUTTON, lambda evt: self.show_panel(self.panel_login))
        btn_register.Bind(wx.EVT_BUTTON, lambda evt: self.show_panel(self.panel_register))
        btn_close.Bind(wx.EVT_BUTTON, lambda evt: self.Close())
        self.panel_main.SetSizer(sizer)

    def build_login(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        lbl_email = wx.StaticText(self.panel_login, label="E-mail:")
        self.login_email = wx.TextCtrl(self.panel_login)
        sizer.Add(lbl_email, 0, wx.ALL, 5)
        sizer.Add(self.login_email, 0, wx.EXPAND | wx.ALL, 5)
        lbl_senha = wx.StaticText(self.panel_login, label="Senha:")
        self.login_password = wx.TextCtrl(self.panel_login, style=wx.TE_PASSWORD)
        sizer.Add(lbl_senha, 0, wx.ALL, 5)
        sizer.Add(self.login_password, 0, wx.EXPAND | wx.ALL, 5)
        btn_login = wx.Button(self.panel_login, label="Login")
        btn_back = wx.Button(self.panel_login, label="Voltar")
        sizer.Add(btn_login, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(btn_back, 0, wx.ALL | wx.EXPAND, 5)
        btn_login.Bind(wx.EVT_BUTTON, self.on_login)
        btn_back.Bind(wx.EVT_BUTTON, lambda evt: self.show_panel(self.panel_main))
        self.panel_login.SetSizer(sizer)

    def build_register(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        lbl_email = wx.StaticText(self.panel_register, label="E-mail:")
        self.register_email = wx.TextCtrl(self.panel_register)
        sizer.Add(lbl_email, 0, wx.ALL, 5)
        sizer.Add(self.register_email, 0, wx.EXPAND | wx.ALL, 5)
        lbl_senha = wx.StaticText(self.panel_register, label="Senha:")
        self.register_password = wx.TextCtrl(self.panel_register, style=wx.TE_PASSWORD)
        sizer.Add(lbl_senha, 0, wx.ALL, 5)
        sizer.Add(self.register_password, 0, wx.EXPAND | wx.ALL, 5)
        btn_register = wx.Button(self.panel_register, label="Criar Conta")
        btn_back = wx.Button(self.panel_register, label="Voltar")
        sizer.Add(btn_register, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(btn_back, 0, wx.ALL | wx.EXPAND, 5)
        btn_register.Bind(wx.EVT_BUTTON, self.on_register)
        btn_back.Bind(wx.EVT_BUTTON, lambda evt: self.show_panel(self.panel_main))
        self.panel_register.SetSizer(sizer)

    def build_files(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self.panel_files, label="Arquivos disponíveis:"), 0, wx.ALL, 5)
        self.list_ctrl = wx.ListBox(self.panel_files, choices=[])
        sizer.Add(self.list_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        btn_download = wx.Button(self.panel_files, label="Baixar selecionado")
        sizer.Add(btn_download, 0, wx.ALL | wx.EXPAND, 5)
        self.btn_upload = wx.Button(self.panel_files, label="Enviar pasta de rota")
        self.btn_upload.Hide()
        sizer.Add(self.btn_upload, 0, wx.ALL | wx.EXPAND, 5)
        self.btn_delete = wx.Button(self.panel_files, label="Deletar selecionado do servidor")
        self.btn_delete.Hide()
        sizer.Add(self.btn_delete, 0, wx.ALL | wx.EXPAND, 5)
        self.btn_upload.Bind(wx.EVT_BUTTON, self.on_upload)
        self.btn_delete.Bind(wx.EVT_BUTTON, self.on_delete)
        btn_back = wx.Button(self.panel_files, label="Voltar ao Menu Principal")
        btn_close = wx.Button(self.panel_files, label="Fechar")
        sizer.Add(btn_back, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(btn_close, 0, wx.ALL | wx.EXPAND, 5)
        btn_download.Bind(wx.EVT_BUTTON, self.on_download)
        btn_back.Bind(wx.EVT_BUTTON, lambda evt: self.show_panel(self.panel_main))
        btn_close.Bind(wx.EVT_BUTTON, lambda evt: self.Close())
        self.panel_files.SetSizer(sizer)

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
        self.show_panel(self.panel_files)
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
                self.show_panel(self.panel_files)
                self.load_files()
            else:
                wx.MessageBox("Conta criada, mas erro no login. Faça login manual.", "Aviso")
                self.show_panel(self.panel_login)
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
        self.load_files()

    def on_upload(self, event):
        with wx.DirDialog(
            self,
            "Selecione a pasta da rota",
            defaultPath=str(ROUTES_DIR),
            style=wx.DD_DIR_MUST_EXIST
        ) as dirDialog:
            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return
            path = dirDialog.GetPath()
            result = client.upload(path, constantes.SESSION["user_id"])
            if result.get("success"):
                wx.MessageBox(f"Pasta {path} enviada com sucesso!", "Servidor")
            else:
                wx.MessageBox(f"Erro ao enviar {path}: {result.get('message')}", "Erro")
            self.load_files()

    def on_delete(self, event):
        selection = self.list_ctrl.GetSelection()
        if selection == wx.NOT_FOUND:
            wx.MessageBox("Nenhum arquivo selecionado!", "Erro")
            return
        file_name = self.list_ctrl.GetString(selection)
        confirm = wx.MessageBox(f"Tem certeza que deseja deletar '{file_name}' do servidor?",
                                "Confirmar deleção", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
        if confirm != wx.YES:
            return
        result = client.delete(file_name, constantes.SESSION["user_id"])
        if result.get("success"):
            wx.MessageBox(f"Arquivo {file_name} deletado com sucesso!", "Sucesso")
        else:
            wx.MessageBox(f"Erro ao deletar: {result.get('message')}", "Erro")
        self.load_files()
