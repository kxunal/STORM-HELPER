FROM python:3.9-slim
WORKDIR /app/
COPY . /app/
RUN apt-get update -y && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install --no-cache-dir --upgrade --requirement requirements.txt
RUN chmod +x start.sh
CMD ["bash", "start.sh"]
