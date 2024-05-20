FROM python:3.8
# Install deployment dependencies
RUN pip3 install --no-cache-dir uwsgi psycopg2

# Install sources
WORKDIR /usr/src/app
COPY . .
# Install application dependencies from pypi to get latests versions
RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
