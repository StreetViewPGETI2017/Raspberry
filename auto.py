# -*- coding: utf-8 -*-

# from usb import Usb

# import service

import numpy as np
import math
import time
import picamera
import os

from flagi import Flagi

def decompose(txt):
    txt = txt[1]
    txt = txt.strip()
    txt = txt.strip("(")
    # 	rest, txt = txt.("(")
    txt = txt.strip(")")
    # print(txt)
    front, right, left = txt.split(",")
    return float(front), float(right), float(left)


# Klasa reprezentujaca stan otaczajacego swiata
class World(object):
    empty = int(0)
    obstacle = int(1)

    def __init__(self, x_size, y_size, unit_x_size, unit_y_size):
        self.x_size = x_size / unit_x_size
        self.y_size = y_size / unit_y_size
        self.unit_x_size = unit_x_size
        self.unit_y_size = unit_y_size
        self.matrix = np.zeros((x_size, y_size))  # zera oznaczają puste pozycje

    def get_index(self, pos):
        # print(pos, type(pos))
        index_x = pos[0] // self.unit_x_size
        if index_x >= self.x_size:
            index_x = None
        index_y = pos[1] // self.unit_y_size
        if index_y >= self.y_size:
            index_y = None
        return np.array((index_x, index_y))

    def get_position(self, index):
        index_x = index[0]
        index_y = index[1]
        pos_x = index_x * self.unit_x_size + self.unit_x_size / 2
        pos_y = index_y * self.unit_x_size + self.unit_y_size / 2  # pytanie co z ulamkami bedzie
        return np.array([pos_x, pos_y])

    def can_go(self, position):
        return self.matrix[position] != self.obstacle

    def set_empty(self, position):
        index_x, index_y = self.get_index(position)
        self.matrix[index_x, index_y] = self.empty

    def set_number(self, position, number):
        index_x, index_y = self.get_index(position)
        self.matrix[index_x, index_y] = number


    def set_obstacle(self, position):
        # print(position)
        index = self.get_index(position)
        # print(index)
        self.matrix[index[0], index[1]] = self.obstacle

    def get_center_position(self):
        return self.get_position((self.x_size / 2, self.y_size / 2))

    def is_index_inside(self, index_x, index_y):
        return 0 <= index_x < self.x_size and 0 <= index_y < self.y_size

    def print(self):
        print(self.matrix)


def length(vector):
    x = vector[0]
    y = vector[1]
    distance = math.sqrt(x ** 2 + y ** 2)
    # distance = math.(x ** 2 + y ** 2) ** (-2)
    return distance


def angle(vector):
    x = vector[0]
    y = vector[1]
    radians = math.atan2(y, x)

    degrees = math.degrees(radians)
    return degrees


def angle_to_vector(degree):
    radian = math.radians(degree)
    x = math.cos(radian)
    y = math.sin(radian)
    vec = np.array([x, y])
    return vec


# Klasa reprezentujaca jeżdżącego robota. Operuje na pozycjach, nie indeksach!
class Driver(object):
    def __init__(self, arduino_connect, world=None, x_size=6000, y_size=6000, cell=100, photo_distance = 500):
        # print(flags.pc_status)
        if world is None:
            world = World(x_size, y_size, cell, cell)
        self.world = world
        self.flags = Flagi()
        self.distance = 0  # dystans przebyty od ostatniego zdjęcia
        self.photo_distance = photo_distance  # dystans, po którym należy robić zdjęcie
        self.arduino_connect = arduino_connect
        # Zakładamy, że to jedyny driver, ale można zmodyfikować na wielu agentów
        self.position = self.world.get_center_position()
        # self.position = np.array(self.position)
        self.rotation = 0  # stopni

    def observations(self):
        orders = ["s"]
        #print("Obserwacje:")
        self.arduino_connect.send(orders)
        status = self.arduino_connect.receive()
        # print(status)

        front, right, left = decompose(status) # odleglosci
        if front < 30:
           orders = ["s"]
           self.arduino_connect.send(orders)
           status = self.arduino_connect.receive()
           front, right, left = decompose(status)
        self.print_surrounding_map()
        print("Sensory(f,r,l): ", front, right, left)
        return front, right, left



    def follow_wall(self, length, distance_to_wall = 60):
        print("algorytm")
        distance_passed = 0

        margin = 30
        far_away = 200
        long_step = 45
        short_step = 10
        correction_angle = 15 
        while distance_passed < length:
            front, right, left = self.observations()
           # print(front, right, left)
            self.set_observation_obstacle(front, 0)
            self.set_observation_obstacle(right, 1)
            self.set_observation_obstacle(left, 2)
            error = left - distance_to_wall 
           # print(error)
            
            if front < 30:
                print("if nr 1")
                self.backward(20)
                self.turn(30)

            elif abs(error) < margin:
                print("if nr 2")
                distance_passed += self.forward(long_step)
                print("pojechalem prosto")

            elif left > far_away: 
                print("if nr 3") 
                wh = 1
                self.turn(-60)
                front, right, left = self.observations()
                while left > far_away:
                    print("while nr:", wh)
                    #self.forward(long_step)
                    distance_passed += self.forward(long_step)
                    self.turn(-correction_angle)
                    front, right, left = self.observations()
                    wh += 1
            elif error < 0:  # oddal sie
                print("if nr 4")
                if front < 0:
                    #self.turn(-45)
                    pass
                else:
                    self.turn(correction_angle)
                    distance_passed += self.forward(short_step)
            elif error > 0:  # przybliz sie
                print("if nr 5")
                if front < 0:
                    #self.turn(45)
                    pass
                else:
                    self.turn(-correction_angle)
                    distance_passed += self.forward(long_step)
                    self.turn(correction_angle)

        print(left, distance_passed)

    def photo_picam(self, name): # robienie zdjec za pomoca biblioteki picamera
        camera = picamera.PiCamera()
        camera.resolution = (1920, 1080) # ustawienia kamery
        camera.hflip = True
        camera.vflip = True
        camera.exposure_mode = 'off' # auto
        camera.meter_mode = 'average'
        camera.capture("static/" + name + ".jpg")  # natychmiast wykonaj i zapisz zdjęcie.
        time.sleep(1)
        camera.close()

    def photo_raspistill(self, name): # robienie zdjec raspistill
        command = "raspistill -n -w 1920 -h 1080 -vf -hf -vs -t 1000 -o static/" + name + ".jpg"  # natychmiast
        os.system(command)  # wywołujemy raspistill który wykonuje zdjęcie

    def handle_photos(self):
        print("Przejechany dystans: ",self.distance)
        if self.distance > self.photo_distance:
            print("Robie sfere")
            self.distance = 0


            for i in range(16):
                name = str(i)
                print("Robie zdjecie "+name)

                self.photo_picam(name)
                # self.photo_raspistill(name) # tu mozemy wybrać która metoda

                if i<15: # nie potrzebujemy ostatniego obrotu
                    orders = ["p", "180"]  # obracamy kamera w prawo
                    self.arduino_connect.send(orders)
                    status = self.arduino_connect.receive()

            orders = ["q", "180"]
            for j in range(15):  # obrocenie raspberry na pierwotna pozycje
                self.arduino_connect.send(orders)
                status = self.arduino_connect.receive()

            self.flags.increment_sfera() # zwiekszamy licznik gdy zdjecia gotowe aby PC moglo zaczac czytac zdjecia
            self.flags.pc_status(0) # ustawiamy flage na 0 - pc sciaga zdjecia i jest niegotowe
            self.flags.update_map(self.world.matrix)
            print("Map update wykonano")
            self.flags.save_map()


    def mateusz_forward(self, distance):
        self.forward(round(distance))

    def forward(self, distance):
        # # Wersja wirtualna:
        direction = angle_to_vector(self.rotation)
        # diff = [direction[0] * distance, direction[1] * distance]
        # diff = np.array(diff)
        # # self.position += (distance * direction)
        # self.position = np.add(self.position, diff)
        #Wersja realna:
        orders = ["f", str(distance)]
        print(orders)
        self.arduino_connect.send(orders)
        status = self.arduino_connect.receive()
        # print(status)
        # TODO  zapisać self.position
        # Optymistycznie, do wywalenia :(
        status = status[-1]
        status = status.rstrip()
        print("Ruch do przodu: ",status)
        real_dist = float(status)
        self.distance += real_dist
        self.position += (real_dist * direction)
        print("Handluje zdjecia")
        self.handle_photos()
        print("Pohandlowane")
        return real_dist
        # self.position += (distance * direction)

    def backward(self, distance):
        # # Wersja wirtualna:
        direction = angle_to_vector(self.rotation)
        # diff = [direction[0] * distance, direction[1] * distance]
        # diff = np.array(diff)
        # # self.position += (distance * direction)
        # self.position = np.add(self.position, diff)
        #Wersja realna:
        orders = ["b", str(distance)]
        print(orders)
        self.arduino_connect.send(orders)
        status = self.arduino_connect.receive()
        # print(status)
        # TODO  zapisać self.position
        # Optymistycznie, do wywalenia :(
        status = status[-1]
        status = status.rstrip()
        print("Ruch do tyłu: ",status)
        real_dist = float(status)
        self.distance += real_dist
        self.position -= (real_dist * direction)
        self.handle_photos()
        return real_dist
        # self.position += (distance * direction)

    def turn(self, degrees):
        # # Wersja wirtualna:
        # # print(self.rotation)
        # self.rotation = degrees
        # # print(self.rotation)
        # diff = degrees - self.rotation
        diff = degrees # zmienione w krzyiek_turn()
        while diff < 0:
            diff += 360
        while diff > 360:
            diff -= 360
        if diff > 180:
            diff = 360 - diff
            orders = ["l", str(round(diff))]
            rtrn = False
        else:
            orders = ["r", str(round(diff))]
            rtrn = True
        # print(diff)
        # print(orders)
        # print("-----")
        self.arduino_connect.send(orders)
        status = self.arduino_connect.receive()
        # print(status)
        status = status[-1]
        status = status.rstrip()
        real_angle = float(status)
        print(real_angle)
        # Optymistycznie, do wywalenia :(
        if rtrn:
            self.rotation += real_angle
        else:
            self.rotation -= real_angle
        # TODO ogarnac status
        # status.
        # self.rotation = ?
        # self.position = ?

        # Wersja realna:
    #    pass
        #TODO zrobić obrót i zapisać self.rotation


   # def pause(self, seconds):
   #     time.sleep(seconds)

    def print_surrounding_map(self):
        index = self.world.get_index(self.position)
        x = index[0]
        y = index[1]
        for i in range(-5, 5, 1):
            for j in range(-5, 5, 1):
                if i == 0 and j == 0:
                    print("X", end=" ")
                elif self.world.is_index_inside(x+j, y+i):
                    print(int(self.world.matrix[x+j, y+i]), end=" ")
            print()

    def set_observation_obstacle(self, distance, side):
        # side = [0, 1, 2]
        # return
        angle = 0
        angle = self.rotation
        if side == 0:
            angle += 0
        if side == 1:
            angle += 90
        if side == 2:
            angle += -90
        direction = angle_to_vector(angle)
        diff = [direction[0] * distance, direction[1] * distance]
        diff = np.array(diff)
        observation_pos = self.position + diff

        # DONE wyifować specjalną wartość
        special_max_distance = 100
        special_min_distance = 5
        if distance < special_max_distance and distance > special_min_distance:
            # observation_index = self.world.get_index(observation_pos)
            self.world.set_obstacle(observation_pos)

    def print(self):
        print(self.position, self.rotation)


