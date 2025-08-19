# Crear entorno virtual
python -m venv venv --> crear entorno virtual

## En Linux/macOS:

source venv/bin/activate

## En Windows:

venv\Scripts\activate

# Instalar dependencias

pip install -r requirements.txt

# En caso de instalar nuevas dependencias
pip freeze > requirements.txt --> generar el reqs.txt de nuevo (en caso de instalar nuevas dependencias)

# Ejecutar el servidor de desarrollo

uvicorn app.main:app --reload

# Abrir otra terminal para el front-end manteniendo la del back-end activa

# Dirigirse al front-end

cd front-end

# Instalar las dependencias

npm install

# Ejecutar el servidor de desarrollo

npm start

