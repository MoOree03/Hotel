import functools
from flask import Flask, render_template, request, flash, jsonify, redirect, g, url_for, session, send_file, \
    make_response
from werkzeug.security import generate_password_hash, check_password_hash

import yagmail as yagmail
import os
import utils
from db import get_db

app = Flask(__name__)
app.secret_key = os.urandom(12)


@app.route('/', methods=["GET"])
def inicio():
    # Si inicio sesion -> Mostrar bienvenida, y cambio de navbar
    # Sino -> mantener rol de visitante
    return render_template('index.html')


@app.route('/IniciarSesion', methods=["GET", "POST"])
def IniciarSesion():
    # Validar si es admin o usuario
    return render_template('IniciarSesion.html')


@app.route('/Registro', methods=('GET', 'POST'))
def Registro():
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
            print(nombre, tipo_documento, pais, numero,
                  email, password, confirma, telefono)
            if not utils.isUsernameValid(nombre):
                error = "El usuario no es valido"
                flash(error)
                print(error)
                return render_template('Registro.html')

            if not utils.isNumberValid(numero):
                error = "El número de documento no es valido"
                flash(error)
                print(error)
                return render_template("Registro.html")

            if not utils.isEmailValid(email):
                error = "El email no es valido"
                flash(error)
                print(error)
                return render_template('Registro.html')

            if not utils.isPasswordValid(password):
                error = "La contraseña no es valida"
                flash(error)
                print(error)
                return render_template('Registro.html')

            if not utils.isPasswordValid(confirma):
                error = "La confirmación no es valida"
                print(error)
                if (password != confirma):
                    error = "La contraseña debe coincidir con la confirmación"
                    print(error)
                flash(error)
                print(error)
                return render_template('Registro.html')
            if not utils.isPhoneValid(telefono):
                error = "El número de telefono no es valido"
                print(error)
                flash(error)
                return render_template("Registro.html")
            try:
                terminos = request.form['terminos']
            except Exception as e:
                e = "Debe aceptar los terminos y condiciones antes de avanzar"
                flash(e)
                print(e)
                return render_template("Registro.html")

            db = get_db()

            user = db.execute(
                'SELECT id FROM usuarios WHERE Email=?', (email,)).fetchone()
            user = db.execute(
                'SELECT id FROM usuarios WHERE Nombre=?', (nombre,)).fetchone()

            if user is not None:
                error = 'El usuario ya existe'.format(email)
                flash(error)
                print("Probem")
                return render_template('Registro.html')
            try:
                db.execute('INSERT INTO usuarios (Nombre,Tipo_Documento,Numero,Pais,Email,Contraseña,Telefono) VALUES (?,?,?,?,?,?,?)',
                           (nombre, tipo_documento, numero, pais, email, generate_password_hash(password), telefono))
                db.commit()
                db.close()
                print("Guarda")
            except Exception as e:
                print(e)
            return redirect(url_for('IniciarSesion'))

        return render_template('Registro.html')
    except Exception as e:
        print(e)
        return render_template('Registro.html')


@app.route('/Recuperar', methods=["GET", "POST"])
def Recuperar():
    # validar que este registrado -> enviar correo
    return render_template('Recuperar.html')


@app.route('/Habitacion', methods=["GET"])
def Habitacion():
    # Crear un buscador para filtrar habitaciones por nombre
    return render_template('Habitacion.html')


@app.route('/Reserva', methods=["GET", "POST"])
def Reserva():
    # Validad datos y registrar
    return render_template('Reserva.html')


@app.route('/Comentarios', methods=["GET"])
def Comentarios():
    return render_template('Comentarios.html')


@app.route('/Calificacion', methods=["GET", "POST"])
def Calificacion():
    return render_template('Calificacion.html')


@app.route('/Herramientas', methods=["GET"])
def Herramienta():
    return render_template('Herramientas.html')


@app.route('/GestionComentarios', methods=["GET", "POST"])
def GestionComentarios():
    return render_template('GestionComentarios.html')


@app.route('/Editar', methods=["GET", "POST"])
def Editar():
    return render_template('Editar.html')


@app.route('/Agregar', methods=["GET", "POST"])
def Agregar():
    return render_template('Agregar.html')


@app.route('/Eliminar', methods=["GET", "POST"])
def Eliminar():
    return render_template('Eliminar.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
