# Creo una API web, es decir, un prograrma que recibe y responde solicitudes HTTP
# uso fastAPI para crear las rutas o puertas de entrada por donde los usuarios piden o envian informacion
# endpoints: direccion especifica URL de la API que cumple una funcion

# GET: son para pedir informacion
# POST: son para enviar informacion

# creo los endpoints
    # a. GET / files: que devuelve una lista de los archivos disponibles en el directorio ./files
    # b. POST / crea un archivo con el nombre y contenido proporcionado en el cuerpo de la solicitud
    # c. GET /files{file_name} : que devuelve el contenido del archivo especificado por file_name

from fastapi import FastAPI
from pydantic import BaseModel
import os

app = FastAPI()

@app.get("/files")
async def get_files():
    # obtengo el nombre de los archivos en la carpeta ./files
    archivos = os.listdir("./files")
    return archivos


# Definino el modelo de datos que esperamos en el body
class FileData(BaseModel):
    name: str
    content: str

@app.post("/files")
async def post_files(file: FileData):
    with open(f"./files/{file.name}", "w") as f:
        f.write(file.content)
    return {"message": f"Archivo '{file.name}' creado con éxito"}
    
# c. GET /files{file_name} : que devuelve el contenido del archivo especificado por file_name
@app.get("/files/{file_name}")
async def get_file_content(file_name: str):
    try:
        with open(f"./files/{file_name}", "r") as file:
            contenido = file.read()
            return {"contenido": contenido}
    except FileNotFoundError:
        return {"error": "Archivo no encontrado"}
    

