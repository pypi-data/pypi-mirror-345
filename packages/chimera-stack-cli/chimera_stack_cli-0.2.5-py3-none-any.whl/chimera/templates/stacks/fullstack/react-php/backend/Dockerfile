ARG PHP_VERSION=8.2

FROM php:${PHP_VERSION}-fpm

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    libpng-dev \
    libonig-dev \
    libxml2-dev \
    libpq-dev \
    zip \
    unzip

# Clear cache
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Install PHP extensions
RUN docker-php-ext-install pdo_mysql pdo_pgsql mbstring exif pcntl bcmath gd

# Get latest Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Set working directory
WORKDIR /var/www/html

# Copy existing application directory contents
COPY . .

# Install dependencies (if composer.json exists)
RUN if [ -f "composer.json" ]; then \
    composer install --no-interaction --no-dev --prefer-dist; \
    fi

# Change ownership of our applications
RUN mkdir -p /var/log/php \
    && touch /var/log/php/error.log \
    && mkdir -p /var/log/php-fpm \
    && touch /var/log/php-fpm/error.log \
    && chown -R www-data:www-data /var/www/html /var/log/php /var/log/php-fpm

# Start PHP-FPM
CMD ["php-fpm"]
