from flask import Flask, request, render_template


app = Flask(__name__)

@app.route("/")
def home():
    return "Hello!"


@app.route("/predict")
def predict():
    inputs = [
        request.args["LIMIT_BAL"]
        
    ]
    #output = model.predict([inputs])[0]
    #return "Insolvente" if output else "Non insolvente"