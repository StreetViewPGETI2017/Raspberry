from flask import Flask
import os
from usb import usb
app = Flask(__name__)
arduino_connect = usb

@app.route('/forward')
def forward(): # przesyla polecenie jazdy do przodu (f) i dystans (w metrach), nastepnie czeka na odpowiedz
    print("jedziemy do przodu")

    # implementacja
    distance = "10" # tymczasowo dystans jest staly i ignowrowany
    orders = ["f", distance]
    arduino_connect.send(orders)
    status = arduino_connect.receive()
    print(status) # status nie jest sprawdzany, zatem sie go tylko wypisuje
    # if status != distance:
       #  print("Error")
    # else:
        # print("Ok")
    return ""

@app.route('/left')
def left(): # przesyla polecenie skretu w lewo (l) i kat (w stopniach), nastepnie czeka na odpowiedz
    print("skrecamy w lewo")
	
    #implementacja
    angle = "90" # tymczasowo kat jest staly i ignowrowany
    orders = ["l", angle]
    arduino_connect.send(orders)
    status = arduino_connect.receive()
    print(status) # status nie jest sprawdzany, zatem sie go tylko wypisuje 
	
    return ""

@app.route('/right')
def right(): # przesyla polecenie skretu w lewo (l) i kat (w stopniach), nastepnie czeka na odpowiedz
    print("skrecamy w prawo")
    angle = "90" # tymczasowo kat jest staly i ignowrowany
    orders = ["r", angle]
    arduino_connect.angle(orders)
    status = arduino_connect.receive()
    print(status) # status nie jest sprawdzany, zatem sie go tylko wypisuje
    return ""

@app.route('/backward')
def backward(): # przesyla polecenie jazdy do tylu (b) i dystans (w metrach), nastepnie czeka na odpowiedz
    print("jedziemy do tylu")

    # implementacja
    distance = "10" # tymczasowo dystans jest staly i ignowrowany
    orders = ["b", distance]
    arduino_connect.send(orders)
    status = arduino_connect.receive()
    print(status) # status nie jest sprawdzany, zatem sie go tylko wypisuje
    return ""

@app.route('/camera')
def camera():
    print("robimy zdjecia")
    os.system("raspistill -n -t 1 -o static/test.jpg") #wywołujemy raspistill który wykonuje zdjęcie po sekundzie
    print("zrobiono zdjecie")
    return "zz" # zdjecie zrobione

@app.route('/photos')
def photos():
    print("zdjecia <\br>")
    print('<a href="static/test.jpg"> Tu </a>')
    #zdjęcia dostępne pod /static/test.jpg
    #implementacja
    return ""

if __name__ == '__main__':
    # arduino_connect.open()
    app.run(host='0.0.0.0')

