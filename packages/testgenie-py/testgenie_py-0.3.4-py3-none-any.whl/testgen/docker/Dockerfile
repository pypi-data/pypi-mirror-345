# Use Python 3.10 image
FROM python:3.10

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    graphviz \
    libgraphviz-dev \
    pkg-config \
    curl

# Install Poetry (optional, in case you ever need it)
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Set environment variables
ENV POETRY_VIRTUALENVS_CREATE=false \
    PYTHONUNBUFFERED=1 \
    RUNNING_IN_DOCKER=true

# Install your package from PyPI
RUN python3 -m pip install --no-cache-dir testgenie-py

# Set a working directory (where your code will be mounted at runtime)
WORKDIR /controller

# Set up PYTHONPATH
ENV PYTHONPATH=/controller:/controller/testgen

# Default command
CMD ["testgenie"]
