# Geospatial API Service

## Overview

A modular FastAPI backend for geospatial vector and raster operations, supporting KML, Shapefile, and GeoTIFF. Async heavy jobs via Celery + Redis. Logging with rotation. Dockerized for dev/prod.

## Features

- Vector/raster conversion, grid, buffer, DEM, slope, union, intersection, etc.
- File uploads in-memory only
- Always reprojects to EPSG:4326
- Returns GeoJSON (vector) or chosen raster format
- MODE=DEV for detailed errors
- Async jobs for heavy ops (DEM, slope, etc.)
- Logging: 10 days rotation

## Dev Setup (Windows, Docker Desktop)

```sh
docker-compose up --build
```

- Access API: http://localhost:8000/docs
- Logs: backend/app/logs/app.log

## Production Setup (Ubuntu)

- Clone repo
- `docker-compose up -d --build`
- Expose only backend/redis in Docker network
- (Later) Add nginx + certbot for HTTPS
- API should only be reachable via frontend/nginx in prod

## Folder Structure

```
backend/
  app/
    main.py
    routers/
    services/
    workers/
    core/
  requirements.txt
  Dockerfile
  docker-compose.yml
```

## Notes

- No HTTPS in dev
- All routes accept MODE=DEV for debug errors
- Heavy jobs run async (Celery)
- Lightweight jobs run inline
