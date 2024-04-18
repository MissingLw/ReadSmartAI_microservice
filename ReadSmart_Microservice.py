# ReadSmart_Microservice.py
import os
from flask import Flask
from generator.question_generator import question_generator
from grader.response_grader import response_grader


app = Flask(__name__)

app.register_blueprint(question_generator, url_prefix='/question_generator')
app.register_blueprint(response_grader, url_prefix='/response_grader')

@app.route('/', methods=['GET'])
def home():
    return "ReadSmart Microservice is running!"

@app.route('/favicon.ico', methods=['GET'])
def favicon():
    return ""


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
