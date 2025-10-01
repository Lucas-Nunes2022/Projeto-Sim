import requests
import constantes
import os
import shutil
import tempfile
import zipfile

def register(nome, email, password):
    try:
        r = requests.post(
            f"{constantes.BASE_URL}/register",
            json={"nome": nome, "email": email, "password": password}
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

def list_files(file_type="routes"):
    try:
        r = requests.get(f"{constantes.BASE_URL}/list/{file_type}")
        return r.json()
    except Exception as e:
        return {"success": False, "message": f"Erro de conexão: {e}"}

def upload(dir_path, user_id):
    try:
        if not os.path.isdir(dir_path):
            return {"success": False, "message": "O upload aceita apenas diretórios"}

        base_name = os.path.basename(dir_path.rstrip("/\\"))
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, f"{base_name}.zip")

        shutil.make_archive(zip_path[:-4], "zip", dir_path)

        with open(zip_path, "rb") as f:
            r = requests.post(
                f"{constantes.BASE_URL}/upload/routes",
                files={"file": f},
                data={"user_id": user_id}
            )

        shutil.rmtree(temp_dir)
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
            zip_path = os.path.join(save_path, file_name)
            with open(zip_path, "wb") as f:
                f.write(resp.content)

            extract_dir = os.path.join(save_path, file_name[:-4])
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(extract_dir)

            os.remove(zip_path)
            return {"success": True, "message": f"{file_name} baixado e extraído em {extract_dir}"}
        return {"success": False, "message": "Falha ao baixar arquivo"}
    except Exception as e:
        return {"success": False, "message": f"Erro de conexão: {e}"}

def delete(file_name, user_id, file_type="routes"):
    try:
        r = requests.post(
            f"{constantes.BASE_URL}/delete/{file_type}",
            json={"file_name": file_name, "user_id": user_id}
        )
        return r.json()
    except Exception as e:
        return {"success": False, "message": f"Erro de conexão: {e}"}
