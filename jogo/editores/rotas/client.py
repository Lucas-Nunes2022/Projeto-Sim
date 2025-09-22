import requests
import constantes
import os

def register(email, password):
    try:
        r = requests.post(
            f"{constantes.BASE_URL}/register",
            json={"email": email, "password": password}
        )
        return r.json()
    except Exception as e:
        return {"success": False, "message": f"Erro de conexão: {e}"}

def login(email, password):
    try:
        r = requests.post(
            f"{constantes.BASE_URL}/login",
            json={"email": email, "password": password}
        )
        return r.json()
    except Exception as e:
        return {"success": False, "message": f"Erro de conexão: {e}"}

def list_files():
    try:
        r = requests.get(f"{constantes.BASE_URL}/list/routes")
        return r.json()
    except Exception as e:
        return {"success": False, "message": f"Erro de conexão: {e}"}

def upload(file_path, user_id):
    try:
        with open(file_path, "rb") as f:
            r = requests.post(
                f"{constantes.BASE_URL}/upload/routes",
                files={"file": f},
                data={"user_id": user_id}
            )
        return r.json()
    except Exception as e:
        return {"success": False, "message": f"Erro de conexão: {e}"}

def download(file_name, save_path):
    try:
        url = f"{constantes.BASE_URL}/files/route"
        r = requests.get(url)
        if not r.json().get("success"):
            return r.json()
        files = r.json().get("files", [])
        if not any(f["file_name"] == file_name for f in files):
            return {"success": False, "message": "Arquivo não encontrado no servidor"}
        file_url = f"{constantes.BASE_URL}/data/routes/{file_name}"
        resp = requests.get(file_url)
        if resp.status_code == 200:
            with open(os.path.join(save_path, file_name), "wb") as f:
                f.write(resp.content)
            return {"success": True, "message": f"{file_name} baixado com sucesso"}
        return {"success": False, "message": "Falha ao baixar arquivo"}
    except Exception as e:
        return {"success": False, "message": f"Erro de conexão: {e}"}
