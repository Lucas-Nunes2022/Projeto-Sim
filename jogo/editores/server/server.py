from flask import Flask, request, jsonify, send_from_directory
import pymysql
import bcrypt
import os
import zipfile
import shutil
from werkzeug.utils import secure_filename

app = Flask(__name__)

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "simbuss",
    "password": "ggmj1&9r",
    "database": "simbus"
}

DATA_DIR = "/srv/simbus/data"
ROUTES_DIR = os.path.join(DATA_DIR, "routes")
VEHICLES_DIR = os.path.join(DATA_DIR, "vehicles")

os.makedirs(ROUTES_DIR, exist_ok=True)
os.makedirs(VEHICLES_DIR, exist_ok=True)

app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024
ALLOWED_ROUTE_EXTENSIONS = {'.zip'}
ALLOWED_VEHICLE_EXTENSIONS = {'.zip'}


def get_db():
    return pymysql.connect(**DB_CONFIG)


def allowed_file_for_type(filename, file_type):
    ext = os.path.splitext(filename)[1].lower()
    if file_type == 'routes':
        return ext in ALLOWED_ROUTE_EXTENSIONS
    if file_type == 'vehicles':
        return ext in ALLOWED_VEHICLE_EXTENSIONS
    return False


def safe_extract_zip(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as z:
        for member in z.namelist():
            normalized = os.path.normpath(member)
            if normalized.startswith("..") or os.path.isabs(normalized):
                raise RuntimeError("Arquivo zip contém caminhos inválidos")
            target = os.path.join(extract_to, normalized)
            abs_target = os.path.abspath(target)
            abs_extract_to = os.path.abspath(extract_to)
            if not abs_target.startswith(abs_extract_to + os.sep) and abs_target != abs_extract_to:
                raise RuntimeError("Tentativa de extração fora do diretório alvo")
        z.extractall(extract_to)


@app.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"success": False, "message": "Dados inválidos"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE email=%s", (email,))
    if cur.fetchone():
        conn.close()
        return jsonify({"success": False, "message": "Usuário já existe"}), 400

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    cur.execute(
        "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, %s)",
        (email, password_hash, "normal")
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Conta criada com sucesso"})


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, password_hash, role FROM users WHERE email=%s", (email,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify({"success": False, "message": "Usuário não encontrado"}), 404

    user_id, stored_hash, role = row
    if bcrypt.checkpw(password.encode(), stored_hash.encode()):
        return jsonify({"success": True, "message": "Login OK", "role": role, "user_id": user_id})
    else:
        return jsonify({"success": False, "message": "Senha incorreta"}), 401


@app.route("/list/<file_type>", methods=["GET"])
def list_files(file_type):
    if file_type not in ["routes", "vehicles"]:
        return jsonify({"success": False, "message": "Tipo inválido"}), 400

    folder = ROUTES_DIR if file_type == "routes" else VEHICLES_DIR
    if file_type == "routes":
        files = [f for f in os.listdir(folder) if os.path.isdir(os.path.join(folder, f))]
    else:
        files = os.listdir(folder)

    return jsonify({"success": True, "files": files})


@app.route("/upload/<file_type>", methods=["POST"])
def upload(file_type):
    if file_type not in ["routes", "vehicles"]:
        return jsonify({"success": False, "message": "Tipo inválido"}), 400

    uploaded_file = request.files.get("file")
    uploaded_by = request.form.get("user_id")

    if not uploaded_file or not uploaded_by:
        return jsonify({"success": False, "message": "Arquivo ou usuário inválido"}), 400

    try:
        uploaded_by_id = int(uploaded_by)
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "user_id inválido"}), 400

    conn = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT role FROM users WHERE id=%s", (uploaded_by_id,))
        row = cur.fetchone()
        if not row or row[0] != "admin":
            conn.close()
            return jsonify({"success": False, "message": "Permissão negada"}), 403

        filename = secure_filename(uploaded_file.filename or "")
        if not filename:
            return jsonify({"success": False, "message": "Nome de arquivo inválido"}), 400

        if not allowed_file_for_type(filename, file_type):
            return jsonify({"success": False, "message": "Extensão de arquivo não permitida"}), 400

        folder = ROUTES_DIR if file_type == "routes" else VEHICLES_DIR
        save_path = os.path.join(folder, filename)

        if os.path.exists(save_path) or os.path.exists(os.path.join(folder, os.path.splitext(filename)[0])):
            return jsonify({"success": False, "message": "Arquivo ou pasta já existe no servidor"}), 409

        uploaded_file.save(save_path)
        if file_type == "routes" and save_path.endswith(".zip"):
            extract_dir = os.path.join(folder, os.path.splitext(filename)[0])
            os.makedirs(extract_dir, exist_ok=True)
            try:
                safe_extract_zip(save_path, extract_dir)
            except Exception as e:
                if os.path.exists(extract_dir):
                    shutil.rmtree(extract_dir, ignore_errors=True)
                os.remove(save_path)
                return jsonify({"success": False, "message": f"ZIP inválido: {e}"}), 400
            os.remove(save_path)

        cur.execute(
            "INSERT INTO files (file_name, file_type, uploaded_by) VALUES (%s, %s, %s)",
            (filename, file_type[:-1], uploaded_by_id)
        )
        conn.commit()
        return jsonify({"success": True, "message": f"{filename} salvo e registrado no banco"})
    except pymysql.MySQLError as e:
        if conn:
            conn.rollback()
        return jsonify({"success": False, "message": f"Erro de banco: {e}"}), 500
    finally:
        if conn:
            conn.close()


@app.route("/files/<file_type>", methods=["GET"])
def files_db(file_type):
    if file_type not in ["route", "vehicle"]:
        return jsonify({"success": False, "message": "Tipo inválido"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT file_name, uploaded_at FROM files WHERE file_type=%s", (file_type,))
    rows = cur.fetchall()
    conn.close()

    files = [{"file_name": r[0], "uploaded_at": str(r[1])} for r in rows]
    return jsonify({"success": True, "files": files})


@app.route("/data/<file_type>/<path:filename>", methods=["GET"])
def serve_file(file_type, filename):
    if file_type not in ["routes", "vehicles"]:
        return jsonify({"success": False, "message": "Tipo inválido"}), 400

    folder = ROUTES_DIR if file_type == "routes" else VEHICLES_DIR
    return send_from_directory(folder, filename, as_attachment=True)


@app.route("/delete/<file_type>", methods=["POST"])
def delete_file(file_type):
    if file_type not in ["routes", "vehicles"]:
        return jsonify({"success": False, "message": "Tipo inválido"}), 400

    data = request.json
    file_name = data.get("file_name")
    user_id = data.get("user_id")

    if not file_name or not user_id:
        return jsonify({"success": False, "message": "Dados inválidos"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT role FROM users WHERE id=%s", (user_id,))
    row = cur.fetchone()
    if not row or row[0] != "admin":
        conn.close()
        return jsonify({"success": False, "message": "Permissão negada"}), 403

    folder = ROUTES_DIR if file_type == "routes" else VEHICLES_DIR
    target_path = os.path.join(folder, file_name)

    if os.path.isdir(target_path):
        shutil.rmtree(target_path)
    elif os.path.isfile(target_path):
        os.remove(target_path)

    cur.execute("DELETE FROM files WHERE file_name=%s AND file_type=%s", (file_name, file_type[:-1]))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": f"{file_name} removido do servidor"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
