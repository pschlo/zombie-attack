import pygame
import random
import math


class Game:
    WIN_WIDTH = 1500
    WIN_HEIGHT = 800
    FPS = 30

    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        pygame.mouse.set_visible(False)
        self.win = pygame.display.set_mode((type(self).WIN_WIDTH, type(self).WIN_HEIGHT))
        pygame.display.set_caption("Zombie Attack")

        self.img_background = pygame.image.load('background_2.png')
        self.width = type(self).WIN_WIDTH
        self.height = type(self).WIN_HEIGHT
        self.score = None
        self.num_zombies = 5

        self.spieler = Fadenkreuz(self)
        self.zombies = pygame.sprite.Group()
        self.base = Base()

        font = pygame.font.SysFont('arial', 40)
        self.text_1 = font.render("Der Präsident wurde von Zombies in Stücke gerissen.", True, (0, 0, 0))
        self.text_2 = font.render("Du hast versagt.", True, (0, 0, 0))

    def run(self):
        run = True
        self.score = Text(self, "Score")
        clock = pygame.time.Clock()
        dead = False

        while run:
            clock.tick(60)
            self.win.blit(self.img_background, (0, 0))
            # pygame.draw.rect(self.win, (0, 0, 255), base.rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    run = False
                if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
                    self.spieler.shoot()
                    for zombie in self.zombies:
                        if zombie.check_hit(pygame.mouse.get_pos()):
                            self.score.add(1)
                            break
            # keys = pygame.key.get_pressed()

            if len(self.zombies) == 0 and not dead:
                # print("empty")
                for i in range(self.num_zombies):
                    self.zombies.add(Zombie(self))
                self.num_zombies += 5
            for zombie in self.zombies:
                if pygame.sprite.collide_circle(zombie, self.base):
                    self.zombies.empty()
                    dead = True
            self.zombies.update()
            self.zombies.draw(self.win)
            self.spieler.draw()
            self.score.draw()
            if dead:
                self.death_screen()
            pygame.display.update()

    def death_screen(self):
        self.win.blit(self.text_1, (0, 100))
        self.win.blit(self.text_2, (0, 150))


class Fadenkreuz:
    img_fadenkreuz = pygame.image.load('fadenkreuz_2.png')

    def __init__(self, game):
        self.game = game

        self.sound_shot = pygame.mixer.Sound('shot_edit.wav')
        self.surface = type(self).img_fadenkreuz
        self.surface = pygame.transform.scale(self.surface, (300, 300))
        self.rect = self.surface.get_rect()
        self.shoot_anim_count = 0
        game.win.blit(self.surface, (0, 0))

    def draw(self):
        pos = pygame.mouse.get_pos()
        if self.shoot_anim_count:
            shift = 10 * self.shoot_anim_count - self.shoot_anim_count ** 2
            surf_new = pygame.transform.scale(self.surface, (self.rect.width - shift, self.rect.height - shift))
            surface = surf_new
            rect = surf_new.get_rect()
            if self.shoot_anim_count < 10:
                self.shoot_anim_count += 1
            else:
                self.shoot_anim_count = 0
        else:
            rect = self.rect
            surface = self.surface
        rect.center = pos
        self.game.win.blit(surface, rect)

    def shoot(self):
        self.sound_shot.play()
        self.shoot_anim_count = 1


class Zombie(pygame.sprite.Sprite):
    img_zombie = pygame.image.load('zombie_2.png')

    def __init__(self, game):
        super().__init__()
        self.game = game

        self.image = type(self).img_zombie
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        # self.hitbox = pygame.Rect((self.rect.x, self.rect.y)
        # self.rect.width /= 2
        # pygame.draw.rect(self.image, pygame.Color('red'), self.rect, 1)
        self.rect.x = random.randint(0, self.game.width)
        self.rect.y = random.randint(int(-self.game.height * (1 / 10)), 0)
        self.radius = 1

    def update(self):
        # print("moin")
        aim_x = self.game.base.rect.center[0]
        aim_y = self.game.base.rect.center[1]
        # Einheitsvektoren bilden
        d_x = (aim_x - self.rect.x)
        d_y = (aim_y - self.rect.y)
        # print(d_x, d_y)
        length = (d_x ** 2 + d_y ** 2) ** 0.5
        if length > 0:
            d_x = d_x / length
            d_y = d_y / length
            # print("old:", d_x, d_y)
            if d_x < 0:
                d_x = math.floor(d_x) if abs(math.modf(d_x)[0]) > random.random() else math.ceil(d_x)
            else:
                d_x = math.floor(d_x) if abs(math.modf(d_x)[0]) < random.random() else math.ceil(d_x)

            if d_y < 0:
                d_y = math.floor(d_y) if abs(math.modf(d_y)[0]) > random.random() else math.ceil(d_y)
            else:
                d_y = math.floor(d_y) if abs(math.modf(d_y)[0]) < random.random() else math.ceil(d_y)
            # d_x = int(d_x) - 1 if d_x % 1 >= random.random() else int(d_x)
            # d_y = int(d_y) - 1 if d_y % 1 >= random.random() else int(d_y)
        # print("new:", d_x, d_y)
        # print()
        # d_x = (WIN_WIDTH / 2 - self.x_orig) / 200
        # d_y = (WIN_HEIGHT - self.y_orig) / 200
        self.rect.move_ip(d_x, d_y)

    def check_hit(self, mouse):
        if self.rect.collidepoint(mouse):
            # print("hit!")
            self.kill()
            return True
        return False


class Base(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.rect = pygame.Rect((642, 537), (196, 196))
        self.radius = 98


class Text:
    def __init__(self, game, title, score=0):
        self.game = game
        self.score = score
        self.title = title
        self.font = pygame.font.SysFont('arial', 30)
        self.text = None
        self.render()

    def add(self, a):
        self.score += a
        self.render()

    def render(self):
        self.text = self.font.render("%s: %d" % (self.title, self.score), True, (0, 0, 0))

    def draw(self):
        self.game.win.blit(self.text, (0, 0))


if __name__ == "__main__":
    game = Game()
    game.run()
