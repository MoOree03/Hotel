from flask import Flask
from flask import render_template
from flask import redirect
from flask import request

app = Flask(__name__)


@app.route('/', methods=["GET"])
def inicio():
    # Si inicio sesion -> Mostrar bienvenida, y cambio de navbar
    # Sino -> mantener rol de visitante
    return render_template('index.html')


@app.route('/IniciarSesion', methods=["GET", "POST"])
def IniciarSesion():
    # Validar si es admin o usuario
    return render_template('IniciarSesion.html')


@app.route('/Registro', methods=["GET", "POST"])
def Registro():
    # validar espacios
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
