import random
# custom imports
from message import MessageManager
from model import AgentFactory, Bar, BartenderAgent, ListenerAgent, Toilets, Scene, BarManager
# libraries imports
import pygame
from pygame.locals import *
import faker

# Constants
WIDTH, HEIGHT = 1280, 720
FPS = 30    
WHITE = (255, 255, 255)

def place_bars(num_bars, scene, toilets):
    bars = []
    for _ in range(num_bars):
        while True:
            x = random.randint(0, WIDTH - 50)
            y = random.randint(0, HEIGHT - 50)
            if not (scene.collidepoint(x, y) or any(toilet.collidepoint(x, y) for toilet in toilets)):
                bars.append(Bar(x, y, None, []))
                break
    return bars

def populateAgents(numberOfListener, numberOfBartender, scene, bars):
    factory = AgentFactory()
    listenerAgents = []
    bartenderAgents = []
    for _ in range(numberOfListener):
        listenerAgents.append(factory.createAgent(faker.Faker().name(), "Listener", scene))
    for _ in range(numberOfBartender):
        bartender = factory.createAgent(faker.Faker().name(), "Bartender")
        bar = random.choice(bars)
        bartender.assignToBar(bar)
        bar.addStaff(bartender)
        bartenderAgents.append(bartender)
    return listenerAgents, bartenderAgents

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    running = True
    message_manager = MessageManager()

    toilets = [
        Toilets(0, (HEIGHT // 2) - 30),
        Toilets(WIDTH - 30, (HEIGHT // 2) - 30),
        Toilets((WIDTH // 2), HEIGHT - 30),
    ]

    scene = Scene((WIDTH // 2) - 300, 0)

    bars = place_bars(2, scene, toilets)

    bar_manager = AgentFactory().createAgent("Manager", "BarManager", bars=bars, message_manager=message_manager)
    for bar in bars:
        bar.manager = bar_manager

    listeners, bartenders = populateAgents(200, 2, scene, bars)
    
    all_agents = listeners + bartenders + [bar_manager]

    # #print all bars for debugging
    # for bar in bars:
    #     print(bar)

    # # print all bartenders for debugging
    # for bartender in bartenders:
    #     print(bartender.name, bartender.bar)


    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Update bars and toilets
        for bar in bars:
            bar.update()
        for toilet in toilets:
            toilet.update()

        # Update agents
        for agent in all_agents:
            if isinstance(agent, ListenerAgent):
                agent.update(bars, toilets)
            elif isinstance(agent, BartenderAgent):
                agent.takeOrder()
                agent.serveDrink()
                agent.checkMessages()
            elif isinstance(agent, BarManager):
                agent.manageBar()
        message_manager.update()
        # Drawing
        screen.fill(WHITE)
        scene.draw(screen)
        for bar in bars:
            bar.draw(screen)
        for toilet in toilets:
            toilet.draw(screen)
        for agent in all_agents:
            if hasattr(agent, 'draw'):
                agent.draw(screen)
        message_manager.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()