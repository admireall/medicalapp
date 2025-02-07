# Use an official Python image
FROM python:3.9

# Set environment variables to prevent Python from writing bytecode
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy only requirements.txt first (Better caching)
COPY requirements.txt /app/

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copy the entire project AFTER installing dependencies (Efficient caching)
COPY . /app/

# Create a non-root user for security
RUN useradd -m myuser && chown -R myuser /app
USER myuser

# Expose the port Django runs on
EXPOSE 8000

# Run migrations and start the Django app with Gunicorn
CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:8000 internship.wsgi:application"]
