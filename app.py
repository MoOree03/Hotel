import re
from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import os
import utils
from db import get_db
import functools

app = Flask(__name__)
app.secret_key = os.urandom(12)


@app.route('/', methods=['GET'])
def inicio():
    # Si inicio sesion -> Mostrar bienvenida, y cambio de navbar
    # Sino -> mantener rol de visitante
    return render_template('index.html')


@app.route('/iniciar', methods=['POST', 'GET'])
def iniciar():
    # Validar si es admin o usuario
    return render_template('iniciar.html')


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    try:
        if request.method == 'POST':
            nombre = request.form['nombre']
            tipo_documento = request.form['tipo']
            pais = request.form['pais']
            numero = request.form['numero']
            email = request.form['email']
            password = request.form['contrasena']
            confirma = request.form['confirma']
            telefono = request.form['telefono']
            error = None

            if not utils.isUsernameValid(nombre):
                error = "El usuario no es valido"
                flash(error)
                return render_template('Registro.html')

            if not utils.isNumberValid(numero):
                error = "El número de documento no es valido"
                flash(error)
                return render_template("Registro.html")

            if not utils.isEmailValid(email):
                error = "El email no es valido"
                flash(error)
                return render_template('Registro.html')

            if not utils.isPasswordValid(password):
                error = "La contraseña no es valida"
                flash(error)
                return render_template('Registro.html')

            if not utils.isPasswordValid(confirma):
                error = "La confirmación no es valida"
                if (password != confirma):
                    error = "La contraseña debe coincidir con la confirmación"
                    print(error)
                flash(error)
                return render_template('Registro.html')

            if not utils.isPhoneValid(telefono):
                error = "El número de telefono no es valido"
                flash(error)
                return render_template("Registro.html")

            try:
                terminos = request.form['terminos']
            except Exception as e:
                e = "Debe aceptar los terminos y condiciones antes de avanzar"
                flash(e)
                return render_template("Registro.html")

            db = get_db()

            demail = db.execute(
                'SELECT id FROM usuarios WHERE Email=?', (email,)).fetchone()
            user = db.execute(
                'SELECT id FROM usuarios WHERE Nombre=?', (nombre,)).fetchone()

            if user is not None:
                error = 'El usuario ya existe'.format(nombre)
                flash(error)

                return render_template('Registro.html')

            if demail is not None:
                error = 'El usuario ya existe'.format(email)
                flash(error)

                return render_template('Registro.html')

            try:
                db.execute('INSERT INTO usuarios (Nombre,Tipo_Documento,Numero,Pais,Email,Contraseña,Telefono) VALUES (?,?,?,?,?,?,?)',
                           (nombre, tipo_documento, numero, pais, email, generate_password_hash(password), telefono))
                db.commit()
                db.close()
                print("Guarda")
            except Exception as e:
                print(e)
            return redirect(url_for('iniciar'))

        return render_template('registro.html')
    except Exception as e:
        print(e)
        return render_template('registro.html')


@app.route('/recuperar', methods=['POST', 'GET'])
def recuperar():
    # validar que este registrado -> enviar correo
    return render_template('recuperar.html')


@app.route('/habitacion', methods=['GET'])
def habitacion():
    # Crear un buscador para filtrar habitaciones por nombre
    return render_template('habitacion.html')


@app.route('/reserva', methods=['POST', 'GET'])
def reserva():
    # Validad datos y registrar
    return render_template('reserva.html')


@app.route('/comentarios', methods=['GET'])
def comentarios():
    return render_template('comentarios.html')


@app.route('/calificacion', methods=['POST', 'GET'])
def calificacion():
    return render_template('calificacion.html')


@app.route('/herramientas', methods=['GET'])
def herramienta():
    return render_template('herramientas.html')


@app.route('/gestion', methods=['POST', 'GET'])
def gestion():
    return render_template('gestion.html')


@app.route('/editar', methods=['POST', 'GET'])
def editar():
    return render_template('editar.html')


@app.route('/agregar', methods=['POST', 'GET'])
def agregar():
    return render_template('agregar.html')


@app.route('/eliminar', methods=['POST', 'GET'])
def eliminar():
    return render_template('eliminar.html')


if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1', port=5000)
