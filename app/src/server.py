from flask import Flask
import os
server = Flask(__name__)
port = int(os.environ.get("PORT", 5000))

@server.route("/")
def hello():
    return "Hello World, Little Dude!"

if __name__ == "__main__":
   server.run(host='0.0.0.0',port=port) 