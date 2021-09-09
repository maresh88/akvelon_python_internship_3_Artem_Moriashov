FROM python:3.8-slim
ENV PYTHONUNBUFFERED=1
RUN python3 -m pip install --upgrade pip wheel
WORKDIR /app
COPY req.txt req.txt
RUN pip3 install -r req.txt
ENTRYPOINT ["/app/entrypoint.sh"]

