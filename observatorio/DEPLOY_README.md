# Guía de Despliegue - Observatorio de Drogas Sintéticas

## Despliegue en Digital Ocean Droplet

### Requisitos Previos

1. **Droplet de Digital Ocean**
   - Ubuntu 20.04 LTS o superior
   - Mínimo 2GB RAM, 1 vCPU
   - Recomendado: 4GB RAM, 2 vCPU para mejor rendimiento

2. **Acceso SSH al servidor**
   - Clave SSH configurada
   - Acceso root o usuario con privilegios sudo

### Pasos de Instalación

#### 1. Conectar al Droplet

```bash
ssh root@tu_ip_del_droplet
```

#### 2. Subir el código al servidor

**Opción A: Usando Git (Recomendado)**
```bash
cd /var/www
git clone https://github.com/tu-usuario/observatorio.git
cd observatorio
```

**Opción B: Usando SCP**
```bash
# Desde tu máquina local
scp -r /ruta/local/observatorio root@tu_ip:/var/www/
```

#### 3. Ejecutar el script de despliegue

```bash
cd /var/www/observatorio
chmod +x deploy_digitalocean.sh
./deploy_digitalocean.sh
```

### Configuración Post-Instalación

#### 1. Configurar variables de entorno

Editar el archivo `/var/www/observatorio/.env`:

```bash
sudo -u observatorio nano /var/www/observatorio/.env
```

Actualizar las siguientes variables:

```env
SECRET_KEY=tu_clave_secreta_muy_segura_aqui_2025
DATABASE_URL=postgresql://observatorio_user:observatorio_password_2025@localhost/observatorio
REDIS_URL=redis://localhost:6379/0
FLASK_ENV=production
APIFY_API_TOKEN=tu_token_apify_aqui
```

#### 2. Verificar servicios

```bash
# Verificar estado de los servicios
sudo systemctl status observatorio
sudo systemctl status observatorio-celery
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis-server
```

#### 3. Ver logs en caso de problemas

```bash
# Logs de la aplicación
sudo journalctl -u observatorio -f

# Logs de Celery
sudo journalctl -u observatorio-celery -f

# Logs de Nginx
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Usuario Administrador

El script automáticamente crea un usuario administrador con las siguientes credenciales:

- **Email:** `ivan.zarate@minseg.gob.ar`
- **Contraseña:** `Minseg2025-`
- **Rol:** Administrador

### Configuración de Dominio (Opcional)

#### 1. Configurar DNS

En tu proveedor de DNS, crear un registro A que apunte a la IP de tu droplet:

```
tudominio.com -> IP_DEL_DROPLET
```

#### 2. Configurar SSL con Let's Encrypt

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obtener certificado SSL
sudo certbot --nginx -d tudominio.com

# Configurar renovación automática
sudo crontab -e
# Agregar la línea:
0 12 * * * /usr/bin/certbot renew --quiet
```

#### 3. Actualizar configuración de Nginx

```bash
sudo nano /etc/nginx/sites-available/observatorio
```

Cambiar `server_name _;` por `server_name tudominio.com;`

```bash
sudo systemctl reload nginx
```

### Comandos Útiles de Mantenimiento

#### Reiniciar servicios

```bash
# Reiniciar aplicación
sudo systemctl restart observatorio

# Reiniciar Celery
sudo systemctl restart observatorio-celery

# Reiniciar Nginx
sudo systemctl restart nginx
```

#### Actualizar la aplicación

```bash
cd /var/www/observatorio
sudo -u observatorio git pull
sudo -u observatorio bash -c "source venv/bin/activate && pip install -r requirements.txt"
sudo systemctl restart observatorio
sudo systemctl restart observatorio-celery
```

#### Backup de la base de datos

```bash
# Crear backup
sudo -u postgres pg_dump observatorio > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar backup
sudo -u postgres psql observatorio < backup_file.sql
```

### Solución de Problemas Comunes

#### 1. Error 502 Bad Gateway

```bash
# Verificar que Gunicorn esté corriendo
sudo systemctl status observatorio

# Verificar logs
sudo journalctl -u observatorio -n 50

# Reiniciar servicio
sudo systemctl restart observatorio
```

#### 2. Error de conexión a la base de datos

```bash
# Verificar PostgreSQL
sudo systemctl status postgresql

# Verificar conexión
sudo -u postgres psql -c "\l"

# Verificar usuario y permisos
sudo -u postgres psql -c "\du"
```

#### 3. Error de Redis/Celery

```bash
# Verificar Redis
sudo systemctl status redis-server
redis-cli ping

# Verificar Celery
sudo systemctl status observatorio-celery
sudo journalctl -u observatorio-celery -n 50
```

### Configuración de Desarrollo Local

Para desarrollo local, puedes usar el script simplificado:

```bash
# Crear usuario administrador localmente
python3 setup_admin.py

# Ejecutar aplicación
python3 run.py --port 5001
```

### Monitoreo y Logs

#### Configurar logrotate

```bash
sudo nano /etc/logrotate.d/observatorio
```

```
/var/www/observatorio/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 observatorio observatorio
    postrotate
        systemctl reload observatorio
    endscript
}
```

### Seguridad

#### 1. Configurar firewall

```bash
# El script ya configura UFW, pero puedes verificar:
sudo ufw status

# Permitir solo puertos necesarios
sudo ufw allow 22   # SSH
sudo ufw allow 80   # HTTP
sudo ufw allow 443  # HTTPS
```

#### 2. Configurar fail2ban

```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

#### 3. Actualizar contraseñas por defecto

- Cambiar contraseña de PostgreSQL
- Actualizar SECRET_KEY en .env
- Cambiar contraseña del usuario administrador desde la interfaz web

### Contacto y Soporte

Para problemas o consultas sobre el despliegue, contactar al equipo de desarrollo.

---

**Nota:** Este script está diseñado para un entorno de producción básico. Para entornos de alta disponibilidad, considerar configuraciones adicionales como load balancers, múltiples instancias, y monitoreo avanzado.