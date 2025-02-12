FROM python:3.11

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

<<<<<<< HEAD
COPY . .

EXPOSE 8000
#run python3 app.py

CMD ["python3", "test_query.py"]
=======
COPY . /app/

EXPOSE 8000

CMD ["python3", "llm_aravind_with_tool_calling.py"]
>>>>>>> 20034833eca244a3f9c64626d2e94289cf505d25
