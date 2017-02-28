from flask import Flask
import os
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
    os.system("raspistill -n -t 1 -o static/test.jpg") #wywołujemy raspistill który wykonuje zdjęcie po sekundzie
    print("zrobiono zdjecie")
    return "zz" # zdjecie zrobione

@app.route('/photos')
def photos():
    print("zdjecia")
    #zdjęcia dostępne pod /static/test.jpg
    #implementacja
    return ""

if __name__ == '__main__':
    app.run(host='0.0.0.0')