from flask import Flask

app = Flask(__name__)

@app.route('/forward')
def forward():
    print("jedziemy do przodu")
    #implementacja
    return ""

@app.route('/left')
def left():
    print("skrecamy w lewo")
    #implementacja
    return ""

@app.route('/right')
def right():
    print("skrecamy w prawo")
    #implementacja
    return ""

@app.route('/backward')
def backward():
    print("jedziemy do tylu")
    #implementacja
    return ""

@app.route('/camera')
def camera():
    print("robimy zdjecia")
    #implementacja
    return ""

@app.route('/photos')
def photos():
    print("zdjecia")
    #implementacja
    return "tu sa zdjecia"

if __name__ == '__main__':
    app.run(host='0.0.0.0')