from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User, GuestUser, UserRoles
from app.forms.auth import LoginForm, ChangePasswordForm
from app import db
from datetime import datetime
from app.auth import bp

@bp.route('/guest-login')
def guest_login():
    if current_user.is_authenticated:
        logout_user()
    guest = GuestUser()
    login_user(guest)
    flash('Has ingresado como invitado', 'info')
    return redirect(url_for('main.home'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Verificar si es un usuario normal (no invitado)
    is_normal_user = current_user.is_authenticated and hasattr(current_user, 'id') and getattr(current_user, 'id') != -1
    
    if is_normal_user:
        return redirect(url_for('main.home'))
    
    # Si es usuario invitado, cerramos sesión para mostrar el login
    if current_user.is_authenticated:
        logout_user()
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.home')
            return redirect(next_page)
        flash('Email o contraseña incorrectos', 'danger')
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Tu contraseña ha sido actualizada', 'success')
            return redirect(url_for('main.feed'))
        else:
            flash('La contraseña actual es incorrecta', 'danger')
    return render_template('auth/change_password.html', form=form)
