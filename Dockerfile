FROM Python:3.11.0
WORKDIR .
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY .* .
EXPOSE 8080
CMD ["uvicorn", "src.server.app:fastapi_app", "--host", "0.0.0.0", "--port", "8080"]
