FROM python:3-slim-buster
WORKDIR /app
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
CMD ["python", "app.py"]

# # for prod
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]