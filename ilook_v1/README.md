# 🧰 Instalación de ambiente de desarrollo / integración / calidad / producción

Este documento describe los pasos necesarios para instalar y ejecutar el proyecto **iLook_v1** en una máquina de desarrollo nueva. Incluye la configuración de PostgreSQL, Python, entorno virtual y dependencias de Django.

## 📦 Requisitos previos

- **Git**
- **Python 3.13+**
- **pip** y **venv**
- **PostgreSQL 13+**

## Instalación paso a paso 

### 🗄️ Base de datos

1. **Instalar PostgreSQL**
   1. Descargar desde [https://www.postgresql.org/download/](https://www.postgresql.org/download/)
   2. Seguir procedimiento de instalación
   3. Aplicar seguridad y configuración de acceso si es una máquina remota

2. **Instalar cliente pgAdmin**
   1. Descargar desde [https://www.pgadmin.org/download/](https://www.pgadmin.org/download/)
   2. Instalar en el PC de pruebas
   3. Configurar la conexión a PostgreSQL

3. **Restaurar respaldo de base de datos**

---

### 🐍 Python

1. Descargar desde [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Instalar la versión **3.13**
3. Seguir las indicaciones de la página de instalación

---

## 💻 Proyecto iLook

1. **Instalar proyecto**
   1. Crear una carpeta `/dev/` como repositorio local en el PC
   2. Instalar GIT desde [https://git-scm.com/downloads](https://git-scm.com/downloads)
   3. Descargar o clonar el repositorio:
      ```bash
      cd /dev/
      git clone https://github.com/marcos-molero/djangodev.git
      ```

2. **Crear entorno virtual en la carpeta `/dev/`**
   ```bash
   cd /dev/
   python -m venv venv_v1
   ```

3. **Activar el entorno virtual**
  - En Windows CMD:
    ```bash
    .\venv_v1\Scripts\activate
    ```
  - En Windows PowerShell:
    ```bash
    .\venv_v1\Scripts\Activate.ps1
    ```

4. **Entrar en la carpeta del proyecto**
    ```bash
    cd .\djangodev\ilook_v1\
    ```

5. **Instalar paquetes de dependencias del proyecto**
    ```bash
    pip install -r requirements.txt
    ```

6. **Verificar que el archivo .env esté presente**
  - No modificar el contenido del archivo

  En caso de no tener el archivo configurarlo de la siguiente manera:
    DEBUG=True
    SECRET_KEY=               {tu clave aqui}
    DB_NAME=ilook_db          {nombre de la base de datos}
    DB_USER=ilook_dev         {usuario de conexión}
    DB_PASSWORD=12345678      {contraseña}
    DB_HOST=172.20.57.124     {o la ip de tu servidor de Postgresql}
    DB_PORT=5432              {o el puerto}
    REDIS_URL=redis://localhost:6379/0
    ALLOWED_HOSTS=localhost,django.local,ilook.com

7. **Aplicar migraciones a la base de datos**
    ```bash
    python manage.py migrate
    ```

8. **Crear superusuario para el panel de administración**
    ```bash
    python manage.py createsuperuser
    ```

9. **Ejecutar servidor para pruebas internas**
    ```bash
    python manage.py runserver
    ```
