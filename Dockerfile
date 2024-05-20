FROM python:3.10
# Install deployment dependencies
RUN pip3 install --no-cache-dir uwsgi psycopg2

# Install sources
WORKDIR /usr/src/app
COPY . .

# Install Tesseract
RUN sudo add-apt-repository ppa:alex-p/tesseract-ocr5
RUN sudo apt update
RUN sudo apt install tesseract-ocr

# Install application dependencies from pypi to get latests versions
RUN pip3 install -r requirements.txt

CMD ["python", "main.py"]
EXPOSE 80/tcp
