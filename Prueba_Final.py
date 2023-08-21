from flask import Flask, jsonify, request
import re, bcrypt, mysql.connector

app = Flask(__name__)

# Configuración de la conexión con la base de datos
conexion_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'linux',
    'database': 'gir3091'
}

def get_db_connection():
    return mysql.connector.connect(**conexion_config)

@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    cnx = get_db_connection()
    cursor = cnx.cursor(dictionary=True)
    
    cursor.execute("SELECT correo, password FROM usuarios")
    result = cursor.fetchall()

    cursor.close()
    cnx.close()

    return jsonify(result), 200

def es_password_valida(password):
    if len(password) < 8:
        return False
    if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password):
        return False
    return True

@app.route('/usuarios', methods=['POST'])
def add_usuarios():
    data = request.get_json()

    if 'correo' not in data:
        return {'error':'Falta el campo correo'}, 400

    if 'password' not in data or not es_password_valida(data['password']):
        return {'error':'La contraseña es inválida'}, 400

    cnx = get_db_connection()
    cursor = cnx.cursor(dictionary=True)

    cursor.execute("SELECT correo FROM usuarios WHERE correo = %s", (data['correo'],))
    existing_user = cursor.fetchone()

    if existing_user:
        cursor.close()
        cnx.close()
        return {'error':'Este usuario ya está registrado'}, 409

    hashed_pw = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    data['password'] = hashed_pw.decode('utf-8')
    
    cursor.execute("INSERT INTO usuarios (correo, password) VALUES (%s, %s)", (data['correo'], data['password']))
    cnx.commit()

    cursor.close()
    cnx.close()

    return {'success':'Registro agregado con éxito'}, 201

@app.route('/alumnos', methods=['GET'])
def get_alumnos():
    cnx = get_db_connection()
    cursor = cnx.cursor(dictionary=True)
    
    cursor.execute("SELECT nombre, email, carrera, cuatrimestre, edad, numero_control, promedio FROM alumnos")
    result = cursor.fetchall()

    cursor.close()
    cnx.close()

    return jsonify(result), 200

@app.route('/alumnos', methods=['POST'])
def add_alumno():
    data = request.get_json()

    required_fields = ['usuario_id', 'nombre', 'email', 'carrera', 'cuatrimestre', 'edad', 'numero_control', 'promedio']

    if not all(key in data for key in required_fields):
        return {'error':'Faltan campos requeridos'}, 400

    cnx = get_db_connection()
    cursor = cnx.cursor(dictionary=True)

    cursor.execute("INSERT INTO alumnos (usuario_id, nombre, email, carrera, cuatrimestre, edad, numero_control, promedio) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                   (data['usuario_id'], data['nombre'], data['email'], data['carrera'], data['cuatrimestre'], data['edad'], data['numero_control'], data['promedio']))
    cnx.commit()

    cursor.close()
    cnx.close()

    return {'success':'Alumno agregado con éxito'}, 201

@app.route('/materias', methods=['GET'])
def get_materias():
    cnx = get_db_connection()
    cursor = cnx.cursor(dictionary=True)
    
    cursor.execute("SELECT nombre_materia, carrera, cantidad_alumnos, area, periodo, maestro, edificio FROM materias")
    result = cursor.fetchall()

    cursor.close()
    cnx.close()

    return jsonify(result), 200

@app.route('/materias', methods=['POST'])
def add_materia():
    data = request.get_json()

    required_fields = ['usuario_id', 'nombre_materia', 'carrera', 'cantidad_alumnos', 'area', 'periodo', 'maestro', 'edificio']

    if not all(key in data for key in required_fields):
        return {'error':'Faltan campos requeridos'}, 400

    cnx = get_db_connection()
    cursor = cnx.cursor(dictionary=True)

    cursor.execute("INSERT INTO materias (usuario_id, nombre_materia, carrera, cantidad_alumnos, area, periodo, maestro, edificio) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                   (data['usuario_id'], data['nombre_materia'], data['carrera'], data['cantidad_alumnos'], data['area'], data['periodo'], data['maestro'], data['edificio']))
    cnx.commit()

    cursor.close()
    cnx.close()

    return {'success':'Materia agregada con éxito'}, 201

if __name__ == "__main__":
    app.run(debug=True)
