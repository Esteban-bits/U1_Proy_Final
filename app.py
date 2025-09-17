from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf.csrf import CSRFProtect
import pymysql
from controllers.controlador import (
    insertar_costo_produccion, insertar_costo_unitario,
    obtener_costo_produccion_por_id, obtener_costos_produccion,
    obtener_costo_unitario_por_id, obtener_costos_unitarios,
    actualizar_costo_produccion, actualizar_costo_unitario,
    eliminar_costo_produccion, eliminar_costo_unitario, obtener_costos_unitarios_con_info
)
from forms import CostoProduccionForm, CostoUnitarioForm, EditarCostoProduccionForm, EditarCostoUnitarioForm, LoginForm, VacioForm

from conexion import obtener_conexion

from models.user import db, Usuario

app = Flask(__name__)
app.secret_key = "U1Final"  
app.config['WTF_CSRF_SECRET_KEY'] = "root123"  

csrf = CSRFProtect(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:3306/usuarios'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET'])
def inicio():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    costos_produccion = obtener_costos_produccion()
    costos_unitarios = obtener_costos_unitarios_con_info()  

    form_csrf = VacioForm()

    return render_template(
        "inicio.html",
        usuario=session['usuario'],
        costos_produccion=costos_produccion,
        costos_unitarios=costos_unitarios,
        form_csrf=form_csrf   
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        usuario = form.usuario.data
        contraseña = form.contraseña.data

        usuario_db = Usuario.query.filter_by(usuario=usuario, contraseña=contraseña).first()

        if usuario_db:
            session['usuario'] = usuario_db.usuario
            flash(f'Bienvenido {usuario_db.usuario}', 'success')
            return redirect(url_for('inicio'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')

    return render_template('loginPurificadora.html', form=form)

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('login'))


@app.route("/agregar_costoproduccion", methods=["GET", "POST"])
def agregar_costoproduccion():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    form = CostoProduccionForm()
    if form.validate_on_submit():
        insertar_costo_produccion(form.materia_prima.data, form.mano_obra.data, form.costos_indirectos.data)
        flash("Costo de producción guardado con éxito", "success")
        return redirect(url_for("inicio"))

    return render_template("agregarCostProd.html", form=form)


@app.route("/editar_costoproduccion/<int:id>", methods=["GET", "POST"])
def editar_costoproduccion(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = obtener_conexion()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, materia_prima_directa, mano_obra_directa, costos_indirectos_fabricacion
        FROM costoProduccion WHERE id = %s
    """, (id,))
    produccion = cursor.fetchone()

    if not produccion:
        flash("El costo de producción no existe.", "danger")
        cursor.close()
        conn.close()
        return redirect(url_for("inicio"))

    form = EditarCostoProduccionForm()

    if request.method == "GET":
        form.materia_prima_directa.data = produccion[1]
        form.mano_obra_directa.data = produccion[2]
        form.costos_indirectos_fabricacion.data = produccion[3]

    if form.validate_on_submit():
        cursor.execute("""
            UPDATE costoProduccion
            SET materia_prima_directa = %s,
                mano_obra_directa = %s,
                costos_indirectos_fabricacion = %s
            WHERE id = %s
        """, (form.materia_prima_directa.data, form.mano_obra_directa.data, form.costos_indirectos_fabricacion.data, id))

        cursor.execute("""
            UPDATE costoUnitario cu
            JOIN costoProduccion cp ON cu.costo_produccion_id = cp.id
            SET cu.costo_total_snapshot = cp.costo_total,
                cu.costo_unitario = cp.costo_total / cu.cantidad_productos
            WHERE cp.id = %s
        """, (id,))

        conn.commit()
        cursor.close()
        conn.close()
        flash("Costo de producción y costos unitarios actualizados correctamente.", "success")
        return redirect(url_for("inicio"))

    cursor.close()
    conn.close()
    return render_template("editarCostProd.html", form=form, id=id)


@app.route("/eliminar_costoproduccion", methods=["POST"])
def eliminar_costoproduccion():
    form = VacioForm()
    if not form.validate_on_submit():
        flash("Acción no permitida. CSRF inválido.", "danger")
        return redirect(url_for("inicio"))

    id = int(request.form["id"])
    eliminar_costo_produccion(id)
    flash("Costo de producción eliminado.", "success")
    return redirect(url_for("inicio"))


@app.route("/agregar_costounitario", methods=["GET", "POST"])
def agregar_costounitario():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = obtener_conexion()
    cursor = conn.cursor()

    cursor.execute("SELECT id, costo_total FROM costoProduccion")
    producciones = cursor.fetchall()

    form = CostoUnitarioForm()
    form.id_produccion.choices = [(str(row[0]), f"ID {row[0]} - Total: {row[1]}") for row in producciones]

    if form.validate_on_submit():
        id_produccion = int(form.id_produccion.data)
        cantidad_productos = form.cantidad_productos.data

        cursor.execute("SELECT costo_total FROM costoProduccion WHERE id = %s", (id_produccion,))
        result = cursor.fetchone()
        if not result:
            flash("Producción no encontrada", "danger")
            return redirect(url_for("agregar_costounitario"))

        costo_total_snapshot = result[0]
        costo_unitario = costo_total_snapshot / cantidad_productos

        cursor.execute("""
            INSERT INTO costoUnitario (costo_produccion_id, cantidad_productos, costo_total_snapshot, costo_unitario, fecha_calculo)
            VALUES (%s, %s, %s, %s, NOW())
        """, (id_produccion, cantidad_productos, costo_total_snapshot, costo_unitario))

        conn.commit()
        cursor.close()
        conn.close()

        flash("Costo unitario guardado correctamente", "success")
        return redirect(url_for("inicio"))

    cursor.close()
    conn.close()
    return render_template("agregarCostUnit.html", form=form)


@app.route("/editar_costounitario/<int:id>", methods=["GET", "POST"])
def editar_costounitario(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = obtener_conexion()
    cursor = conn.cursor()

    cursor.execute("SELECT id, costo_produccion_id, cantidad_productos FROM costoUnitario WHERE id = %s", (id,))
    unitario = cursor.fetchone()

    if not unitario:
        flash("El costo unitario no existe.", "danger")
        cursor.close()
        conn.close()
        return redirect(url_for("inicio"))

    cursor.execute("SELECT id, costo_total FROM costoProduccion")
    producciones = cursor.fetchall()

    form = EditarCostoUnitarioForm()
    form.id_produccion.choices = [(row[0], f"ID {row[0]} - Total: {row[1]}") for row in producciones]

    if request.method == "GET":
        form.id_produccion.data = unitario[1]
        form.cantidad_productos.data = unitario[2]

    if form.validate_on_submit():
        id_produccion = form.id_produccion.data
        cantidad_productos = form.cantidad_productos.data

        cursor.execute("SELECT costo_total FROM costoProduccion WHERE id = %s", (id_produccion,))
        result = cursor.fetchone()
        if not result:
            flash("Producción no encontrada", "danger")
            cursor.close()
            conn.close()
            return redirect(url_for("editar_costounitario", id=id))

        costo_total_snapshot = result[0]
        costo_unitario = costo_total_snapshot / cantidad_productos

        cursor.execute("""
            UPDATE costoUnitario
            SET costo_produccion_id = %s,
                cantidad_productos = %s,
                costo_total_snapshot = %s,
                costo_unitario = %s
            WHERE id = %s
        """, (id_produccion, cantidad_productos, costo_total_snapshot, costo_unitario, id))

        conn.commit()
        cursor.close()
        conn.close()
        flash("Costo unitario actualizado correctamente.", "success")
        return redirect(url_for("inicio"))

    cursor.close()
    conn.close()
    return render_template("editarCostUnit.html", form=form, id=id)


@app.route("/eliminar_costounitario", methods=["POST"])
def eliminar_costounitario():
    form = VacioForm()
    if not form.validate_on_submit():
        flash("Acción no permitida. CSRF inválido.", "danger")
        return redirect(url_for("inicio"))

    id = int(request.form["id"])
    eliminar_costo_unitario(id)
    flash("Costo unitario eliminado.", "success")
    return redirect(url_for("inicio"))


if __name__ == "__main__":
    app.run(debug=True)