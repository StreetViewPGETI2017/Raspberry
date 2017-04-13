from flask import Flask
import os
from usb import Usb
app = Flask(__name__)
arduino_connect = Usb()

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
    angle = "90"  # tymczasowo kat jest staly i ignowrowany
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
    angle = "0"  # tymczasowo kat jest staly i ignowrowany
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
    angle = "0"  # tymczasowo kat jest staly i ignorowany
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
    # command = "raspistill -n -t 1 -o static/"+name+".jpg"  # sekundowe opóźnienie
    command = "raspistill -n -t -o static/"+name+".jpg"  # natychmiast

    os.system(command)  # wywołujemy raspistill który wykonuje zdjęcie
    print("zrobiono zdjecie")
    return "zz"  # zdjecie zrobione


@app.route('/camera')
def round_camera(turns=10):  # Wykonuje pełen obrót kamerą i zdjęcia wokół
    # Zapisuje je jako pliki 0.jpg do 9.jpg z kolejnymi numerami
    # Zdjęcia nadpisują poprzednie!

    # Póki co, czekam aż Arduino zacznie zwracać i przyjmować kąty, o jakie kamera się obróciła.
    # Do tego czasu tymczasowe rozwiązanie.
    # NIEPRZETESTOWANE na robocie
    for i in range(turns):
        name = str(i)
        single_shot(name)  # natychmiast wykonaj i zapisz zdjęcie.
        right()  # może być i left(), jeśli to będzie miało znaczenie


@app.route('/photos')  # Pokazuje linki do zdjęć, można zrobić coś sprytniejszego
def photos():
    print("Pojedyncze: <\\br>")
    print('<a href="static/test.jpg"> Tu </a>')
    print("Pełne koło: <\\br>")
    for i in range(10):
        name = str(i)
        print('<a href="static/'+name+'.jpg">'+name+'</a>')
    # implementacja
    return ""


if __name__ == '__main__':
    arduino_connect.open()
    app.run(host='0.0.0.0')
