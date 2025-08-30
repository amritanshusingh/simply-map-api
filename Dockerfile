FROM ghcr.io/osgeo/gdal:ubuntu-full-latest
ENV PYTHONUNBUFFERED=1
WORKDIR /app


# Install pip and Python dependencies
RUN apt-get update && apt-get install -y python3-pip && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Copy app code
COPY . .

EXPOSE 8000
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "4"]
