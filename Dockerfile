FROM python:3.13.9
WORKDIR /usr/src/app
COPY . .
RUN pip install -r requirements.txt 
CMD ["python", "home/MawileBot/BeatlesBoy.py"]
