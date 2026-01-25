FROM python:3.13.9
WORKDIR /usr/src/app
COPY home/MawileBot .
RUN pip install -r requirements.txt 
CMD ["python", "BeatlesBoy.py"]
