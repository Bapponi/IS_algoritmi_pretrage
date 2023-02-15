import math
import os
import random
import queue

import pygame

import config


class BaseSprite(pygame.sprite.Sprite):
    images = dict()

    def __init__(self, x, y, file_name, transparent_color=None, wid=config.SPRITE_SIZE, hei=config.SPRITE_SIZE):
        pygame.sprite.Sprite.__init__(self)
        if file_name in BaseSprite.images:
            self.image = BaseSprite.images[file_name]
        else:
            self.image = pygame.image.load(os.path.join(config.IMG_FOLDER, file_name)).convert()
            self.image = pygame.transform.scale(self.image, (wid, hei))
            BaseSprite.images[file_name] = self.image
        # making the image transparent (if needed)
        if transparent_color:
            self.image.set_colorkey(transparent_color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


class Surface(BaseSprite):
    def __init__(self):
        super(Surface, self).__init__(0, 0, 'terrain.png', None, config.WIDTH, config.HEIGHT)


class Coin(BaseSprite):
    def __init__(self, x, y, ident):
        self.ident = ident
        super(Coin, self).__init__(x, y, 'coin.png', config.DARK_GREEN)

    def get_ident(self):
        return self.ident

    def position(self):
        return self.rect.x, self.rect.y

    def draw(self, screen):
        text = config.COIN_FONT.render(f'{self.ident}', True, config.BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class CollectedCoin(BaseSprite):
    def __init__(self, coin):
        self.ident = coin.ident
        super(CollectedCoin, self).__init__(coin.rect.x, coin.rect.y, 'collected_coin.png', config.DARK_GREEN)

    def draw(self, screen):
        text = config.COIN_FONT.render(f'{self.ident}', True, config.RED)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class Agent(BaseSprite):
    def __init__(self, x, y, file_name):
        super(Agent, self).__init__(x, y, file_name, config.DARK_GREEN)
        self.x = self.rect.x
        self.y = self.rect.y
        self.step = None
        self.travelling = False
        self.destinationX = 0
        self.destinationY = 0

    def set_destination(self, x, y):
        self.destinationX = x
        self.destinationY = y
        self.step = [self.destinationX - self.x, self.destinationY - self.y]
        magnitude = math.sqrt(self.step[0] ** 2 + self.step[1] ** 2)
        self.step[0] /= magnitude
        self.step[1] /= magnitude
        self.step[0] *= config.TRAVEL_SPEED
        self.step[1] *= config.TRAVEL_SPEED
        self.travelling = True

    def move_one_step(self):
        if not self.travelling:
            return
        self.x += self.step[0]
        self.y += self.step[1]
        self.rect.x = self.x
        self.rect.y = self.y
        if abs(self.x - self.destinationX) < abs(self.step[0]) and abs(self.y - self.destinationY) < abs(self.step[1]):
            self.rect.x = self.destinationX
            self.rect.y = self.destinationY
            self.x = self.destinationX
            self.y = self.destinationY
            self.travelling = False

    def is_travelling(self):
        return self.travelling

    def place_to(self, position):
        self.x = self.destinationX = self.rect.x = position[0]
        self.y = self.destinationX = self.rect.y = position[1]

    # coin_distance - cost matrix
    # return value - list of coin identifiers (containing 0 as first and last element, as well)
    def get_agent_path(self, coin_distance):
        pass

    def heapPermutation(a, size):
        pass


class ExampleAgent(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        path = [i for i in range(1, len(coin_distance))]
        random.shuffle(path)
        return [0] + path + [0]


class Aki(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        # print(coin_distance)
        i = 0
        path = [0]
        for x in range(len(coin_distance) - 1):
            # print(x, "/////////////////////////////////////////////////////////////////////")
            j_min = len(coin_distance) + 2
            min = 1000000
            for j in range(len(coin_distance)):
                if j not in path and coin_distance[i][j]!=0:
                    # print("Kolona koja je bitna", j_min)
                    # print("Minimalna vrednost trenutna", coin_distance[i][j], "Minimum vrednost globalna" , min)
                    if coin_distance[i][j] < min:
                        min = coin_distance[i][j]
                        j_min = j
                        # print("Minimum vrednost" , min)
                        # print("Minimum kolona" , j_min)
            path.append(j_min)
            i = j_min
            # print("Sledeca vrsta", i)
        # print(path)
        return path + [0]


class Jocke(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    costMin = 100000
    path = [0, 1, 2, 3, 4, 0]

    def permutation(a, size, coin_distance):
        if size == 1:
            # print()
            # print("Trenutni niz", a)
            # print("Trenutni najkraci put:", Jocke.path, "Najmanja cena:", Jocke.costMin, "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            cost = 0

            for x in range(len(a) - 1):
                cost += coin_distance[a[x]][a[x+1]]

            cost += coin_distance[0][a[0]]
            cost += coin_distance[a[len(a) - 1]][0]
            # print("Cena na kraju:", cost, "Globalno Min:", Jocke.costMin)

            if(cost < Jocke.costMin):
                Jocke.costMin = cost
                Jocke.path = a.copy()
                # print("Trenutni najkraci put:", Jocke.path, "Najmanja cena:", Jocke.costMin)

            return

        for i in range(size):
            Jocke.permutation(a, size-1, coin_distance)
            
            if size & 1:
                a[0], a[size-1] = a[size-1], a[0]
            else:
                a[i], a[size-1] = a[size-1], a[i]

    
    def get_agent_path(self, coin_distance):
        a = []
        n = len(coin_distance) - 1

        for i in range(1, len(coin_distance)):
            a.append(i)
        
        # print(a, n)

        Jocke.permutation(a, n, coin_distance)
        # print("Izasao", Jocke.path)

        return [0] + Jocke.path + [0]

class Uki(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):

        pQueue = queue.PriorityQueue()
        pQueue.put((0, len(coin_distance), 0, [0]))
        path = [0]
        i = 0
        krug = 0

        # print("Pre for-a")
        while(1):
            krug += 1
            # print("")
            # print(krug, ". prolaz kroz ciklus")
            temp = pQueue.get()
            putKraj = temp[3]
            if(len(putKraj) == len(coin_distance)):
                path = putKraj
                break
            i = temp[2]
            for j in range(len(coin_distance)):
                if j not in temp[3] and coin_distance[i][j]!=0:
                    cena = temp[0] + coin_distance[i][j]
                    br = temp[1] - 1
                    id = j
                    put = temp[3] + [j]
                    # print("Cena distance", coin_distance[i][j],"Nova cena:", cena, "Ostatak novcica:", br, "ID", id, "Put", put, "Duzina puta", len(put))
                    if(len(put)==len(coin_distance)):
                        cena += coin_distance[j][0]
                    pQueue.put((cena, br, id, put))    


        # print("Krajnji put:", path)

        return path + [0]


class Micko(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_MST(self, coin_distance, current):

        if(current == []):
            return 0
        i = 0
        path = [0]
        connections = []
        rest = [0]

        for z in range(len(coin_distance)):
            if z not in current:
                rest.append(z)

        while(1):
            min = 100000
            j_min = len(coin_distance) + 2
            i_min = len(coin_distance) + 2
            price = 0
            for x in range(len(path)):
                if(len(path) == len(rest)):
                    for y in range(len(connections)):
                        veza = connections[y]
                        price += coin_distance[veza[0]][veza[1]]
                    return price
                i = x
                for j in rest:
                    if j not in path and coin_distance[i][j]!=0:
                        if coin_distance[i][j] < min:
                            j_min = j
                            i_min = i
                            min = coin_distance[i][j]
            connections.append((i_min, j_min))
            path.append(j_min)
            # print("Cvorevi", path, "Putanje", connections)

    def get_agent_path(self, coin_distance):

        pQueue = queue.PriorityQueue()
        pQueue.put((0, len(coin_distance), 0, [0], []))
        path = [0]
        i = 0
        krug = 0

        while(1):
            krug += 1
            # print("")
            # print(krug, ". prolaz kroz ciklus")
            temp = pQueue.get()
            putKraj = temp[3]
            if(len(putKraj) == len(coin_distance)):
                path = putKraj
                break
            i = temp[2]
            for j in range(len(coin_distance)):
                if j not in temp[3] and coin_distance[i][j]!=0:
                    cena = temp[0] + coin_distance[i][j] + Micko.get_MST(self, coin_distance, temp[3]) - Micko.get_MST(self, coin_distance, temp[4])
                    br = temp[1] - 1
                    id = j
                    put = temp[3] + [j]
                    # print("Cena distance", coin_distance[i][j],"Nova cena:", cena, "Ostatak novcica:", br, "ID", id, "Put", put, "Stari put", temp[3])
                    if(len(put)==len(coin_distance)):
                        cena += coin_distance[j][0]
                    pQueue.put((cena, br, id, put, temp[3]))    

        # print("Krajnji put:", path)

        return path + [0]