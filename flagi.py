class Flagi():
    liczba_obiektow = 0
    def __init__(self):
        self.numer_sfery = 0 # flaga informujaca o numerze sfery dla ktorej przeznaczone sa zdjecia na raspberry
        self.auto_jazda = 0 # flaga informujaca o trwaniu autonomicznego przejazdu
        self.error = 0 # flaga dla ewentualnej obslugi bledow
        self.pc_ready = 1 # flaga dla PC, czy skonczyli pobierac
        if Flagi.liczba_obiektow != 0:
            self.read_flags()
            print("Obiekt flagi juz istnieje wiec wczytuje flagi z pliku")
        else:
            self.write_flags() # jezeli pierwszy obiekt to zapisujemy flagi poczatkowe
        Flagi.liczba_obiektow += 1

    def clear_file(self,file): # czyscimy plik przed zapisem nowych flag
        file.seek(0)
        file.truncate()

    def read_flags(self):
        file = open('flags.txt','r')
        self.numer_sfery = int(file.readline())
        self.pc_ready = int(file.readline())
        self.auto_jazda = int(file.readline())
        self.error = int(file.readline())
        print("Wczytano flagi(nr,pcr,auto,error): ",self.numer_sfery," ",self.pc_ready," ",self.auto_jazda," ",self.error)
        file.close()

    def write_flags(self):
        file = open('flags.txt','w')
        self.clear_file(file)
        print("Wyczyszczono plik flag")
        lista_flag = [self.numer_sfery,self.pc_ready,self.auto_jazda,self.error]
        file.writelines(lista_flag)
        print("Zapisano do pliku: ",lista_flag)
        file.close()

    def pc_status(self,status):
        self.pc_ready = status
        print("Flaga: pcstatus - ",status)
        self.write_flags()

    def increment_sfera(self):
        self.numer_sfery += 1
        print("Flaga: sfera - ",self.numer_sfery)
        self.write_flags()

    def auto_start(self):
        self.auto_jazda = 1
        print("Flaga: auto 1")
        self.write_flags()

    def auto_stop(self):
        self.auto_jazda = 0
        print("Flaga: auto 0")
        self.write_flags()

    def set_error(self,error):
        self.error = error
        self.write_flags()

    def reset_error(self):
        self.error = 0