##### STAGE 1: Build
# Use official Python image as base
FROM python:3.12-slim AS builder
# Set working directory
WORKDIR /

# Preinstall system packages (only what you *really* need)
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Create virtualenv and install into it
RUN python -m venv venv
COPY requirements.txt .

# Install dependencies
RUN ./venv/bin/pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN ./venv/bin/pip install --no-cache-dir sentence-transformers
RUN ./venv/bin/pip install --only-binary=:all: --no-cache-dir -r requirements.txt

# Set cache path
ENV SPACY_DATA_DIR=/cache/spacy \
    HF_HOME=/cache/sbert
RUN ./venv/bin/python -m spacy download en_core_web_sm
RUN ./venv/bin/python -c "\
from sentence_transformers import SentenceTransformer;\
SentenceTransformer('all-MiniLM-L6-v2')"
RUN ./venv/bin/python -c "\
from sentence_transformers import SentenceTransformer;\
model = SentenceTransformer('all-MiniLM-L6-v2');\
model.save('/models/sbert')"
# Clear cache
RUN rm -rf /cache

##### STAGE 2: Package
FROM python:3.12-slim
WORKDIR /app

# Minimal system libs just for runtime
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy prebuilt venv
COPY --from=builder ./venv ./venv
# Copy downloaded model
COPY --from=builder /models /models
# Copy source code
COPY . .

# Set entry point
CMD ["./venv/bin/python", "lambda_test.py"]