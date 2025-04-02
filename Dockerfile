FROM python:3.11

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

EXPOSE 3001

# Set environment variables
ENV FLASK_APP=/app/flask/app.py
ENV FLASK_ENV=production

# Initialize database migrations if the migrations directory does not exist
RUN flask db init || echo "Migrations directory already exists"

# Create initial migration and apply it
# RUN flask db migrate -m "Initial migration" || echo "No changes to apply"
RUN flask db migrate -m "Initial migration" && flask db upgrade || echo "Migration failed or no changes to apply"

CMD ["python3", "-u", "flask/app.py"]
