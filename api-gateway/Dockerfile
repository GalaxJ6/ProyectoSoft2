# Usamos una imagen de PHP con Apache sobre Debian Bookworm
FROM php:8.4-apache-bookworm

# Instalamos dependencias del sistema y extensiones de PHP para MySQL
RUN rm -rf /var/lib/apt/lists/* \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        dpkg-dev \
        libpng-dev \
        zip \
        unzip \
        git \
    && docker-php-ext-install pdo_mysql \
    && rm -rf /var/lib/apt/lists/*

# Instalamos Composer de forma global
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer

# Establecemos el directorio de trabajo
WORKDIR /var/www/html

# Copiamos los archivos del proyecto
COPY . .

# Instalamos las dependencias de Laravel (ignorando scripts para evitar errores de entorno)
RUN composer install --no-interaction --optimize-autoloader --no-scripts

# Ajustamos los permisos para el servidor web
RUN chown -R www-data:www-data storage bootstrap/cache

# Exponemos el puerto de Laravel
EXPOSE 8000

# Comando para iniciar el servidor de desarrollo
CMD ["php", "artisan", "serve", "--host=0.0.0.0", "--port=8000"]