FROM python:3.12.4
WORKDIR /usr/src/app

# Step 1: copy only requirements first
COPY requirements.txt .
RUN pip install -r requirements.txt

# Step 2: copy the rest of your code
COPY . .

CMD ["python", "-u", "home/MawileBot/BeatlesBoy.py"]
