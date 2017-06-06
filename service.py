# -*- coding: utf-8 -*-
import os
import threading

import numpy as np
from flask import Flask

import auto
from flagi import Flagi
from usb import Usb

app = Flask(__name__)
arduino_connect = Usb()
arduino_connect.open()
auto_log = "Start:\n"

flags = Flagi() # obiekt przechowujacy flagi

@app.route('/pcready')
def pc_read():
    flags.read_flags()
    flags.pc_status(1)
    return "pc ready"

@app.route('/numersfery') # zwracamy aktualny stan licznika miejsca w ktorym robione jest zdjecie 360
def numer_sfery():
    flags.read_flags()
    print("Numer sfery ",flags.numer_sfery)
    return str(flags.numer_sfery)

@app.route('/flagaauto') # zwracamy flage informujaca o trwaniu przejazdu autonomicznego: 0 - nie jedziemy, 1 - robot jedzie
def flaga_auto():
    flags.read_flags()
    return str(flags.auto_jazda)

@app.route('/flagaerror') # zwracamy flage informującą o bledach, do przyszlego uzytku
def flaga_error():
    flags.read_flags()
    return str(flags.error)

@app.route('/mapa') # zwracamy flage informującą o bledach, do przyszlego$
def mapa():
    return flags.read_map()

# Tymczasowo Arduino ignoruje przesyłane wartości przemieszczeń i kątów, więc są podawane dowolne.
# Tymczasowo nie można założyć, że Arduino zwraca informacje o dokonanym przemieszczeniu lub obrocie,
# więc nie sprawdzamy poprawności ruchu.
# Można za to założyć, że ruch zostanie przerwany przy zbliżaniu się do przeszkody.

@app.route('/forward')
def forward():  # Przesyla polecenie jazdy do przodu (f) i dystans (w metrach), nastepnie czeka na odpowiedz
    print("jedziemy do przodu")

    # implementacja
    distance = "10"  # tymczasowo dystans jest staly i ignowrowany
    orders = ["f", distance]
    arduino_connect.send(orders)
    status = arduino_connect.receive()
    print(status)  # status nie jest sprawdzany, zatem sie go tylko wypisuje
    # Kod czeka na lepsze czasy:
    # if status != distance:
    #   print("Error")
    # else:
    #   print("Ok")
    return "forward"


@app.route('/left')
def left():  # przesyla polecenie skretu w lewo (l) i kat (w stopniach), nastepnie czeka na odpowiedz
    print("skrecamy w lewo")
    # implementacja
    angle = "90"  # tymczasowo kat jest staly i ignowrowany
    orders = ["l", angle]
    arduino_connect.send(orders)
    status = arduino_connect.receive()
    print(status)  # status nie jest sprawdzany, zatem sie go tylko wypisuje
    return "left"


@app.route('/right')
def right():  # przesyla polecenie skretu w lewo (l) i kat (w stopniach), nastepnie czeka na odpowiedz
    print("skrecamy w prawo")
    angle = "30"  # tymczasowo kat jest staly i ignowrowany
    orders = ["r", angle]
    arduino_connect.send(orders)
    status = arduino_connect.receive()
    print(status)  # status nie jest sprawdzany, zatem sie go tylko wypisuje
    return "right"


@app.route('/backward')
def backward():  # przesyla polecenie jazdy do tylu (b) i dystans (w metrach), nastepnie czeka na odpowiedz
    print("jedziemy do tylu")

    # implementacja
    distance = "10"  # tymczasowo dystans jest staly i ignowrowany
    orders = ["b", distance]
    arduino_connect.send(orders)
    status = arduino_connect.receive()
    print(status)  # status nie jest sprawdzany, zatem sie go tylko wypisuje
    return "backward"


@app.route('/p')
def camera_right():  # przesyla polecenie skrętu serwa kamery w prawo (p) i kat (w stopniach),
    #  nastepnie czeka na odpowiedź
    print("serwo w prawo")

    # implementacja
    angle = "255"  # tymczasowo kat jest staly i ignowrowany
    orders = ["p", angle]
    arduino_connect.send(orders)
    status = arduino_connect.receive()
    print(status)  # status nie jest sprawdzany, zatem sie go tylko wypisuje

    return ""


@app.route('/q')
def camera_left():  # przesyla polecenie skretu serwa kamery w lewo (q) i kat (w stopniach),
    # następnie czeka na odpowiedź
    print("Obrót kamery w lewo")

    # implementacja
    angle = "255"  # tymczasowo kat jest staly i ignorowany
    orders = ["q", angle]
    arduino_connect.send(orders)
    status = arduino_connect.receive()
    print(status)  # status nie jest sprawdzany, zatem sie go tylko wypisuje

    return ""


@app.route('/s')
def get_data_from_sensors():  # przesyla polecenie pobrania danych z sensorów(s),
    # następnie czeka na odesłanie danych ze wszystkich sensorów.
    # Obecnie wypisuje tylko wszystko nieprzetworzone.
    # W przyszłości trzeba dodać opcję pobierania tych pomiarów do celów sterowania autonomicznego.
    print("Pobierz dane z sensorów")

    # implementacja
    angle = "0"  # tymczasowo kat jest staly i ignorowany
    orders = ["s", angle]  # Nie mam pojęcia, czy to konieczne. Ktoś to chyba przekopiował.
    arduino_connect.send(orders)
    status = arduino_connect.receive()
    print(status)  # status nie jest sprawdzany i przetwarzany ani formatowany, zatem sie go tylko wypisuje

    return status


@app.route('/test')
def test():
    orders = ["p"]
    arduino_connect.send(orders)
    status = arduino_connect.receive()
    print(status)  # status nie jest sprawdzany, zatem sie go tylko wypisuje
    return ""


@app.route('/single')
def single_shot(name="test"):  # wykonuje pojedyncze zdjecie i zapisuje je w katalogu static,
    # pod nazwą podaną jako argument -- string name
    print("robimy zdjecia")
    # command = "raspistill -n -t 1 -o static/"+name+".jpg"  # sekundowe opóźnienie, vs - stabilizacja
    command = "raspistill -n -w 1920 -h 1080 -vf -hf -vs -t 1 -o static/"+name+".jpg"  # natychmiast

    os.system(command)  # wywołujemy raspistill który wykonuje zdjęcie
    print("zrobiono zdjecie")
    return "zz"  # zdjecie zrobione


@app.route('/camera')
def round_camera(turns=16):  # Wykonuje pełen obrót kamerą i zdjęcia wokół
    # Zapisuje je jako pliki 0.jpg do 9.jpg z kolejnymi numerami
    # Zdjęcia nadpisują poprzednie!

    # Póki co, czekam aż Arduino zacznie zwracać i przyjmować kąty, o jakie kamera się obróciła.
    # Do tego czasu tymczasowe rozwiązanie.
    while flags.pc_ready == 0: #czekamy az pc pobierze stare zdjecia i ustawi flage ready
        pass

    for i in range(turns):
        name = str(i)
        single_shot(name)  # natychmiast wykonaj i zapisz zdjęcie.
        camera_right()  # może być i left(), jeśli to będzie miało znaczenie

    for j in range(turns): # obrocenie raspberry na pierwotna pozycje
        camera_left()

    #flags.increment_sfera() # zwiekszamy licznik gdy zdjecia gotowe aby PC moglo zaczac czytac zdjecia
    #flags.pc_status(0) # ustawiamy flage na 0 - pc sciaga zdjecia i jest niegotowe

@app.route('/cameraflaga')
def cameraflaga():
   print(flags)
   print("Zwrocono index: ", flags.numer_sfery)
   return "zdjecie "

@app.route('/photos')  # Pokazuje linki do zdjęć, można zrobić coś sprytniejszego
def photos():
    print("Pojedyncze: <\\br>")
    print('<a href="static/test.jpg"> Tu </a>')
    print("Pełne koło: <\\br>")
    for i in range(16):
        name = str(i)
        print('<a href="static/'+name+'.jpg">'+name+'</a>')
    # implementacja
    return ""

@app.route('/log')
def log():
    print(auto_log)
    return auto_log


@app.route('/cok')
def cok():
    coko = auto.LicznikMiejsca(flags)
    threading.Thread(target=coko.cokolwiek).start() # testujemy dzialanie watkow
    return "lol"

@app.route('/auto_test')
def auto_test():
    print("Test:")
    flags.auto_start()
    robot = auto.Driver(arduino_connect=arduino_connect, x_size=800, y_size=800)
    
    print(robot.position)
    dest = np.array([350,0])
    dest = robot.position + dest
    print(dest, type(dest))
    #robot.turn(45)
    #robot.forward(5)
    watek = threading.Thread(target = robot.run, args = [dest])     # TODO odpalenie jazdy w osobnym wątku
    watek.daemon = True
    watek.start()
    print(robot.position)
    #robot.krzysiek_turn(90)
    #robot.mateusz_forward(5)
    #robot.krzysiek_turn(90)
    #robot.pause(1)
    #robot.mateusz_forward(5) 
    #robot.krzysiek_turn(-90)
    #robot.mateusz_forward(5)
    #robot.krzysiek_turn(88)
    # auto_log += "auto"
    return auto_log

#def auto_thread():
    

@app.route('/auto_wall')
def auto_wall():  # przesyla polecenie jazdy do tylu (b) i dystans (w metrach), nastepnie czeka na odpowiedz
    print("Robot jest poza kontrolą")
    robot = auto.Driver(arduino_connect=arduino_connect)
#    stacksize = threading.stack_size()
#    print("Stacksize ", str(stacksize))
#    threading.stack_size(stacksize*2)
    watek = threading.Thread(target = robot.follow_wall, args = [15000])
    watek.daemon = True
    watek.start()
    return "auto"


if __name__ == '__main__':
    # arduino_connect.open() 
    app.run(host='0.0.0.0')

