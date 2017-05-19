# from usb import Usb

# import service

import numpy as np
import math
import time
from service import round_camera
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

# print(decompose("s(11,12,13)"))

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
        return self.matrix[position] == self.empty

    def set_empty(self, position):
        index_x, index_y = self.get_index(position)
        self.matrix[index_x, index_y] = self.empty

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

    def shortest_path(self, start_position, end_position):
        start_x = start_position[0]
        start_y = start_position[1]
        end_x = end_position[0]
        end_y = end_position[1]

        INF = 999999999

        def relax(old, x, y):
            new_cost = closed_cost[old] + 1
            if open_cost[x, y] > new_cost and closed_cost[x, y] == INF and self.can_go((x, y)):
                open_cost[x, y] = new_cost
                parent[x, y] = old
                # print(type(old))

        # class Node:
        #     def __init__(self, key, x, y):
        #         self.key = key
        #         self.x = x
        #         self.y = y

        # TODO: kopiec

        open_cost = np.zeros((self.x_size, self.y_size))
        closed_cost = np.zeros((self.x_size, self.y_size))
        parent = np.zeros((self.x_size, self.y_size, 2))
        parent.fill(INF)
        open_cost.fill(INF)
        closed_cost.fill(INF)

        open_cost[start_x, start_y] = 0
        parent[start_x, start_y] = [-1, -1]

        while closed_cost[end_x, end_y] == INF:
            candidate_pos = np.unravel_index(open_cost.argmin(), open_cost.shape)  # magiczna linia, indeks minimum
            # print(candidate_pos, open_cost[candidate_pos])
            if open_cost[candidate_pos] == INF:
                return None  # nie udalo sie znalezc
            else:
                closed_cost[candidate_pos] = open_cost[candidate_pos]
                open_cost[candidate_pos] = INF
                c_x = candidate_pos[0]
                c_y = candidate_pos[1]

                # new_cost = closed_cost[c_x, c_y] + 1 # bo przechodzimy dalej
                # lewo
                if self.is_index_inside(c_x - 1, c_y):
                    relax(candidate_pos, c_x - 1, c_y)
                # prawo
                if self.is_index_inside(c_x + 1, c_y):
                    relax(candidate_pos, c_x + 1, c_y)
                # góra
                if self.is_index_inside(c_x, c_y - 1):
                    relax(candidate_pos, c_x, c_y - 1)
                # dół
                if self.is_index_inside(c_x, c_y + 1):
                    relax(candidate_pos, c_x, c_y + 1)

        # odtwarzanie ścieżki
        current = end_position
        c_x = current[0]
        c_y = current[1]
        current = np.array([c_x, c_y])
        path = []
        # while current[0] != start_position[0] or current[1] != start_position[1]:
        # print(current, start_position)
        # print(current[0] != start_position[0] or current[1] != start_position[1])
        # while (parent[current] != [-1, -1]).any():
        # print(type(start_position[0]))
        while c_x != start_position[0] or c_y != start_position[1]:
            # print(current)
            path.insert(0, current)
            current = parent[c_x, c_y]
            c_x, c_y = current

        # print(path)
        return path
        # return closed_cost[end_x, end_y] # To długość najkrótszej ścieżki


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
    def __init__(self, arduino_connect, world=None):
        # print(flags.pc_status)
        if world is None:
            world = World(800, 800, 40, 40)
        self.world = world
        self.flags = Flagi()
        self.distance = 0  # dystans przebyty od ostatniego zdjęcia
        self.photo_distance = 200  # dystans, po którym należy robić zdjęcie
        self.arduino_connect = arduino_connect
        # Zakładamy, że to jedyny driver, ale można zmodyfikować na wielu agentów
        self.position = self.world.get_center_position()
        # self.position = np.array(self.position)
        self.rotation = 0  # stopni

    def find_path(self, destination):
        destination_index = self.world.get_index(destination)
        # destination_index = destination
        own_index = self.world.get_index(self.position)
        print("\t",own_index, destination_index)
        if own_index[0] == destination_index[0] and own_index[1] == destination_index[1]:
            path = None
            print("Meta")
            #self.flags.autostop()
        else:
            path = self.world.shortest_path(own_index, destination_index)
        # for p in path:
            # p = self.world.get_position(p)
        return path

    def run(self, destination):
        self.handle_observations()
        self.print_surrounding_map()
        path = self.find_path(destination)
        print(path)
        if path is None:
            return
        else:
            print("RUN")
            # print(self.position)
            # print(path[0])
            next = self.world.get_position(path[0])
            print(next)
            self.move(next)
            self.world.print()
            self.run(destination)
            self.handle_observations()
        # while not path:
            # self.move(path[0])
            # path = self.find_path(destination)

    # może zrobić wersję move(path)?
    def move(self, destination):
        print(destination, self.position)
        print("lol")
        diff = destination - self.position
        print(diff, angle(diff), length(diff))
        self.krzysiek_turn(angle(diff))
        # self.pause(10)
        self.mateusz_forward(length(diff))
        # self.pause(10)
        # self.handle_observations()
        # self.pause(10)

    def handle_photos(self):
        if self.distance > self.photo_distance:
            self.distance = 0
            round_camera()
            self.flags.increment_sfera()

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
        self.handle_photos()
        # self.position += (distance * direction)

    def krzysiek_turn(self, degrees):
        degrees = degrees - self.rotation
        if(degrees > 0):
            while(degrees > 15):
                degrees -= 30
                print("prawo", degrees)
                self.turn(30)
        else:
            while(degrees < -15):
                degrees += 30
                print("lewo", degrees)
                self.turn(-30)

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
            diff -= 180
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
        pass
        #TODO zrobić obrót i zapisać self.rotation


    def pause(self, seconds):
        time.sleep(seconds)

    def handle_observations(self):
        orders = ["s"]
        print("Obserwacje:")
        self.arduino_connect.send(orders)
        status = self.arduino_connect.receive()
        # print(status)
        # s(pr,pra,l)E
        # TODO pobrać trzy obserwacje i użyć poniższej funkcji
        front, right, left = decompose(status) # odleglosci
        print(front, right, left)
        self.set_observation_obstacle(front, 0)
        self.set_observation_obstacle(right, 1)
        self.set_observation_obstacle(left, 2)

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


# robot = Driver()
# # print(robot.position)
# # robot.move(np.array([21, 40]))
# # robot.print()
#
# # print
# robot.world.set_obstacle((3, 2))
# robot.world.set_obstacle((4, 2))
# robot.world.set_obstacle((4, 3))
# robot.world.set_obstacle((4, 1))
# robot.world.set_obstacle((4, 0))
# robot.world.set_obstacle((3, 0))
# robot.world.set_obstacle((3, 3))
# robot.world.set_obstacle((3, 4))
# robot.world.print()
#
# robot.move(np.array([2, 2]))
# robot.print()
# dest_pos = robot.world.get_position(np.array([6, 2]))
# robot.run(dest_pos)
#
# # path = (robot.world.shortest_path(np.array([2, 2]), np.array([6, 2])))
# # for i in path:
# #     print(i)
# #     robot.move(i)
# #     robot.print()
# #
# robot.print()

