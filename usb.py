import serial

class usb:
    ser = serial.Serial
    def open(self): # otwiera polaczenie;stale wartosci, mozna sparametryzowac
        self.ser = serial.Serial ("/dev/ttyACM0")    #Open named port
        self.ser.baudrate = 9600                     #Set baud rate to 9600


    def write(self, order): # Pisze na usb pojedyncza linie
        self.ser.write(order.encode())


    def send(self, orders): # wysyla liste orders z dodanym znakiem konca "$"
        for i in orders:
            self.write(i)
        self.write('E') # koniec polecenia


    def read(self): # czeka i zwraca pojedyncza odpowiedz (linie)
        data = self.ser.readline()
        print(data)
        return data.decode()  # Zwraca odpowiedz przekonwertowana na stringa


    def receive(self): # czeka, wczytuje do "$" i zwraca wszysstkie komunikaty jako liste (bez "$").
        data = []
        last = self.read()
        while last != 'E\r\n':
            data.append(last)
            last = self.read()
            print(last)
        print("Koniec")
        return data



    def close(self): # zamkniecie polaczenia po usb
       self.ser.close()
