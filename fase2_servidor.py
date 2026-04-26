"""
FASE 2 - SERVIDOR FLASK VULNERABLE
====================================
Servidor web con login intencionalmente vulnerable a SQL injection.
Arrancar con:  python fase2_servidor.py
Acceder en:    http://localhost:5000
"""

import sqlite3
from flask import Flask, request, render_template_string, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "escape-room-ia-2024"

# ── Templates HTML ─────────────────────────────────────────────────────────

LOGIN_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SysPanel · Login</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Courier New', monospace;
      background: #0a0e1a;
      color: #c8d3e8;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .terminal {
      background: #0f1520;
      border: 1px solid #1e3a5f;
      border-radius: 8px;
      padding: 40px;
      width: 420px;
      box-shadow: 0 0 40px rgba(0,100,255,0.08);
    }
    .logo {
      text-align: center;
      margin-bottom: 32px;
    }
    .logo h1 { font-size: 22px; color: #4a9eff; letter-spacing: 4px; font-weight: normal; }
    .logo p  { font-size: 11px; color: #3d5a80; margin-top: 6px; letter-spacing: 2px; }
    label {
      display: block;
      font-size: 11px;
      color: #3d7abf;
      letter-spacing: 1px;
      margin-bottom: 6px;
    }
    input[type=text], input[type=password] {
      width: 100%;
      padding: 10px 12px;
      background: #071018;
      border: 1px solid #1e3a5f;
      border-radius: 4px;
      color: #7eb8f7;
      font-family: 'Courier New', monospace;
      font-size: 14px;
      margin-bottom: 20px;
      outline: none;
      transition: border-color 0.2s;
    }
    input:focus { border-color: #4a9eff; }
    button {
      width: 100%;
      padding: 12px;
      background: #1a3a6b;
      border: 1px solid #4a9eff;
      border-radius: 4px;
      color: #7eb8f7;
      font-family: 'Courier New', monospace;
      font-size: 13px;
      letter-spacing: 2px;
      cursor: pointer;
      transition: background 0.2s;
    }
    button:hover { background: #1e4a8a; }
    .error {
      background: #1a0a0a;
      border: 1px solid #5f1e1e;
      border-radius: 4px;
      padding: 10px 14px;
      font-size: 12px;
      color: #ff6b6b;
      margin-bottom: 20px;
      letter-spacing: 1px;
    }
    .hint {
      margin-top: 24px;
      padding-top: 20px;
      border-top: 1px solid #1e3a5f;
      font-size: 11px;
      color: #2d4a6a;
      line-height: 1.7;
    }
    .hint span { color: #3d7abf; }
  </style>
</head>
<body>
  <div class="terminal">
    <div class="logo">
      <h1>SYSPANEL</h1>
      <p>SISTEMA DE ADMINISTRACIÓN · v2.1</p>
    </div>
    {% if error %}
    <div class="error">⚠ {{ error }}</div>
    {% endif %}
    <form method="POST" action="/login">
      <label>USUARIO</label>
      <input type="text" name="username" autocomplete="off" autofocus>
      <label>CONTRASEÑA</label>
      <input type="password" name="password">
      <button type="submit">ACCEDER →</button>
    </form>
    <div class="hint">
      <span>PISTA:</span> Solo el rol <span>admin</span> tiene acceso<br>
      al panel de control. Identificad al admin<br>
      en los logs antes de intentar el acceso.
    </div>
  </div>
</body>
</html>
"""

PANEL_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>SysPanel · Panel</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Courier New', monospace;
      background: #0a0e1a;
      color: #c8d3e8;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .panel {
      background: #0f1520;
      border: 1px solid #1e5f3a;
      border-radius: 8px;
      padding: 40px;
      width: 520px;
      text-align: center;
    }
    .success { font-size: 36px; margin-bottom: 20px; }
    h2 { color: #4aff9e; font-size: 18px; letter-spacing: 3px; font-weight: normal; margin-bottom: 12px; }
    .user  { color: #3d7abf; font-size: 13px; margin-bottom: 32px; }
    .flag-box {
      background: #071810;
      border: 2px solid #1e5f3a;
      border-radius: 6px;
      padding: 24px;
      margin-bottom: 24px;
    }
    .flag-label { font-size: 11px; color: #2d6a4a; letter-spacing: 2px; margin-bottom: 10px; }
    .flag  { font-size: 22px; color: #4aff9e; letter-spacing: 4px; font-weight: bold; }
    .info  { font-size: 12px; color: #2d4a6a; line-height: 1.8; }
    .info span { color: #3d7abf; }
    .query {
      margin-top: 28px;
      background: #071018;
      border: 1px solid #1e3a5f;
      border-radius: 4px;
      padding: 14px;
      font-size: 12px;
      color: #2d6aaa;
      text-align: left;
    }
    .query .label { color: #1e4a80; font-size: 10px; letter-spacing: 1px; margin-bottom: 6px; }
    .query code   { color: #4a9eff; }
  </style>
</head>
<body>
  <div class="panel">
    <div class="success">✓</div>
    <h2>ACCESO CONCEDIDO</h2>
    <p class="user">Bienvenido, <strong>{{ username }}</strong> · rol: {{ rol }}</p>
    <div class="flag-box">
      <div class="flag-label">CONTRASEÑA SIGUIENTE FASE</div>
      <div class="flag">{{ flag }}</div>
    </div>
    <div class="info">
      Habéis explotado una vulnerabilidad de<br>
      <span>SQL Injection</span> en el formulario de login.<br><br>
      La consulta que ejecutó el servidor fue:<br>
    </div>
    <div class="query">
      <div class="label">QUERY EJECUTADA:</div>
      <code>{{ query }}</code>
    </div>
  </div>
</body>
</html>
"""

ACCESO_DENEGADO_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>SysPanel · Acceso denegado</title>
  <style>
    body { font-family: 'Courier New', monospace; background: #0a0e1a;
           color: #c8d3e8; min-height: 100vh; display: flex;
           align-items: center; justify-content: center; }
    .box { background: #0f1520; border: 1px solid #5f1e1e; border-radius: 8px;
           padding: 40px; width: 420px; text-align: center; }
    h2 { color: #ff6b6b; font-size: 16px; letter-spacing: 3px; margin-bottom: 16px; }
    p  { font-size: 12px; color: #3d4a5a; line-height: 1.8; }
    a  { display: inline-block; margin-top: 24px; color: #3d7abf; font-size: 12px; text-decoration: none; }
  </style>
</head>
<body>
  <div class="box">
    <h2>ACCESO DENEGADO</h2>
    <p>Credenciales correctas pero sin privilegios.<br>
       Solo el rol <strong style="color:#4a9eff">admin</strong> puede acceder al panel.<br><br>
       Revisad el cluster identificado en los logs.</p>
    <a href="/login">← Volver al login</a>
  </div>
</body>
</html>
"""

# ── Rutas ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template_string(LOGIN_HTML, error=None)

    username = request.form.get("username", "")
    password = request.form.get("password", "")

    conn = sqlite3.connect("database.db")
    cur  = conn.cursor()

    # ⚠ VULNERABLE: concatenación directa de inputs del usuario
    query = f"SELECT username, password, rol, flag FROM usuarios WHERE username='{username}' AND password='{password}'"

    try:
        cur.execute(query)
        row = cur.fetchone()
    except sqlite3.OperationalError as e:
        conn.close()
        return render_template_string(LOGIN_HTML, error=f"Error SQL: {e}")

    conn.close()

    if row is None:
        return render_template_string(LOGIN_HTML, error="Usuario o contraseña incorrectos.")

    db_user, db_pass, rol, flag = row

    if rol != "admin":
        return render_template_string(ACCESO_DENEGADO_HTML)

    return render_template_string(
        PANEL_HTML,
        username=db_user,
        rol=rol,
        flag=flag,
        query=query,
    )


if __name__ == "__main__":
    print("=" * 50)
    print("  FASE 2 · Servidor arrancado")
    print("  URL: http://localhost:5000")
    print("  Detener con Ctrl+C")
    print("=" * 50)
    app.run(debug=False, port=5000)
