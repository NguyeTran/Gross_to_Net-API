FROM python:3.12-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py calculator.py ./

EXPOSE 5000 

CMD ["python", "main.py"]