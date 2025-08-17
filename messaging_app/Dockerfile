#Use official python image
FROM python:3.10

# Set work directory
WORKDIR /app

COPY requirements.txt .

#install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .
COPY manage.py .

#EXPOSE Django port
EXPOSE 8000

# Start Django app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]