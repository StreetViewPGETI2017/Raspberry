import numpy as np

class Flagi():
    liczba_obiektow = 0
    def __init__(self):

        self.numer_sfery = 0 # flaga informujaca o numerze sfery dla ktorej przeznaczone sa zdjecia na raspberry
        self.auto_jazda = 0 # flaga informujaca o trwaniu autonomicznego przejazdu
        self.error = 0 # flaga dla ewentualnej obslugi bledow
        self.pc_ready = 1 # flaga dla PC, czy skonczyli pobierac
        self.map_width = 80
        self.map_height = 80
        self.mapa = np.zeros((self.map_width,self.map_height))
        #self.save_map()

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
        file = open('/home/pi/projekt/flags.txt','w')
        self.clear_file(file)
        print("Wyczyszczono plik flag")
        lista_flag = [str(self.numer_sfery)+"\n",str(self.pc_ready)+"\n",str(self.auto_jazda)+"\n",str(self.error)+"\n"]
        file.writelines(lista_flag)
        print("Zapisano do pliku: ",lista_flag)
        file.close()

    def save_map(self,map):
        file = open('/home/pi/projekt/static/mapa.txt','w')
        self.clear_file(file)
        for y in range(self.map_height):
            for x in range(self.map_width):
                file.write(str(int(map[x,y])))
            file.write("\n")
        file.close()
        print("Zapisano mape do pliku")

    def read_map(self):
        file = open('/static/mapa.txt','r')
        return_map = ""
        for y in range(self.map_height):
            for x in range(self.map_width):
                current = file.read()
                return_map += current
            return_map += "\n"
        file.close()
        print("Wczytano mape")
        return return_map

    def update_map(self,map):
        #self.mapa = np.zeros((self.map_width,self.map_height))
        self.mapa = np.array(map, copy = True)

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
