from flask_wtf import FlaskForm
from wtforms import DecimalField, SubmitField, SelectField, IntegerField, StringField, PasswordField
from wtforms.validators import DataRequired, NumberRange, Length

class CostoProduccionForm(FlaskForm):
    materia_prima = DecimalField("Materia Prima Directa (Costo de los materiales que se utilizan directamente en la fabricación de un producto y que pueden identificarse fácilmente en el producto terminado)", validators=[DataRequired(), NumberRange(min=0)])
    mano_obra = DecimalField("Mano de Obra Directa (Costo del trabajo humano que se puede asignar a  laproducción del producto)", validators=[DataRequired(), NumberRange(min=0)])
    costos_indirectos = DecimalField("Costos Indirectos de Fabricación  (Gastos necesarios para el funcionamiento de la empresa)", validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField("Guardar")


class CostoUnitarioForm(FlaskForm):
    id_produccion = SelectField("Producción (ID)", choices=[], validators=[DataRequired()])
    cantidad_productos = IntegerField("Cantidad de Productos", validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField("Guardar")


class EditarCostoProduccionForm(FlaskForm):
    materia_prima_directa = DecimalField("Materia Prima Directa (Costo de los materiales que se utilizan directamente en la fabricación de un producto y que pueden identificarse fácilmente en el producto terminado)", validators=[DataRequired(), NumberRange(min=0)])
    mano_obra_directa = DecimalField("Mano de Obra Directa: Costo del trabajo humano que se puede asignar a  laproducción del producto", validators=[DataRequired(), NumberRange(min=0)])
    costos_indirectos_fabricacion = DecimalField("Costos Indirectos de Fabricación (Gastos necesarios para el funcionamiento de la empresa", validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField("Actualizar")

class EditarCostoUnitarioForm(FlaskForm):
    id_produccion = SelectField("Producción",coerce=int, validators=[DataRequired()])
    cantidad_productos = IntegerField("Cantidad de Productos", validators=[DataRequired(), NumberRange(min=1)],)
    submit = SubmitField("Actualizar")

class LoginForm(FlaskForm):
    usuario = StringField('Usuario (Maximo 20 Caracteres)', id='usuario', validators=[DataRequired()])
    contraseña = PasswordField('Contraseña (Maximo 15 Caracteres)', id='contraseña', validators=[DataRequired()])
    submit = SubmitField('Ingresar')

class VacioForm(FlaskForm):
    """Formulario para CSRF en acciones DELETE"""
    pass