import wx
import json
import pathlib
from cryptography.fernet import Fernet
from models import Rota, Elemento
from editor_frame import EditorRotaFrame
import constantes

APPDATA = pathlib.Path.home() / "AppData" / "Roaming" / "lucas_producoes" / "simbus"
ROUTES_DIR = APPDATA / "routes"

class EditorRota(wx.App):
    def OnInit(self):
        choices = ("Criar nova rota", "Editar rota existente")
        dlg = wx.SingleChoiceDialog(None, "Escolha uma opção:", f"Editor de Rotas v{constantes.versao}", choices)

        cancel_btn = dlg.FindWindowById(wx.ID_CANCEL)
        if cancel_btn:
            cancel_btn.SetLabel("Cancelar")

        action = None
        if dlg.ShowModal() == wx.ID_OK:
            action = dlg.GetStringSelection()
        dlg.Destroy()

        if action == "Criar nova rota":
            frame = EditorRotaFrame(None, title=f"Criar rota - Editor de Rotas v{constantes.versao}", dados=Rota(), pasta=None)

        elif action == "Editar rota existente":
            with wx.DirDialog(None, "Escolha a pasta da rota",
                              defaultPath=str(ROUTES_DIR),
                              style=wx.DD_DIR_MUST_EXIST) as dirDialog:
                if dirDialog.ShowModal() == wx.ID_CANCEL:
                    return False
                pasta = pathlib.Path(dirDialog.GetPath())
                rou_files = list(pasta.glob("*.rou"))
                if not rou_files:
                    wx.MessageBox("Nenhum arquivo .rou encontrado na pasta!", "Erro")
                    return False
                caminho = rou_files[0]
                dados_enc = caminho.read_text(encoding="utf-8")
                fernet = Fernet(constantes.FERNET_KEY)
                dados_json = fernet.decrypt(dados_enc.encode()).decode()
                d = json.loads(dados_json)
                r = Rota(
                    id_rota=d.get("id_rota", ""),
                    nome_rota=d.get("nome_rota", ""),
                    operador=d.get("operador", ""),
                    tipo_via=d.get("tipo_via", ""),
                    tipo_rota=d.get("tipo_rota", ""),
                    ponto_inicial=d.get("ponto_inicial", ""),
                    ponto_final=d.get("ponto_final", ""),
                    distancia_p0_pf=d.get("distancia_p0_pf", 0),
                    veiculos=d.get("veiculos", []),
                    tmp_estimado=d.get("tmp_estimado", 0),
                    tipo_trafego=d.get("tipo_trafego", ""),
                    intervalo_min=d.get("intervalo_min", 0),
                    elementos=[Elemento(**e) for e in d.get("elementos", [])]
                )
                frame = EditorRotaFrame(None, title=f"Editar {r.nome_rota} - Editor de Rotas v{constantes.versao}", dados=r, pasta=pasta)
        else:
            return False

        frame.Show()
        return True
