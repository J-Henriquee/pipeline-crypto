# base Docker image that we will build on
FROM python:3.13-slim

# set up the working directory inside the container
WORKDIR /app

# copy the requirements and src to the container
COPY requirements.txt .
COPY src/ src

# set up our image by installing requirements;
RUN pip install -r requirements.txt

# define what to do first when the container runs
ENTRYPOINT ["python", "src/extract_data.py"]