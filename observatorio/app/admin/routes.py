from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.admin import admin
from app.models.user import User
from app.user_forms import AdminCreateUserForm

def admin_required(f):
    """Decorador para requerir rol de ADMIN"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'administrador':
            flash('Acceso denegado. Se requieren permisos de administrador.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/users')
@login_required
@admin_required
def manage_users():
    """Página principal de gestión de usuarios"""
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('admin/manage_users.html', users=users)

@admin.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    """Crear nuevo usuario"""
    form = AdminCreateUserForm()
    
    if form.validate_on_submit():
        try:
            # Crear nuevo usuario
            user = User(
                nombre=form.nombre.data,
                apellido=form.apellido.data,
                email=form.email.data.lower(),
                telefono=form.telefono.data,
                dependencia=form.dependencia.data,
                role=form.role.data
            )
            
            # Establecer contraseña temporal
            user.set_password(form.password.data)
            
            # Marcar que debe cambiar contraseña en primer login
            user.first_login = True
            user.is_active = True
            
            # Guardar en base de datos
            db.session.add(user)
            db.session.commit()
            
            return redirect(url_for('admin.manage_users'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error al crear el usuario. Por favor, intente nuevamente.', 'error')
    
    return render_template('admin/create_user.html', form=form)

@admin.route('/users/<int:user_id>/toggle-status')
@login_required
@admin_required
def toggle_user_status(user_id):
    """Activar/desactivar usuario"""
    user = User.query.get_or_404(user_id)
    
    # No permitir desactivar al propio usuario admin
    if user.id == current_user.id:
        flash('No puedes desactivar tu propia cuenta.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    try:
        user.is_active = not user.is_active
        db.session.commit()
        
        status = 'activado' if user.is_active else 'desactivado'
        flash(f'Usuario {user.nombre} {user.apellido} {status} exitosamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error al cambiar el estado del usuario.', 'error')
    
    return redirect(url_for('admin.manage_users'))