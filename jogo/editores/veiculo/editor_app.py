import wx
import json
import pathlib
from cryptography.fernet import Fernet
from models import Veiculo, Motor, Sons
from editor_frame import EditorFrame
import constantes

APPDATA = pathlib.Path.home() / "AppData" / "Roaming" / "lucas_producoes" / "simbus"
VEHICLES_DIR = APPDATA / "vehicles"

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
            with wx.DirDialog(None, "Escolha a pasta do veículo",
                              defaultPath=str(VEHICLES_DIR),
                              style=wx.DD_DIR_MUST_EXIST) as dirDialog:
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
