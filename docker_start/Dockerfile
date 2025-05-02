##### STAGE 1: Build #####
# Use official Python image as base
FROM public.ecr.aws/lambda/python:3.12 AS builder
# Set working directory
WORKDIR /
# Copy packages
COPY requirements.txt .
# Install dependencies
RUN pip install --no-cache-dir --only-binary=:all: -r requirements.txt
# Clear cache
RUN rm -rf /cache

##### STAGE 2: Package #####
FROM public.ecr.aws/lambda/python:3.12
WORKDIR /var/task
# Copy python libraries
COPY --from=builder /var/lang/lib/python3.12 /var/lang/lib/python3.12
# Copy source code
COPY . .

# Set entry point
CMD ["lambda_func_start.lambda_handler"]