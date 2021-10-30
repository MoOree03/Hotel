import re
from flask import Flask, render_template, request, flash, redirect, url_for, session,\
    g
import yagmail
from werkzeug.security import generate_password_hash, check_password_hash
import os
import utils
from db import get_db
import functools

correo_envia = 'mintic202221@gmail.com'
contraseña_envia = 'Mintic2022'
yag = yagmail.SMTP(user=correo_envia, password=contraseña_envia)

tema_registro = 'Activa tu cuenta'
contenido_registro = [
    'Estas a un paso de completar tu registro en HyattLumpur Hotel\n'
    'Da clic en el siguiente link\n'
    'link'
]
tema_reserva = 'Recibo de su reserva'

tema_recupera = '¿Olvidaste tu contraseña'
recupera_contenido = [
    'Para restablecer tu contraseña da click en el siguiente enlace\n'
    'ENLACE'
]

app = Flask(__name__)
app.secret_key = os.urandom(12)
inicioS = False
admin = False
superAdmin= False


@app.route('/', methods=['GET'])
def inicio():
    # Si inicio sesion -> Mostrar bienvenida, y cambio de navbar
    # Sino -> mantener rol de visitante
    return render_template('index.html', inicioS=inicioS)


@app.route('/iniciar', methods=['POST', 'GET'])
def iniciar():
    global inicioS
    global admin
    global superAdmin
    try:
        if request.method == 'POST':
            username = request.form['usuario']
            password = request.form['password']
            error = None
            if not username:
                error = 'Debes ingresar un usuario'
                flash(error)
                return render_template('iniciar.html')

            if not password:
                error = 'Debes ingresar una contraseña'
                flash(error)
                return render_template('iniciar.html')
            db = get_db()
            user = db.execute(
                'SELECT * FROM usuarios WHERE Nombre= ?', (username, )).fetchone()

            lista = db.execute(
                'SELECT habitacion FROM habitaciones WHERE estado = "Disponible" ').fetchall()
            db.close()
            if user is None:
                error = 'Usuario o contraseña inválidos'
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
            if adminL == 'SuperAdmin':
                superAdmin = True
            inicioS = True
            return redirect(url_for('reserva'))
        return render_template('iniciar.html', inicioS=inicioS)
    except Exception as e:
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
            if superAdmin==True:
                return view(**kwargs)
            return redirect(url_for('inicio'))
        return view(**kwargs)
    return wrapped_view

def super_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None or superAdmin == False:
            return redirect(url_for('inicio'))
        return view(**kwargs)
    return wrapped_view

@app.route('/salir')
def salir():
    global inicioS
    global admin
    global superAdmin
    inicioS = False
    admin = False
    superAdmin=False
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
                yag.send(to=email, subject=tema_registro,
                         contents=contenido_registro)
                exito = True
                render_template('registro.html')
            except Exception as e:
                print("")
            return redirect(url_for('iniciar'))

        return render_template('registro.html')
    except Exception as e:
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
            if validacion is None:
                error = 'El usuario no existe'.format(email)
                flash(error)
                return render_template('recuperar.html')
            exito = True
            flash('Hemos enviado un mensaje a su correo')
            yag.send(to=email, subject=tema_recupera,
                     contents=recupera_contenido)
            return render_template('recuperar.html', inicioS=inicioS, exito=exito)
        return render_template('recuperar.html', inicioS=inicioS)
    except Exception as e:
        return render_template('recuperar.html', inicioS=inicioS)


@app.route('/habitacion', methods=['GET'])
def habitacion():
    return render_template('habitacion.html', inicioS=inicioS)


@app.route('/reserva', methods=['POST', 'GET'])
@login_required
def reserva():
    db = get_db()
    lista = db.execute(
        'SELECT habitacion FROM habitaciones WHERE estado = "Disponible"').fetchall()
    listaN = db.execute(
        'SELECT habitacion FROM habitaciones').fetchall()
    listaA = db.execute(
        'SELECT habitacion FROM habitaciones WHERE estado="Ocupado"').fetchall()
    if len(listaN)==len(listaA):
        flash ("No hay habitaciones disponibles, intente más tarde")
        return render_template("reserva.html",inicioS=inicioS,lista=lista)
    
    try:
        if request.method == 'POST':
            llegada = request.form['llegada']
            salida = request.form['salida']
            habitacion = request.form['habi']
            numero = request.form['numero']
            error = None
            exito = False
            habitacion = habitacion.replace('(', '')
            habitacion = habitacion.replace(')', '')
            habitacion = habitacion.replace("'", "")
            habitacion = habitacion.replace(',', '')
            try:
                terminos = request.form['terminos']
            except Exception as e:
                e = "Debe aceptar los terminos y condiciones antes de avanzar"
                flash(e)
                return render_template("reserva.html",lista=lista)
            disponibilidad = db.execute(
                'SELECT estado FROM habitaciones WHERE habitacion= :habitacion', {"habitacion": habitacion}).fetchone()

            user_email = db.execute(
                'SELECT Email FROM usuarios WHERE id=?', (session.get('user_id'),)).fetchone()
            habita = db.execute(
                'SELECT habitacion FROM habitaciones WHERE habitacion= ?', (habitacion,)).fetchone()

            if disponibilidad == ('Ocupada',):
                error = 'Habitación ocupada, seleccione otra'.format(
                    disponibilidad)
                flash(error)
                return render_template('reserva.html',lista=lista)

            try:

                db.execute('INSERT INTO Reservas (Llegada,Salida,id_Habitacion,NumeroPersonas,id_usuario) VALUES (?,?,?,?,?)',
                           (llegada, salida, habitacion, numero, session.get('user_id')))

                db.execute(
                    'UPDATE habitaciones SET estado = "Ocupada" WHERE habitacion =?', (habita))
                db.commit()
                db.close()
                exito = True
                flash("La reserva se ha completado exitosamente")
                contenido = ('Ha realizado una reserva para el dia %s hasta %s en la habitacion %s para %s personas\n ¡Esperamos que nuestras instalaciones sean de su agrado!') % (
                    llegada, salida, habitacion, numero)
                yag.send(to=user_email, subject=tema_reserva,
                         contents=contenido)
            except Exception as e:
                flash(e)
            return render_template('reserva.html', inicioS=inicioS, exito=exito, lista=lista)
        return render_template('reserva.html', inicioS=inicioS, lista=lista)
    except Exception as e:
        return render_template('reserva.html', inicioS=inicioS,lista=lista)


@app.route('/calificacion', methods=['GET', 'POST'])
@login_required
def calificacion():
    db = get_db()
    lista = db.execute(
        'SELECT habitacion FROM habitaciones WHERE estado = "Disponible" ').fetchall()
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
            id_user = session.get('user_id')
            try:
                numero = db.execute(
                    'SELECT * FROM Reservas WHERE id_usuario= ?', (id_user,)).fetchone()
                nombre = db.execute(
                    'SELECT Nombre FROM usuarios WHERE id=?', (id_user,)).fetchone()
                llegada = db.execute(
                    'SELECT llegada FROM Reservas WHERE id_usuario= ?', (id_user,)).fetchone()
                nombre=str(nombre)
                llegada=str(llegada)
                id_hab = numero[3]
                db.execute('INSERT INTO Comentarios (Calificacion,Comentario,id_Usuario,id_Habitacion,id_llegada) VALUES (?,?,?,?,?)',
                           (promedio, comentario, nombre, id_hab, llegada))
                db.commit()
                db.close()
                exito = True
                flash("Gracias por comentar su experiencia!")
            except Exception as e:
                flash("Primero debes reservar una habitación")
                return render_template('reserva.html', inicioS=inicioS, exito=exito, lista=lista)
            return render_template('calificacion.html', inicioS=inicioS, exito=exito)
        return render_template('calificacion.html', inicioS=inicioS)
    except Exception as e:
        return render_template('calificacion.html', inicioS=inicioS)


@app.route('/comentarios', methods=['GET'])
def comentarios():
    try:
        db = get_db()
        nombre = db.execute(
            'SELECT id_Usuario FROM Comentarios').fetchall()
        fecha = db.execute(
            'SELECT id_llegada FROM Comentarios').fetchall()
        comentarios = db.execute(
            'SELECT Comentario FROM Comentarios').fetchall()
        tamano = len(comentarios)  
        for i in range(len(nombre)):
            nombre[i]=str(nombre[i]).replace('(','')
            nombre[i]=str(nombre[i]).replace(')','')
            nombre[i]=str(nombre[i]).replace("'","")
            nombre[i]=str(nombre[i]).replace(",","")
            nombre[i]=str(nombre[i]).replace('"','')
        for i in range(len(fecha)):
            fecha[i]=str(fecha[i]).replace('(','')
            fecha[i]=str(fecha[i]).replace(')','')
            fecha[i]=str(fecha[i]).replace("'","")
            fecha[i]=str(fecha[i]).replace(",","")
            fecha[i]=str(fecha[i]).replace('"','')
        for i in range(len(comentarios)):
            comentarios[i]=str(comentarios[i]).replace('(','')
            comentarios[i]=str(comentarios[i]).replace(')','')
            comentarios[i]=str(comentarios[i]).replace("'","")
            comentarios[i]=str(comentarios[i]).replace(",","")
            comentarios[i]=str(comentarios[i]).replace('"','')
        
        db.commit()
        db.close()
        return render_template('comentarios.html', inicioS=inicioS, nombre=nombre, fecha=fecha, comentarios=comentarios,tamano=tamano)
    except Exception as e:
        flash(e)
    return render_template('comentarios.html', inicioS=inicioS)


@app.route('/herramientas', methods=['GET'])
@admin_required
def herramienta():
    return render_template('herramientas.html',superAdmin=superAdmin)


@app.route('/gestion', methods=['POST', 'GET'])
@admin_required
def gestion():
    try:
        if request.method == 'POST':
            try:
                db = get_db()
                comentarios = db.execute(
                    'SELECT id,id_Usuario,Calificacion,Comentario FROM Comentarios').fetchall()
                for i in comentarios:
                    flash(i, category='warning')
            except Exception as e:
                print("")
            try:
                terminos = request.form['terminos']
            except Exception as e:
                return render_template('gestion.html')

            try:
                eliminar = request.form['eliminar']
                db.execute(
                    'DELETE FROM Comentarios WHERE id = ?', (eliminar,))
                db.commit()
                db.close()
                flash("El comentario fue eliminado exitosamente",
                      category='success')
                
                return render_template('gestion.html')
            except Exception as e:
                return render_template('gestion.html')
    except Exception as e:
        print("")
        return render_template('gestion.html')
    return render_template('gestion.html')


@app.route('/editar', methods=['POST', 'GET'])
@admin_required
def editar():
    try:
        if request.method == 'POST':
            try:
                db = get_db()
                habitaciones = db.execute(
                    'SELECT habitacion,estado FROM habitaciones').fetchall()
                
                for i in habitaciones:
                    flash(i, category='info')
                
            except Exception as e:
                flash(e)
            try:
                db = get_db()
                id_habitacion = request.form['id']
                id_habi = db.execute('SELECT habitacion FROM habitaciones WHERE habitacion = :id', {
                                     "id": id_habitacion}).fetchone()
                nombre = request.form['nombre']

                if len(nombre) >= 3:
                    db.execute(
                        'UPDATE habitaciones SET habitacion = :nombre WHERE habitacion = :id', {"nombre": nombre, "id": id_habi[0]})
                    db.commit()
                    flash("Se realizo la edición de la habitación",
                          category='success')
                    return render_template('editar.html')
            except Exception as e:
                return render_template('editar.html')
            try:
                db = get_db()
                disponibilidad = request.form['disponibilidad']
                db.execute(
                    'UPDATE habitaciones SET estado = :estado WHERE habitacion = :id', {"estado": disponibilidad, "id": id_habi[0]})
                db.commit()
                db.close()
                flash("Se realizo la edición de la habitación", category='success')
                return render_template('editar.html')
            except Exception as e:
                return render_template('editar.html')
        return render_template('editar.html')
    except Exception as e:
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
            try:
                crear = request.form['crear']
                if len(crear) >= 3:
                    db.execute(
                        'INSERT INTO habitaciones (habitacion,estado) VALUES(?,?)', (crear, "Disponible"))
                    db.commit()
                    db.close()
                    exito = True
                    flash("La habitación fue creada exitosamente",
                          category='success')
                    return render_template('agregar.html', exito=exito)
            except Exception as e:
                return render_template('agregar.html')
        return render_template('agregar.html', exito=exito)
    except Exception as e:
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
                    flash(i,category="info")
            except Exception as e:
                flash(e)

            

            try:
                eliminar = request.form['eliminar']
                if len(eliminar) >= 3:
                    db.execute(
                        'DELETE FROM habitaciones WHERE habitacion = ?', (eliminar,))
                    db.commit()
                    db.close()
                    exito = True
                    try:
                        terminos = request.form['confirma']
                    except Exception as e:
                        flash("Debe confirmar eliminación",category="error")
                        return render_template("eliminar.html")
                    flash("La habitación fue eliminada exitosamente",
                          category='success')
                    return render_template('eliminar.html', exito=exito)
                flash("Debe ingresar habitación a eliminar",category="error")
                return render_template('eliminar.html', exito=exito)
            except Exception as e:
                exito = False
                return render_template('eliminar.html', exito=exito)
    except Exception as e:
        return render_template('eliminar.html')
    return render_template('eliminar.html')

@app.route('/superUser', methods=['GET','POST'])
@super_required
def superUser ():
    db = get_db()
    try:
        if request.method == 'POST':
            try:
                usuarios = db.execute(
                    'SELECT id, Nombre,rol FROM usuarios').fetchall()
                for i in usuarios:
                    flash(i, category='info')

            except Exception as e:
                flash(e)
                return render_template('superUser.html')
            try:
                id_seleccionado = request.form['id']
                while len(id_seleccionado) <1 :
                    id_seleccionado = request.form['id']
                    flash("Debe ingresar el id de usuario",category="error")
                    return render_template('superUser.html')
                nuevo = request.form['nuevo']
                if(len(nuevo)>0):
                    db.execute(
                        'UPDATE usuarios SET Nombre = :nombre WHERE id = :id', {"nombre": nuevo, "id":id_seleccionado})
                    db.commit()
                    flash("Se realizo la edicion del nombre de usuario",
                            category='success')
                    return render_template('superUser.html')
            except Exception as e:
                print("")
                
                
            try:
                
                rol = request.form['estado']
                db.execute(
                    'UPDATE usuarios SET rol = :estado WHERE id = :id', {"estado": rol, "id":id_seleccionado})
                db.commit()
                
                flash("Se realizo la edición del rol", category='success')
                return render_template('superUser.html')
            except Exception as e:
                print("")
            try:
                db = get_db()
                print("a")
                eliminar = request.form['eliminar']
                print("a")
                while len(eliminar) <1 :
                    eliminar = request.form['eliminar']
                    print("b")
                    flash("Debe ingresar el id de usuario",category="error")
                    return render_template('superUser.html')
                db.execute(
                    'DELETE FROM usuarios WHERE id = ?', (eliminar,))
                db.commit()
                try:
                    terminos = request.form['confirmar']
                except Exception as e:
                    print(e)
                    flash("Debe confirmar eliminación",category="error")
                    return render_template("superUser.html")
                flash("Se realizo la eliminación del usuario", category='success')
                return render_template('superUser.html')
            except Exception as e:
                print(e)
                return render_template('superUser.html')
        return render_template('superUser.html')
    except Exception as e:
        print(e)
        return render_template('superUser.html')
    

if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1', port=5000)
