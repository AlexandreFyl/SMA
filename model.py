import math
import random
from pygame.locals import *
import pygame
from queue import Queue

# Constants
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

class Element :
    def __init__(self, x, y) :
        self.x=x
        self.y=y

class Scene(Element):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.sizeX = 200
        self.sizeY = 100
        self.sizeDanceFloorX = 3*self.sizeX
        self.sizeDanceFloorY = 3.5*self.sizeY
        self.left = self.x
        self.right = self.x + self.sizeDanceFloorX
        self.top = self.y
        self.bottom = self.y + self.sizeDanceFloorY
        self.leftStage = self.x + (self.sizeDanceFloorX / 2) - (self.sizeX / 2)
        self.rightStage = self.leftStage + self.sizeX

    def collidepoint(self, x, y):
        in_dance_floor = (self.left <= x < self.right and self.top <= y < self.bottom)
        on_stage = (self.leftStage <= x < self.rightStage and self.top <= y < self.top + self.sizeY)
        return in_dance_floor and not on_stage
       
    def draw(self, surface) :
        rect_x = self.x + (self.sizeDanceFloorX - self.sizeX) // 2
        pygame.draw.rect(surface, BLACK, (rect_x, self.y, self.sizeX, self.sizeY))
        pygame.draw.rect(surface, BLACK, (self.x, self.y, self.sizeDanceFloorX, self.sizeDanceFloorY), 1)

class Bar(Element):
    def __init__(self, x, y, manager, bartenders):
        super().__init__(x, y)
        self.manager = manager
        self.bartenders = bartenders or []
        self.queue = Queue()
        self.sizeX = 50
        self.sizeY = 50
        self.left = self.x
        self.right = self.x + self.sizeX
        self.top = self.y
        self.bottom = self.y + self.sizeY
    
    def collidepoint(self, x, y):
        return self.left < x < self.right and self.top < y < self.bottom

    def draw(self, surface):
        pygame.draw.rect(surface, GREEN, (self.x, self.y, 50, 50))

    def addStaff(self, agent):
        self.bartenders.append(agent)

    def removeStaff(self, agent):
        self.bartenders.remove(agent)

    def addToQueue(self, agent):
        self.queue.put(agent)

    def serveCustomers(self):
        for bartender in self.bartenders:
            if not self.queue.empty():
                customer = self.queue.get()
                print(f"Bar at ({self.x}, {self.y}) served {customer.name} by {bartender.name}")

    def update(self):
        self.serveCustomers()

    def removeFromQueue(self):
        if not self.queue.empty():
            return self.queue.get()
        return None

class Toilets(Element):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.queue = Queue()
        self.sizeX = 30
        self.sizeY = 30
        self.left = self.x
        self.right = self.x + self.sizeX
        self.top = self.y
        self.bottom = self.y + self.sizeY
        self.leftStage = self.right - self.left

    def collidepoint(self, x, y):
        return self.left < x < self.right and self.top < y < self.bottom
    
    def draw(self, surface):
        pygame.draw.rect(surface, BLUE, (self.x, self.y, 30, 30))

    def addToQueue(self, agent):
        self.queue.put(agent)

    def update(self):
        if not self.queue.empty():
            customer = self.queue.get()
            print(f"Toilet at ({self.x}, {self.y}) used by {customer.name}")

class Agent :
    def __init__(self,name) :
        self.name=name

class ListenerAgent(Agent):
    def __init__(self, name, scene):
        super().__init__(name)
        self.type = "Listener"
        self.scene = scene
        self.x, self.y = self.get_valid_position(scene)
        self.thirstScore = random.uniform(0, 40)
        self.urgeToPeeScore = random.uniform(0, 60)
        self.thirstThreshold = random.uniform(40, 60)
        self.peeThreshold = random.uniform(60, 80)
        self.thirstIncrementRate = random.uniform(0.05, 0.15)
        self.peeIncrementRate = random.uniform(0.08, 0.2)
        self.speed = random.uniform(0.5, 1.5)
        self.direction = random.uniform(0, 2 * math.pi)
        self.state = "dancing"
        self.destination = None
        self.current_bar = None
        self.current_toilet = None
        self.radius = 5
        self.move_speed = 2

    def update(self, bars, toilets):
        if self.state == "dancing":
            self.dance()
            self.thirstScore += self.thirstIncrementRate * random.uniform(0.8, 1.2)
            self.urgeToPeeScore += self.peeIncrementRate * random.uniform(0.8, 1.2)
            
            if self.thirstScore > self.thirstThreshold and random.random() < 0.1:
                self.getADrink(bars)
            elif self.urgeToPeeScore > self.peeThreshold and random.random() < 0.1:
                self.goPee(toilets)

        elif self.state == "moving_to_bar":
            self.move_to_destination()
            if self.reached_destination():
                self.state = "at_bar"
                self.current_bar.addToQueue(self)

        elif self.state == "moving_to_toilet":
            self.move_to_destination()
            if self.reached_destination():
                self.state = "at_toilet"
                self.current_toilet.addToQueue(self)

        elif self.state == "at_bar":
            if self not in self.current_bar.queue.queue:
                self.thirstScore = 0
                self.urgeToPeeScore += random.uniform(10, 20)
                if self.urgeToPeeScore > self.peeThreshold and random.random() < 0.5:
                    self.goPee(toilets)
                else:
                    self.return_to_scene()

        elif self.state == "at_toilet":
            if self not in self.current_toilet.queue.queue:
                self.urgeToPeeScore = 0
                if self.thirstScore > self.thirstThreshold and random.random() < 0.5:
                    self.getADrink(bars)
                else:
                    self.return_to_scene()

        elif self.state == "returning_to_scene":
            self.move_to_destination()
            if self.reached_destination():
                self.state = "dancing"

    def getADrink(self, bars):
        if self.state in ["dancing", "at_toilet"]:
            print(f"Listener {self.name} is getting a drink (Thirst: {self.thirstScore:.2f})")
            self.current_bar = min(bars, key=lambda bar: math.dist((self.x, self.y), (bar.x, bar.y)))
            self.destination = (self.current_bar.x, self.current_bar.y)
            self.state = "moving_to_bar"
            self.current_toilet = None

    def goPee(self, toilets):
        if self.state in ["dancing", "at_bar"]:
            print(f"Listener {self.name} is going to pee (Urge: {self.urgeToPeeScore:.2f})")
            self.current_toilet = min(toilets, key=lambda toilet: math.dist((self.x, self.y), (toilet.x, toilet.y)))
            self.destination = (self.current_toilet.x, self.current_toilet.y)
            self.state = "moving_to_toilet"
            self.current_bar = None

    def return_to_scene(self):
        nearest_point = self.get_nearest_scene_point()
        self.destination = nearest_point
        self.state = "returning_to_scene"
        self.current_bar = None
        self.current_toilet = None

    def get_nearest_scene_point(self):
        points = [
            (self.scene.left, max(self.scene.top, min(self.y, self.scene.bottom))),
            (self.scene.right, max(self.scene.top, min(self.y, self.scene.bottom))),
            (max(self.scene.left, min(self.x, self.scene.right)), self.scene.top),
            (max(self.scene.left, min(self.x, self.scene.right)), self.scene.bottom)
        ]
        valid_points = [p for p in points if self.scene.collidepoint(*p)]
        if not valid_points:
            return self.get_valid_position(self.scene)
        return min(valid_points, key=lambda p: math.dist((self.x, self.y), p))
    
    def draw(self, surface):
        pygame.draw.circle(surface, (255, 0, 0), (int(self.x), int(self.y)), 5)

    def dance(self):
        new_x = self.x + self.speed * math.cos(self.direction)
        new_y = self.y + self.speed * math.sin(self.direction)
        if self.scene.collidepoint(new_x, new_y):
            self.x, self.y = new_x, new_y
        else:
            self.direction = random.uniform(0, 2 * math.pi)

    def move_to_destination(self):
        if self.destination:
            dx = self.destination[0] - self.x
            dy = self.destination[1] - self.y
            distance = math.sqrt(dx**2 + dy**2)
            if distance > self.move_speed:
                self.x += (dx / distance) * self.move_speed
                self.y += (dy / distance) * self.move_speed
            else:
                self.x, self.y = self.destination

    def reached_destination(self):
        if self.destination:
            return math.dist((self.x, self.y), self.destination) < self.move_speed
        return False

    def get_valid_position(self, scene):
        while True:
            x = random.uniform(scene.left, scene.right)
            y = random.uniform(scene.top, scene.bottom)
            if scene.collidepoint(x, y):
                return x, y


class BartenderAgent(Agent):
    def __init__(self, name):
        super().__init__(name)
        self.type = "Bartender"
        self.bar = None
        self.clientsToServe = []
        self.mailbox = Queue()

    def assignToBar(self, bar):
        self.bar = bar

    def takeOrder(self):
        print("Bartender " + self.name + " is taking an order")
        if self.bar and not self.bar.queue.empty():
            client = self.bar.removeFromQueue()
            self.clientsToServe.append(client)

    def serveDrink(self):
        print("Bartender " + self.name + " is serving a drink")
        if self.clientsToServe:
            client = self.clientsToServe.pop(0)
            print(f"Bartender {self.name} served a drink to {client.name}")

    def checkMessages(self):
        while not self.mailbox.empty():
            message = self.mailbox.get()
            print(f"Bartender {self.name} received message: {message}")
            if message.startswith("Moved"):
                _, _, _, _, x, y = message.split()
                new_x, new_y = int(x.rstrip(',')), int(y)
                self.moveToNewBar(new_x, new_y)
            elif message.startswith("Bartender"):
                _, _, _, _, x, y = message.split()
                new_x, new_y = int(x.rstrip(',')), int(y)
                for bar in self.bar.manager.bars:
                    if bar.x == new_x and bar.y == new_y:
                        self.moveToNewBar(bar)
                        break

    def moveToNewBar(self, new_bar):
        print(f"Bartender {self.name} is moving to new bar at ({new_bar.x}, {new_bar.y})")
        self.bar.removeStaff(self)
        self.bar = new_bar
        new_bar.addStaff(self)

class BarManager(Agent):
    def __init__(self, name, bars, message_manager):
        super().__init__(name)
        self.type = "BarManager"
        self.bars = bars
        self.mailbox = Queue()
        self.message_manager = message_manager

    def manageBar(self):
        print(f"BarManager {self.name} is managing the bars")
        for bar in self.bars:
            if not bar.bartenders:
                continue
            workload = bar.queue.qsize() / len(bar.bartenders)
            if workload > 2:  # Adjust this threshold as needed
                other_bars = [b for b in self.bars if b != bar and b.bartenders]
                if other_bars:
                    other_bar = min(other_bars, key=lambda b: b.queue.qsize() / len(b.bartenders))
                    if len(bar.bartenders) > 1:
                        bartender_to_move = bar.bartenders.pop()
                        bartender_to_move.moveToNewBar(other_bar)
                        message = f"Moved {bartender_to_move.name}"
                        self.message_manager.add_message(message, (bar.x, bar.y - 20))
                        self.sendMessage(bartender_to_move, message)
                        print(f"Moved {bartender_to_move.name} from bar at ({bar.x}, {bar.y}) to bar at ({other_bar.x}, {other_bar.y})")

    def sendMessage(self, bartender, message):
        bartender.mailbox.put(message)

class AgentFactory:
    def createAgent(self, name, type, scene=None, bars=None, message_manager=None):
        if type == "Listener":
            return ListenerAgent(name, scene)
        elif type == "Bartender":
            return BartenderAgent(name)
        elif type == "BarManager":
            return BarManager(name, bars, message_manager)
        else:
            return None