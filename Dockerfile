# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.9

WORKDIR /code
ENV FLASK_APP=app.py
ENV FLASKRUN_HOST=0.0.0.0


RUN python -m pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install xlrd
RUN pip install numpy
RUN pip install pandas
RUN pip install sklearn
RUN pip install request
RUN pip install --upgrade tensorflow
RUN pip install transformers

EXPOSE 5000

COPY . .
CMD ["flask", "run"]