FROM python:3.10-slim

WORKDIR /app

# Install dependencies from root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project (including server/ and baseline.py)
COPY . .

# Set environment variables for HF Spaces
ENV PORT=7860
ENV HOST=0.0.0.0
EXPOSE 7860

# Run the FastAPI server natively
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
