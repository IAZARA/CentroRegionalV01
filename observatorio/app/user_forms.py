from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.user import User, UserRoles

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

class RegistrationForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=64)])
    apellido = StringField('Apellido', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    telefono = StringField('Teléfono', validators=[DataRequired(), Length(min=8, max=20)])
    dependencia = StringField('Dependencia/Dirección', validators=[DataRequired(), Length(min=2, max=120)])
    role = SelectField('Rol', choices=UserRoles.get_roles(), validators=[DataRequired()])
    submit = SubmitField('Registrar')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Este email ya está registrado.')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Contraseña Actual', validators=[DataRequired()])
    new_password = PasswordField('Nueva Contraseña', validators=[
        DataRequired(),
        Length(min=8, message='La contraseña debe tener al menos 8 caracteres'),
        EqualTo('confirm_password', message='Las contraseñas deben coincidir')
    ])
    confirm_password = PasswordField('Confirmar Nueva Contraseña', validators=[DataRequired()])
    submit = SubmitField('Cambiar Contraseña')

class AdminCreateUserForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=64)])
    apellido = StringField('Apellido', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    telefono = StringField('Teléfono', validators=[DataRequired(), Length(min=8, max=20)])
    dependencia = StringField('Dependencia/Dirección', validators=[DataRequired(), Length(min=2, max=120)])
    role = SelectField('Rol', choices=UserRoles.get_roles(), validators=[DataRequired()])
    password = PasswordField('Contraseña Temporal', validators=[
        DataRequired(),
        Length(min=8, message='La contraseña debe tener al menos 8 caracteres')
    ])
    submit = SubmitField('Crear Usuario')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Este email ya está registrado.')
