from flask import Flask
from flask import render_template
from flask import redirect
from flask import request

app = Flask(__name__)

lista_habitaciones = ["a", "b"]


ingreso = False


@app.route('/', methods=["GET"])
def inicio():
    # Si inicio sesion -> Mostrar bienvenida, y cambio de navbar
    # Sino -> mantener rol de visitante
    return render_template('index.html', ingreso=ingreso)


@app.route('/iniciarSesion', methods=["GET", "POST"])
def ingreso():
    global ingreso
    if request.method == "GET":
        return render_template('iniciarSesion.html')
    else:
        ingreso = True
        return redirect("/")


@app.route('/salida', methods=["POST"])
def salida():
    global ingreso
    ingreso = False
    return redirect("/")


@app.route('/registro', methods=["GET", "POST"])
def registro():
    return render_template('registro.html')


@app.route('/recuperar', methods=["GET", "POST"])
def recuperar():
    return render_template('recuperar.html')


@app.route('/habitaciones', methods=["GET", "POST"])
def habitaciones():
    # Crear un input para insertar numero de habitacion y validar
    return render_template('habitaciones.html')



@app.route('/habitacion/<id_habitacion>', methods=["GET"])
def habitacionVista(id_habitacion):
    return f"La habitacion /habitacion{id_habitacion}.html"



@app.route('/reserva', methods=["GET", "POST"])
def reserva():
    return render_template('reserva.html')


@app.route('/pago', methods=["GET", "POST"])
def pago():
    return render_template('pago.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
