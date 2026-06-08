import os
import cv2
import numpy as np
import pymysql
from datetime import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'amai-shop-secret-key-2024')

# Variable global para guardar fotos (evita problemas de sesión)
user_photos = {}

# ============================================
# CONEXION MYSQL CON PYMYSQL
# ============================================
def get_db_connection():
    return pymysql.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER', 'root'),
        password='',
        database=os.getenv('MYSQL_DB', 'amai_shop'),
        cursorclass=pymysql.cursors.DictCursor,
        charset='utf8mb4'
    )

# ============================================
# CONFIGURACION ARCHIVOS
# ============================================
UPLOAD_FOLDER = 'static/images/uploads'
CLOTHING_FOLDER = 'static/images/ropa'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(f'{CLOTHING_FOLDER}/hombre', exist_ok=True)
os.makedirs(f'{CLOTHING_FOLDER}/mujer', exist_ok=True)

# ============================================
# AUTO-GENERAR PLACEHOLDERS SI NO EXISTEN
# ============================================
def crear_placeholder(texto, ruta):
    if os.path.exists(ruta):
        return
    img = np.zeros((400, 300, 4), dtype=np.uint8)
    img[:, :] = (240, 240, 240, 255)
    color = (100, 150, 200, 255)
    cv2.rectangle(img, (20, 20), (280, 380), color, -1)
    cv2.rectangle(img, (20, 20), (280, 380), (80, 130, 180, 255), 3)
    palabras = texto.replace('.png', '').replace('_', ' ').title().split()
    y_pos = 140
    for i, palabra in enumerate(palabras[:3]):
        cv2.putText(img, palabra, (30, y_pos + (i*45)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255, 255), 2)
    cv2.putText(img, "DEMO", (30, 360), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150, 255), 1)
    cv2.imwrite(ruta, img)
    print(f"✅ Placeholder creado: {ruta}")

def verificar_imagenes():
    prendas_hombre = [
        'camisa_oxford.png', 'camisa_denim.png', 'playera_negra.png', 'playera_estampada.png',
        'jeans_slim.png', 'chinos_caqui.png', 'bomber.png', 'derby.png'
    ]
    prendas_mujer = [
        'blusa_seda.png', 'camisa_oversize.png', 'crop_top.png', 'vestido_floral.png',
        'vestido_negro.png', 'falda_midi.png', 'jeans_mom.png', 'trench.png',
        'zapatillas.png', 'tacones_nude.png'
    ]
    for p in prendas_hombre:
        crear_placeholder(p, f'static/images/ropa/hombre/{p}')
    for p in prendas_mujer:
        crear_placeholder(p, f'static/images/ropa/mujer/{p}')
    print("✅ Verificación de imágenes completa")

# Generar placeholders al iniciar
verificar_imagenes()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor inicia sesion para continuar', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== RUTAS PRINCIPALES ====================

@app.route('/')
def index():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT p.*, COUNT(op.prenda_id) as veces_usada FROM prendas p LEFT JOIN outfit_prendas op ON p.id = op.prenda_id GROUP BY p.id ORDER BY veces_usada DESC LIMIT 8")
            destacados = cur.fetchall()
    finally:
        conn.close()
    return render_template('index.html', destacados=destacados)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
                user = cur.fetchone()
        finally:
            conn.close()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['nombre']
            flash(f'Bienvenido, {user["nombre"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email o contrasena incorrectos', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm_password']
        if password != confirm:
            flash('Las contrasenas no coinciden', 'danger')
            return redirect(url_for('register'))
        if len(password) < 6:
            flash('Minimo 6 caracteres', 'danger')
            return redirect(url_for('register'))
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
                if cur.fetchone():
                    flash('Email ya registrado', 'warning')
                    return redirect(url_for('register'))
                password_hash = generate_password_hash(password)
                cur.execute("INSERT INTO usuarios (nombre, email, password_hash) VALUES (%s, %s, %s)", (nombre, email, password_hash))
                conn.commit()
        finally:
            conn.close()
        flash('Registro exitoso!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    user_photos.clear()
    flash('Sesion cerrada', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as total_outfits FROM outfits WHERE usuario_id = %s", (session['user_id'],))
            stats = cur.fetchone()
            cur.execute("SELECT o.*, GROUP_CONCAT(p.nombre SEPARATOR ', ') as prendas, COUNT(op.id) as num_prendas FROM outfits o LEFT JOIN outfit_prendas op ON o.id = op.outfit_id LEFT JOIN prendas p ON op.prenda_id = p.id WHERE o.usuario_id = %s GROUP BY o.id ORDER BY o.fecha_creacion DESC LIMIT 10", (session['user_id'],))
            outfits = cur.fetchall()
    finally:
        conn.close()
    return render_template('dashboard.html', stats=stats, outfits=outfits)

@app.route('/catalogo')
@app.route('/catalogo/<genero>')
@app.route('/catalogo/<genero>/<categoria>')
def catalogo(genero=None, categoria=None):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = "SELECT * FROM prendas WHERE 1=1"
            params = []
            if genero in ['hombre', 'mujer']:
                query += " AND genero = %s"
                params.append(genero)
            if categoria in ['camisas', 'playeras', 'pantalones', 'vestidos', 'faldas', 'chaquetas', 'zapatos']:
                query += " AND categoria = %s"
                params.append(categoria)
            query += " ORDER BY categoria, nombre"
            cur.execute(query, tuple(params))
            prendas = cur.fetchall()
    finally:
        conn.close()
    return render_template('catalogo.html', prendas=prendas, genero=genero, categoria=categoria)

@app.route('/probador', methods=['GET', 'POST'])
@login_required
def probador():
    user_id = session['user_id']
    
    if request.method == 'POST':
        print(f"POST recibido. user_id: {user_id}")
        print(f"Files: {request.files}")
        
        if 'foto' not in request.files:
            print("ERROR: No hay 'foto' en request.files")
            flash('No se selecciono foto', 'danger')
            return redirect(request.url)
        
        file = request.files['foto']
        print(f"Archivo recibido: {file.filename}")
        
        if file.filename == '':
            print("ERROR: filename vacio")
            flash('No se selecciono foto', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(f"user_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            print(f"Foto guardada en: {filepath}")
            
            # Guardar en variable global Y sesion
            user_photos[user_id] = filename
            session['last_photo'] = filename
            session.modified = True
            
            print(f"user_photos: {user_photos}")
            print(f"session last_photo: {session.get('last_photo')}")
            
            flash('Foto subida correctamente', 'success')
            return redirect(url_for('probador'))
    
    # GET - Recuperar foto de variable global o sesion
    last_photo = user_photos.get(user_id) or session.get('last_photo')
    print(f"GET probador. user_id: {user_id}, last_photo: {last_photo}")
    
    if last_photo and not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], last_photo)):
        print(f"Foto no existe fisicamente: {last_photo}")
        last_photo = None
        user_photos.pop(user_id, None)
        session.pop('last_photo', None)
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM prendas ORDER BY genero, categoria")
            prendas = cur.fetchall()
    finally:
        conn.close()
    
    return render_template('probador.html', prendas=prendas, last_photo=last_photo)

@app.route('/api/try-on', methods=['POST'])
@login_required
def api_try_on():
    data = request.get_json()
    print(f"API try-on. Datos: {data}")
    print(f"user_photos: {user_photos}")
    print(f"session: {session.get('last_photo')}")
    
    if not data:
        return jsonify({'error': 'No se recibieron datos'}), 400
    
    # Obtener foto de variable global o datos
    user_id = session['user_id']
    photo_filename = data.get('photo') or user_photos.get(user_id) or session.get('last_photo')
    
    print(f"photo_filename: {photo_filename}")
    
    if not photo_filename:
        return jsonify({'error': 'No hay foto cargada'}), 400
    
    if 'prenda_id' not in data:
        return jsonify({'error': 'No hay prenda_id'}), 400
    
    prenda_id = data['prenda_id']
    scale = float(data.get('scale', 1.0))
    pos_x = int(data.get('pos_x', 0))
    pos_y = int(data.get('pos_y', 0))
    
    # Verificar que la foto existe
    user_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_filename)
    if not os.path.exists(user_photo_path):
        return jsonify({'error': f'Foto no encontrada: {photo_filename}'}), 404
    
    # Obtener prenda
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT imagen FROM prendas WHERE id = %s", (prenda_id,))
            prenda = cur.fetchone()
    finally:
        conn.close()
    
    if not prenda:
        return jsonify({'error': 'Prenda no encontrada'}), 404
    
    prenda_path = os.path.join('static/images', prenda['imagen'])
    
    try:
        result_path = process_try_on(user_photo_path, prenda_path, scale, pos_x, pos_y)
        result_filename = os.path.basename(result_path)
        
        return jsonify({
            'success': True,
            'result_image': f'/static/images/uploads/{result_filename}',
            'message': 'Prenda superpuesta correctamente'
        })
    except Exception as e:
        print(f"Error en process_try_on: {str(e)}")
        return jsonify({'error': str(e)}), 500

def process_try_on(user_photo_path, prenda_path, scale=1.0, pos_x=0, pos_y=0):
    user_img = cv2.imread(user_photo_path)
    if user_img is None:
        raise ValueError("No se pudo cargar la foto del usuario")
    prenda = cv2.imread(prenda_path, cv2.IMREAD_UNCHANGED)
    if prenda is None:
        prenda = create_placeholder_prenda()
    h, w = user_img.shape[:2]
    ph, pw = prenda.shape[:2]
    new_w = int(w * 0.4 * scale)
    new_h = int(new_w * (ph / pw))
    x = (w - new_w) // 2 + pos_x
    y = (h - new_h) // 2 + pos_y
    x = max(0, min(x, w - new_w))
    y = max(0, min(y, h - new_h))
    prenda_resized = cv2.resize(prenda, (new_w, new_h))
    if prenda_resized.shape[2] == 4:
        alpha = prenda_resized[:, :, 3] / 255.0
        for c in range(3):
            roi = user_img[y:y+new_h, x:x+new_w, c]
            user_img[y:y+new_h, x:x+new_w, c] = alpha * prenda_resized[:, :, c] + (1 - alpha) * roi
    else:
        mask = np.ones((new_h, new_w), dtype=np.float32) * 0.8
        for c in range(3):
            user_img[y:y+new_h, x:x+new_w, c] = mask * prenda_resized[:, :, c] + (1 - mask) * user_img[y:y+new_h, x:x+new_w, c]
    result_filename = f"result_{session['user_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
    result_path = os.path.join(app.config['UPLOAD_FOLDER'], result_filename)
    cv2.imwrite(result_path, user_img)
    return result_path

def create_placeholder_prenda():
    img = np.zeros((400, 300, 4), dtype=np.uint8)
    img[:, :] = (240, 240, 240, 255)
    cv2.rectangle(img, (50, 50), (250, 350), (100, 150, 200, 200), -1)
    cv2.putText(img, "PRENDA", (75, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255, 255), 2)
    return img

@app.route('/outfits', methods=['GET', 'POST'])
@login_required
def outfits():
    if request.method == 'POST':
        nombre = request.form['nombre']
        imagen_resultado = request.form.get('imagen_resultado', '')
        prendas_ids = request.form.getlist('prendas[]')
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO outfits (usuario_id, nombre, imagen_resultado) VALUES (%s, %s, %s)", (session['user_id'], nombre, imagen_resultado))
                outfit_id = cur.lastrowid
                for prenda_id in prendas_ids:
                    cur.execute("INSERT INTO outfit_prendas (outfit_id, prenda_id) VALUES (%s, %s)", (outfit_id, prenda_id))
                conn.commit()
        finally:
            conn.close()
        flash('Outfit guardado!', 'success')
        return redirect(url_for('dashboard'))
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM prendas ORDER BY nombre")
            prendas = cur.fetchall()
    finally:
        conn.close()
    return render_template('outfits.html', prendas=prendas)

@app.route('/api/outfits/<int:outfit_id>', methods=['DELETE'])
@login_required
def delete_outfit(outfit_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT usuario_id FROM outfits WHERE id = %s", (outfit_id,))
            outfit = cur.fetchone()
            if not outfit or outfit['usuario_id'] != session['user_id']:
                return jsonify({'error': 'No autorizado'}), 403
            cur.execute("DELETE FROM outfits WHERE id = %s", (outfit_id,))
            conn.commit()
    finally:
        conn.close()
    return jsonify({'success': True})

@app.route('/api/prendas')
def api_prendas():
    genero = request.args.get('genero')
    categoria = request.args.get('categoria')
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = "SELECT * FROM prendas WHERE 1=1"
            params = []
            if genero:
                query += " AND genero = %s"
                params.append(genero)
            if categoria:
                query += " AND categoria = %s"
                params.append(categoria)
            cur.execute(query, tuple(params))
            prendas = cur.fetchall()
    finally:
        conn.close()
    return jsonify(prendas)

@app.route('/toggle-theme', methods=['POST'])
def toggle_theme():
    current = session.get('theme', 'light')
    session['theme'] = 'dark' if current == 'light' else 'light'
    return jsonify({'theme': session['theme']})

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('index.html'), 500

if __name__ == '__main__':
    print("=" * 50)
    print(" AMAI SHOP - CONECTADO A PHPMYADMIN")
    print("=" * 50)
    print(" Abre: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)