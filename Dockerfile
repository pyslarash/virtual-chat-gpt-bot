# Use the official Python image as the base image
FROM python:3.8-slim

# Install pipenv
RUN pip install pipenv

# Create a non-root user with limited permissions
RUN groupadd -r bot_group && useradd --no-log-init -r -g bot_group bot_user

# Set the working directory inside the container
WORKDIR /app

# Copy the Pipfile and Pipfile.lock to the container
COPY Pipfile* ./

# Install dependencies using pipenv
RUN pipenv install --system --deploy --ignore-pipfile

# Copy the rest of the files to the container's working directory
COPY . .

# Change ownership of the working directory to the non-root user
RUN chown -R bot_user:bot_group /app

# Switch to the non-root user
USER bot_user

# Run the Python script (app.py) inside the container
CMD ["python", "app.py"]
