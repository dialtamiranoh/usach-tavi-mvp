# ARCO-backend

Backend del proyecto ARCO (Asistente para el Registro Civil y su Orientacion).

## Como ejecutar este backend en otro computador

### 1. Clonar el repositorio

git clone <URL_DEL_REPO>
cd ARCO-backend

### 2. Crear el entorno virtual

python3 -m venv .venv

### 3. Activar el entorno virtual

source .venv/bin/activate

Si salio bien, deberia aparecer (.venv) al inicio de la terminal.

### 4. Instalar las dependencias del proyecto

pip install -r requirements.txt

### 5. Instalar el servidor de llama-cpp-python

pip install "llama-cpp-python[server]"

### 6. Tener un modelo local .gguf

Cada integrante debe tener un modelo .gguf guardado en su computador.

Ejemplo de ruta:
/home/USUARIO/models/qwen25-3b/Qwen2.5-3B-Instruct-Q4_K_M.gguf

La ruta cambia segun el computador de cada integrante.

### 7. Levantar el modelo local

Abrir una terminal nueva dentro de la carpeta del proyecto y ejecutar:

cd ~/ARCO-backend
source .venv/bin/activate
python -m llama_cpp.server --model "/RUTA/AL/MODELO.gguf" --host 127.0.0.1 --port 8001 --model_alias arco-llm --n_ctx 2048

Ejemplo:

python -m llama_cpp.server --model "/home/USUARIO/models/qwen25-3b/Qwen2.5-3B-Instruct-Q4_K_M.gguf" --host 127.0.0.1 --port 8001 --model_alias arco-llm --n_ctx 2048

Esta terminal debe quedar abierta mientras el modelo este corriendo.

### 8. Levantar el backend

Abrir otra terminal nueva dentro de la carpeta del proyecto y ejecutar:

cd ~/ARCO-backend
source .venv/bin/activate
uvicorn main:app --reload

Si todo salio bien, el backend quedara disponible en:
http://127.0.0.1:8000

### 9. Probar ARCO

Abrir en el navegador:
http://127.0.0.1:8000/docs

Ahi se puede probar el endpoint POST /ask.

### 10. Ejemplos de consultas

{"query": "quiero renovar mi carnet de identidad"}

{"query": "quiero transferir un vehiculo"}

{"query": "necesito sacar pasaporte"}

{"query": "quiero renovar licencia de conducir"}

## Si algo falla

Si Python no funciona:
python3 --version

Si el entorno virtual no esta activo:
source .venv/bin/activate

Si el modelo no responde:
verificar que la terminal del modelo siga abierta

Si la ruta del modelo esta mala:
find ~/models -type f -iname "*.gguf" 2>/dev/null

## Archivos principales

main.py: backend FastAPI
knowledge.json: base de conocimiento con tramites
requirements.txt: dependencias del proyecto
.gitignore: archivos ignorados por Git

## Notas

.venv no se sube al repositorio
los modelos .gguf no se suben al repositorio
cada integrante puede usar una ruta distinta para su modelo
