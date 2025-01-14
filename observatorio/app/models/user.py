from flask_login import UserMixin
from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class UserRoles:
    ADMIN = 'administrador'
    ANALISTA = 'analista'
    OPERADOR = 'operador'
    CONSULTOR = 'consultor'
    
    @staticmethod
    def get_roles():
        return [
            (UserRoles.ADMIN, 'Administrador'),
            (UserRoles.ANALISTA, 'Analista'),
            (UserRoles.OPERADOR, 'Operador'),
            (UserRoles.CONSULTOR, 'Consultor')
        ]

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    nombre = db.Column(db.String(64), nullable=False)
    apellido = db.Column(db.String(64), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    dependencia = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False, default=UserRoles.CONSULTOR)
    is_active = db.Column(db.Boolean, default=True)
    first_login = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

    @property
    def full_name(self):
        return f"{self.nombre} {self.apellido}"

    def has_role(self, role):
        return self.role == role

    @property
    def is_admin(self):
        return self.role == UserRoles.ADMIN

    @property
    def is_analista(self):
        return self.role == UserRoles.ANALISTA

    @property
    def is_operador(self):
        return self.role == UserRoles.OPERADOR

    @property
    def is_consultor(self):
        return self.role == UserRoles.CONSULTOR

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
