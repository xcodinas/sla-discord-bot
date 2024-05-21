FROM python:3.10

# Install deployment dependencies
RUN pip3 install --no-cache-dir uwsgi psycopg2

# Install sources
WORKDIR /usr/src/app
COPY . .

# Install Tesseract
RUN apt-get update -y && \
    apt-get install -y software-properties-common libgl1-mesa-glx && \
    add-apt-repository ppa:alex-p/tesseract-ocr5 || (apt-get install -y tesseract-ocr && echo "Fallback to default repository")

# Install application dependencies from pypi to get latest versions
RUN pip3 install -r requirements.txt

COPY healthcheck.py .

# Run both the bot and the health check server
CMD ["sh", "-c", "python healthcheck.py & python main.py"]
EXPOSE 8000
