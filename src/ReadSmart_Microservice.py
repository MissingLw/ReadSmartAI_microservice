# ReadSmart_Microservice.py
from flask import Flask
from generator.question_generator import question_generator
from grader.response_grader import response_grader


app = Flask(__name__)

app.register_blueprint(question_generator, url_prefix='/question_generator')
app.register_blueprint(response_grader, url_prefix='/response_grader')

if __name__ == "__main__":
    app.run(port=5000)
