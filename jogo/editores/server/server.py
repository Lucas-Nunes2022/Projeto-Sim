from flask import Flask, request, jsonify
import pymysql
import bcrypt
import os

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

def get_db():
    return pymysql.connect(**DB_CONFIG)

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
        return jsonify({"success": False, "message": "Usuário já existe"}), 400
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    cur.execute("INSERT INTO users (email, password_hash, role) VALUES (%s, %s, %s)", 
                (email, password_hash, "normal"))
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
    files = os.listdir(folder)
    return jsonify({"success": True, "files": files})

@app.route("/upload/<file_type>", methods=["POST"])
def upload(file_type):
    if file_type not in ["routes", "vehicles"]:
        return jsonify({"success": False, "message": "Tipo inválido"}), 400
    file = request.files.get("file")
    uploaded_by = request.form.get("user_id")
    if not file or not uploaded_by:
        return jsonify({"success": False, "message": "Arquivo ou usuário inválido"}), 400
    folder = ROUTES_DIR if file_type == "routes" else VEHICLES_DIR
    save_path = os.path.join(folder, file.filename)
    file.save(save_path)
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO files (file_name, file_type, uploaded_by) VALUES (%s, %s, %s)",
        (file.filename, file_type[:-1], uploaded_by)
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": f"Arquivo {file.filename} salvo e registrado no banco"})

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
