import pygame

class OnScreenMessage:
    def __init__(self, text, position, duration=3000):  # duration in milliseconds
        self.text = text
        self.position = position
        self.creation_time = pygame.time.get_ticks()
        self.duration = duration

    def should_remove(self):
        return pygame.time.get_ticks() - self.creation_time > self.duration

class MessageManager:
    def __init__(self):
        self.messages = []
        self.font = pygame.font.Font(None, 24)  # You can specify a font file instead of None

    def add_message(self, text, position):
        self.messages.append(OnScreenMessage(text, position))

    def update(self):
        self.messages = [msg for msg in self.messages if not msg.should_remove()]

    def draw(self, surface):
        for msg in self.messages:
            text_surface = self.font.render(msg.text, True, (255, 255, 255))  # White text
            surface.blit(text_surface, msg.position)
