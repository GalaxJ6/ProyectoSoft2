# Imagen ligera de Node.js
FROM node:18-alpine

WORKDIR /app

# Copiamos archivos de dependencias
COPY package*.json ./

# Instalamos las librerías de Node
RUN npm install

# Copiamos el código
COPY . .

# Puerto de Express
EXPOSE 3000

# Comando para iniciar el microservicio
CMD ["npm", "start"]