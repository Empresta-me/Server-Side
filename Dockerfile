# the Flask application container will use python:3.10-alpine as the base image
#FROM python:3.10-alpine
FROM python:3.7.2-stretch

# this command will create the working directory for our Python Flask application Docker image
WORKDIR /app

# this command will copy the dependencies and libraries in the requirements.txt to the working directory
COPY requirements.txt /app

# this command will install the dependencies in the requirements.txt to the Docker image
RUN pip install -r requirements.txt --no-cache-dir

# this command will copy the files and source code required to run the application
COPY . /app

# this command will start the Python Flask application Docker container
CMD python Community.py --pem testpassword
