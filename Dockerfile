# Use a base Python image
FROM python:3.13

# Set environment variables for unbuffered Python output
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /app/myproject

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Django project into the container
COPY . .

RUN python manage.py collectstatic --noinput

# Expose the port Django will run on (default 8000)
EXPOSE 8000

# Define the command to run the Django development server
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]
