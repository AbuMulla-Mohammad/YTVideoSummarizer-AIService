FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY [pyproject.toml](http://_vscodecontentref_/0) /app/pyproject.toml
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    cohere==5.16.1 \
    dotenv==0.9.9 \
    fastapi==0.116.0 \
    pydantic==2.11.7 \
    pytube==15.0.0 \
    requests==2.32.4 \
    uvicorn==0.35.0 \
    youtube-transcript-api==1.1.1


COPY app /app/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]