FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir \
    torch==2.8.0 \
    --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir sentence-transformers

COPY src ./src

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]