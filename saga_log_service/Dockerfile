# Usa una imagen oficial de Python como base
FROM python:3.9

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia los archivos de la aplicación al contenedor
COPY . .

# Instala las dependencias desde requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto del servicio
EXPOSE 5007

# Comando para ejecutar la aplicación Flask
CMD ["python", "app.py"]
