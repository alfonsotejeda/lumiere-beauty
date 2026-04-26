FROM b2b-backend-worker:latest
WORKDIR /app
# All required packages are pre-installed in base image (fastapi, uvicorn, motor, pymongo, redis, pydantic, python-dotenv, httpx, pytest, pytest-asyncio)
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
