FROM python:latest

LABEL authors="Jeamfry"

WORKDIR /app
ENV OUTPUT_DIRECTORY="/output"
ENV DGRAPH_URL="localhost:39080"

# Init pipenv to install dependencies
COPY Pipfile Pipfile.lock /app/
RUN pip install pipenv && \
    apt-get update && \
    apt-get install -y --no-install-recommends g++ && \
    pipenv install --system --deploy && \
    curl https://get.dgraph.io -sSf | bash && \
    apt-get remove -y g++ && \
    apt-get autoremove -y && \
    pip uninstall pipenv -y

# Entrypoint and helpers
COPY entrypoint.sh .

# Files
COPY create_json_data.py /app/
COPY dbs/* /app/dbs/

ENV DGRAPH_ZERO_URL="localhost:5080"

ENV PYTHONPATH=/app:$PYTHONPATH
ENTRYPOINT ["/app/entrypoint.sh"]