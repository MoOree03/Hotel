import re
from flask import Flask, render_template, request, flash, redirect, url_for, session,\
    make_response, g
from werkzeug.security import generate_password_hash, check_password_hash
import os
import utils
from db import get_db
import functools


app = Flask(__name__)
app.secret_key = os.urandom(12)
inicioS = False
admin = False


@app.route('/', methods=['GET'])
def inicio():
    # Si inicio sesion -> Mostrar bienvenida, y cambio de navbar
    # Sino -> mantener rol de visitante
    return render_template('index.html', inicioS=inicioS)


@app.route('/iniciar', methods=['POST', 'GET'])
def iniciar():
    global inicioS
    global admin
    try:
        if request.method == 'POST':
            username = request.form['usuario']
            password = request.form['password']
            error = None
            if not username:
                error = 'Debes ingresar un usuario'
                flash(error)
                print(error)
                return render_template('iniciar.html')

            if not password:
                error = 'Debes ingresar una contraseña'
                flash(error)
                print(error)
                return render_template('iniciar.html')
            db = get_db()
            user = db.execute(
                'SELECT * FROM usuarios WHERE Nombre= ?', (username, )).fetchone()
            db.close()
            if user is None:
                error = 'Usuario o contraseña inválidos'
                print(error)
                flash(error)
                return render_template('iniciar.html')
            else:
                store_password = user[6]
                result = check_password_hash(store_password, password)
                if result is False:
                    error = 'Usuario o contraseña inválidos'
                    flash(error)
                    return render_template('iniciar.html')
                else:
                    session.clear()
                    inicioS = False
                    session['user_id'] = user[0]
            adminL = user[8]
            if adminL == 'Admin':
                admin = True
            inicioS = True
            return render_template('reserva.html',inicioS=inicioS)
        return render_template('iniciar.html', inicioS=inicioS)
    except Exception as ex:
        print(ex)
        return render_template('iniciar.html')


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('iniciar'))
        return view(**kwargs)
    return wrapped_view


def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None or admin == False:
            return redirect(url_for('inicio'))
        return view(**kwargs)
    return wrapped_view


@app.route('/salir')
def salir():
    global inicioS
    global admin
    inicioS = False
    admin = False
    session.clear()
    return redirect(url_for('inicio'))


@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        db = get_db()
        g.user = db.execute(
            'SELECT * FROM usuarios WHERE id = ?', (user_id, )).fetchone()


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
            exito = False
            if not utils.isUsernameValid(nombre):
                error = "El usuario no es valido"
                flash(error)
                return render_template('registro.html')

            if not utils.isNumberValid(numero):
                error = "El número de documento no es valido"
                flash(error)
                return render_template("registro.html")

            if not utils.isEmailValid(email):
                error = "El email no es valido"
                flash(error)
                return render_template('registro.html')

            if not utils.isPasswordValid(password):
                error = "La contraseña no es valida"
                flash(error)
                return render_template('registro.html')

            if not utils.isPasswordValid(confirma):
                error = "La confirmación no es valida"
                if (password != confirma):
                    error = "La contraseña debe coincidir con la confirmación"
                    print(error)
                flash(error)
                return render_template('registro.html')

            if not utils.isPhoneValid(telefono):
                error = "El número de telefono no es valido"
                flash(error)
                return render_template("registro.html")

            try:
                terminos = request.form['terminos']
            except Exception as e:
                e = "Debe aceptar los terminos y condiciones antes de avanzar"
                flash(e)
                return render_template("registro.html")

            db = get_db()

            demail = db.execute(
                'SELECT id FROM usuarios WHERE Email=?', (email,)).fetchone()
            user = db.execute(
                'SELECT id FROM usuarios WHERE Nombre=?', (nombre,)).fetchone()

            if user is not None:
                error = 'El usuario ya existe'.format(nombre)
                flash(error)

                return render_template('registro.html')

            if demail is not None:
                error = 'El usuario ya existe'.format(email)
                flash(error)

                return render_template('registro.html')

            try:
                db.execute('INSERT INTO usuarios (Nombre,Tipo_Documento,Numero,Pais,Email,Contraseña,Telefono) VALUES (?,?,?,?,?,?,?)',
                           (nombre, tipo_documento, numero, pais, email, generate_password_hash(password), telefono))
                db.commit()
                db.close()

                print("Guarda")
                exito = True
                render_template('registro.html')
            except Exception as e:
                print(e)
            return redirect(url_for('iniciar'))

        return render_template('registro.html')
    except Exception as e:
        print(e)
        return render_template('registro.html')


@app.route('/recuperar', methods=['POST', 'GET'])
def recuperar():
    try:
        if request.method == 'POST':
            email = request.form['email']
            error = None
            exito = False

            if not utils.isEmailValid(email):
                error = "El email no es valido"
                flash(error)
                return render_template('recuperar.html')

            db = get_db()

            validacion = db.execute(
                'SELECT Email FROM usuarios WHERE Email=?', (email,)).fetchone()
            print(validacion)
            if validacion is None:
                error = 'El usuario no existe'.format(email)
                flash(error)
                return render_template('recuperar.html')

            exito = True
            flash('Hemos enviado un mensaje a su correo')
            return render_template('recuperar.html', inicioS=inicioS, exito=exito)
        return render_template('recuperar.html', inicioS=inicioS)
    except Exception as e:
        return render_template('recuperar.html', inicioS=inicioS)


@app.route('/habitacion', methods=['GET'])
def habitacion():
    # Crear un buscador para filtrar habitaciones por nombre
    return render_template('habitacion.html', inicioS=inicioS)


@app.route('/reserva', methods=['POST', 'GET'])
@login_required
def reserva():
    try:
        if request.method == 'POST':
            llegada = request.form['llegada']
            salida = request.form['salida']
            habitacion = request.form['habi']
            numero = request.form['numero']

            error = None
            exito = False

            if not utils.isDateValid(llegada):
                error = "La fecha de llegada no es valida"
                flash(error)
                return render_template('reserva.html')

            if not utils.isDateValid(salida):
                error = "La fecha de salida no es valida"
                flash(error)
                return render_template('reserva.html')

            try:
                terminos = request.form['terminos']
            except Exception as e:
                e = "Debe aceptar los terminos y condiciones antes de avanzar"
                flash(e)
                return render_template("reserva.html")

            db = get_db()

            disponibilidad = db.execute(
                'SELECT estado FROM habitaciones WHERE habitacion=?', (habitacion,)).fetchone()
            habita = db.execute(
                'SELECT Habitacion FROM Habitaciones WHERE Habitacion=?', (habitacion,)).fetchone()

            if disponibilidad == ('Ocupada',):
                error = 'Habitación ocupada, seleccione otra'.format(
                    disponibilidad)
                flash(error)
                return render_template('reserva.html')
            try:
                db.execute('INSERT INTO Reservas (Llegada,Salida,id_Habitacion,NumeroPersonas,id_usuario) VALUES (?,?,?,?,?)',
                           (llegada, salida, habitacion, numero, session.get('user_id')))
                db.execute(
                    'UPDATE habitaciones SET estado = "Ocupada" WHERE habitaciones.habitacion =?', (habita))
                db.commit()
                db.close()
                exito = True
                flash("La reserva se ha completado exitosamente")
            except Exception as e:
                flash(e)
                print(e)
            return render_template('reserva.html', inicioS=inicioS, exito=exito)
        return render_template('reserva.html',inicioS=inicioS)
    except Exception as e:
        return render_template('reserva.html',inicioS=inicioS)


@app.route('/calificacion', methods=['GET', 'POST'])
@login_required
def calificacion():
    try:
        if request.method == 'POST':
            limpieza = request.form['limpieza']
            atencion = request.form['atencion']
            conectividad = request.form['conectividad']
            servicio = request.form['habitacion']
            comentario = request.form['comentario']
            exito = False
            promedio = float((int(limpieza) + int(atencion) +
                             int(conectividad) + int(servicio)))/4
            print(promedio)
            db = get_db()
            id_user = session.get('user_id')
            print(id_user)
            try:
                numero = db.execute(
                    'SELECT * FROM Reservas WHERE id_usuario= ?', (id_user,)).fetchone()
                id_hab = numero[3]
                db.execute('INSERT INTO Comentarios (Calificacion,Comentario,id_Usuario,id_Habitacion) VALUES (?,?,?,?)',
                           (promedio, comentario, session.get('user_id'), id_hab))
                db.commit()
                db.close()
                exito = True
                flash("Gracias por comentar su experiencia!")
            except Exception as e:
                flash("Primero debes reservar una habitación")
                print(e)
            return render_template('calificacion.html', inicioS=inicioS, exito=exito)
        return render_template('calificacion.html', inicioS=inicioS)
    except Exception as e:
        print(e)
        return render_template('calificacion.html', inicioS=inicioS)


@app.route('/comentarios', methods=['GET'])
def comentarios():
    return render_template('comentarios.html', inicioS=inicioS)


@app.route('/herramientas', methods=['GET'])
@admin_required
def herramienta():
    return render_template('herramientas.html')


@app.route('/gestion', methods=['POST', 'GET'])
@admin_required
def gestion():
    try:
        if request.method == 'POST':
            try:
                db = get_db()
                comentarios = db.execute(
                    'SELECT Comentario FROM Comentarios').fetchall()
                calificacion = db.execute(
                    'SELECT Calificacion FROM Comentarios').fetchall()
                usuarios = db.execute(
                    'SELECT id_Usuario FROM Comentarios').fetchall()
                for i in comentarios:
                    flash(i, category='warning')
                for a in calificacion:
                    flash(a, category='info')
                for b in usuarios:
                    flash(b, category='error')
            except Exception as e:
                print(e)
            try:
                terminos = request.form['terminos']
            except Exception as e:
                print("Debe aceptar los términos y condiciones antes de avanzar")
                return render_template('gestion.html')

            try:
                eliminar = request.form['eliminar']
                print(eliminar)
                db.execute(
                    'DELETE FROM Comentarios WHERE id_Usuario = ?', (eliminar,))
                db.commit()
                db.close()
                flash("El comentario fue eliminada exitosamente",
                      category='success')
                return render_template('gestion.html')
            except Exception as e:
                print(e)
                return render_template('gestion.html')
    except Exception as e:
        print(e)
        return render_template('gestion.html')
    return render_template('gestion.html')


@app.route('/editar', methods=['POST', 'GET'])
@admin_required
def editar():
    try:
        exito = False
        consulta = False
        if request.method == 'POST':
            try:
                db = get_db()
                habitaciones = db.execute(
                    'SELECT habitacion FROM habitaciones').fetchall()
                estado = db.execute(
                    'SELECT estado FROM habitaciones').fetchall()
                for i in habitaciones:
                    flash(i, category='info')
                for i in estado:
                    flash(i, category='error')
            except Exception as e:
                flash(e)
                print(e)
            print("entra")
            try:
                db = get_db()
                id_habitacion = request.form['id']
                id_habi = db.execute('SELECT habitacion FROM habitaciones WHERE habitacion = :id', {
                                     "id": id_habitacion}).fetchone()
                nombre = request.form['nombre']
                print(nombre)
                print(id_habi[0])
                print(type(id_habi))

                if len(nombre) >= 3:
                    db.execute(
                        'UPDATE habitaciones SET habitacion = :nombre WHERE habitacion = :id', {"nombre": nombre, "id": id_habi[0]})
                    print("Funciona")
                    db.commit()
                    flash("Se realizo la edición de la habitación",
                          category='success')
                    return render_template('editar.html')
            except Exception as e:
                print(e)
                print("Valio")
                return render_template('editar.html')
            try:
                db = get_db()
                disponibilidad = request.form['disponibilidad']
                db.execute(
                    'UPDATE habitaciones SET estado = :estado WHERE habitacion = :id', {"estado": disponibilidad, "id": id_habi[0]})
                print("Funciona")
                db.commit()
                db.close()
                flash("Se realizo la edición de la habitación", category='success')
                return render_template('editar.html')
            except Exception as e:
                print(e)
                print("Valio")
                return render_template('editar.html')
        return render_template('editar.html')
    except Exception as e:
        print(e)
        return render_template('editar.html')


@app.route('/agregar', methods=['POST', 'GET'])
@admin_required
def agregar():
    try:
        exito = False
        consulta = False
        if request.method == 'POST':
            try:
                db = get_db()
                habitaciones = db.execute(
                    'SELECT habitacion FROM habitaciones').fetchall()
                for i in habitaciones:
                    flash(i)
            except Exception as e:
                flash(e)
                print(e)
            print("entra")
            try:
                crear = request.form['crear']
                if len(crear) >= 3:
                    print(crear)
                    db.execute(
                        'INSERT INTO habitaciones (habitacion,estado) VALUES(?,?)', (crear, "Disponible"))
                    db.commit()
                    db.close()
                    exito = True
                    flash("La habitación fue creada exitosamente",
                          category='success')
                    return render_template('agregar.html', exito=exito)
            except Exception as e:
                print(e)
                return render_template('agregar.html')
        return render_template('agregar.html', exito=exito)
    except Exception as e:
        print(e)
        return render_template('agregar.html', exito=exito)


@app.route('/eliminar', methods=['POST', 'GET'])
@admin_required
def eliminar():
    try:
        exito = False
        if request.method == 'POST':
            try:
                db = get_db()
                habitaciones = db.execute(
                    'SELECT habitacion FROM habitaciones').fetchall()
                for i in habitaciones:
                    flash(i)
            except Exception as e:
                flash(e)
                print(e)

            try:
                terminos = request.form['confirma']
            except Exception as e:
                print("Debe aceptar los términos y condiciones antes de avanzar")
                return render_template("eliminar.html")

            try:
                eliminar = request.form['eliminar']
                if len(eliminar) >= 3:
                    print(eliminar)
                    db.execute(
                        'DELETE FROM habitaciones WHERE habitacion = ?', (eliminar,))
                    db.commit()
                    db.close()
                    exito = True
                    flash("La habitación fue eliminada exitosamente",
                          category='success')
                    return render_template('eliminar.html', exito=exito)
            except Exception as e:
                exito = False
                print(e)
                return render_template('eliminar.html', exito=exito)
    except Exception as e:
        print(e)
        return render_template('eliminar.html')
    return render_template('eliminar.html')


if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1', port=5000)
