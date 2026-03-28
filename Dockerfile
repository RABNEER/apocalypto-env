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
ENV PYTHONPATH=.
EXPOSE 7860

# Run the FastAPI server as a module to resolve relative imports
CMD ["python", "-m", "server.app"]
