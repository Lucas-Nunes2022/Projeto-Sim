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
        dlg = wx.SingleChoiceDialog(None, "Escolha uma opção:", f"Editor de Veículos v{constantes.versao}", choices)

        cancel_btn = dlg.FindWindowById(wx.ID_CANCEL)
        if cancel_btn:
            cancel_btn.SetLabel("Cancelar")

        action = None
        if dlg.ShowModal() == wx.ID_OK:
            action = dlg.GetStringSelection()
        dlg.Destroy()

        if action == "Criar novo veículo":
            frame = EditorFrame(None, title=f"Criar veículo - Editor de Veículos v{constantes.versao}", dados=Veiculo(), pasta=None)

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
                    fabricante=d.get("fabricante",""),
                    ano=d.get("ano",0),
                    tipo=d.get("tipo",""),
                    cambio=d.get("cambio",""),
                    qtd_marchas=d.get("qtd_marchas",0),
                    comprimento_m=d.get("comprimento_m",0),
                    portas=d.get("portas",0),
                    capacidade=d.get("capacidade",0),
                    peso=d.get("peso",0),
                    altura=d.get("altura",0),
                    largura=d.get("largura",0),
                    cap_tanque=d.get("cap_tanque",0),
                    qtd_eixos=d.get("qtd_eixos",0),
                    motor=Motor(**d.get("motor",{})),
                    sons=Sons(**d.get("sons",{}))
                )
                pasta_sons = pasta / "sounds"
                if pasta_sons.exists():
                    for attr, val in v.sons.__dict__.items():
                        if val:
                            setattr(v.sons, attr, str(pasta_sons / val))

                frame = EditorFrame(None, title=f"Editar {v.nome} - Editor de Veículos v{constantes.versao}", dados=v, pasta=pasta)
        else:
            return False

        frame.Show()
        return True
