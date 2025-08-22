# Use slim Debian-based Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . .

# Render assigns a dynamic port via $PORT
ENV PORT=8080

# Expose the Render port (not strictly required, but good practice)
EXPOSE $PORT

# Run Flask app with gunicorn (better for production than plain python)
CMD ["gunicorn", "-b", "0.0.0.0:${PORT}", "app:app"]
