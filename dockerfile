FROM python:3.14-slim

# Create app user in prod
#RUN groupadd -r app && useradd -r -g app app

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ai_blog_generator.py .

# local
EXPOSE 5000
CMD ["python", "ai_blog_generator.py"]

# prod
# Expose port 8000 (gunicorn)
#EXPOSE 8000

# Run as non-root
#USER app

# Use gunicorn with reasonable worker count and timeout
#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "ai_blog_generator:app"]