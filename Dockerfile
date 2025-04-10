##### STAGE 1: Build #####
# Use official Python image as base
FROM public.ecr.aws/lambda/python:3.12 AS builder
# Set working directory
WORKDIR /

COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir sentence-transformers
RUN pip install --no-cache-dir --only-binary=:all: -r requirements.txt

# Set cache path
ENV SPACY_DATA_DIR=/cache/spacy \
    HF_HOME=/cache/sbert
RUN python -m spacy download en_core_web_sm
RUN python -c "\
from sentence_transformers import SentenceTransformer;\
SentenceTransformer('all-MiniLM-L6-v2')"
RUN python -c "\
from sentence_transformers import SentenceTransformer;\
model = SentenceTransformer('all-MiniLM-L6-v2');\
model.save('/models/sbert')"
# Clear cache
RUN rm -rf /cache

##### STAGE 2: Package #####
FROM public.ecr.aws/lambda/python:3.12
WORKDIR /var/task

# Copy python libraries
COPY --from=builder /var/lang/lib/python3.12 /var/lang/lib/python3.12
# Copy downloaded model
COPY --from=builder /models /models
# Copy source code
COPY . .

# Set entry point
CMD ["lambda_func.lambda_handler"]