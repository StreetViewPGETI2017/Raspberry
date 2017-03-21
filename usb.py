import serial

class usb:
    ser = serial.Serial
    def open(self): # otwiera polaczenie;stale wartosci, mozna sparametryzowac
        self.ser = serial.Serial ("/dev/ttyACM0")    #Open named port
        self.ser.baudrate = 9600                     #Set baud rate to 9600


    def write(self, order): # Pisze na usb pojedyncza linie
        self.ser.write(order.encode)


    def send(self, orders): # wysyla liste orders z dodanym znakiem konca "$"
        for i in orders:
            write(i.encode())
        write(b"$") # koniec polecenia


    def read(self): # czeka i zwraca pojedyncza odpowiedz (linie)
        data = self.ser.readline()
        # print(out)
        return data.decode()  # Zwraca odpowiedz przekonwertowana na stringa


    def receive(self): # czeka, wczytuje do "$" i zwraca wszysstkie komunikaty jako liste (bez "$").
        data = []
        last = read()
        while last != "$":
            data = data + last
            last = read()
        return data



    def close(self): # zamkniecie polaczenia po usb
       self.ser.close()
