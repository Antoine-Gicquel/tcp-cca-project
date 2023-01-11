from flask import Flask

print("Hello Server")


app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World! I am the server and I am serving you this string</p>"


if __name__ == '__main__':
    app.run(host='0.0.0.0')