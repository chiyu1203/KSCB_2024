import pygame

pygame.init()

# Font that is used to render the text
font20 = pygame.font.Font("freesansbold.ttf", 20)

# RGB values of standard colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Basic parameters of the screen
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

clock = pygame.time.Clock()
FPS = 30

# Striker class


class Striker:
    # Take the initial position, dimensions, speed and color of the object
    def __init__(self, posx, posy, width, height, speed, color):
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        self.speed = speed
        self.color = color
        # Rect that is used to control the position and collision of the object
        self.geekRect = pygame.Rect(posx, posy, width, height)
        # Object that is blit on the screen
        self.geek = pygame.draw.rect(screen, self.color, self.geekRect)

    # Used to display the object on the screen
    def display(self):
        self.geek = pygame.draw.rect(screen, self.color, self.geekRect)

    def update(self, yFac):
        self.posy = self.posy + self.speed * yFac

        # Restricting the striker to be below the top surface of the screen
        if self.posy <= 0:
            self.posy = 0
        # Restricting the striker to be above the bottom surface of the screen
        elif self.posy + self.height >= HEIGHT:
            self.posy = HEIGHT - self.height

        # Updating the rect with the new values
        self.geekRect = (self.posx, self.posy, self.width, self.height)

    def displayScore(self, text, score, x, y, color):
        text = font20.render(text + str(score), True, color)
        textRect = text.get_rect()
        textRect.center = (x, y)

        screen.blit(text, textRect)

    def getRect(self):
        return self.geekRect


# Ball class


class Ball:
    def __init__(self, posx, posy, radius, speed, color):
        self.posx = posx
        self.posy = posy
        self.radius = radius
        self.speed = speed
        self.color = color
        self.xFac = 1
        self.yFac = -1
        self.ball = pygame.draw.circle(
            screen, self.color, (self.posx, self.posy), self.radius
        )
        self.firstTime = 1

    def display(self):
        self.ball = pygame.draw.circle(
            screen, self.color, (self.posx, self.posy), self.radius
        )

    def update(self):
        self.posx += self.speed * self.xFac
        self.posy += self.speed * self.yFac

        # If the ball hits the top or bottom surfaces,
        # then the sign of yFac is changed and
        # it results in a reflection
        if self.posy <= 0 or self.posy >= HEIGHT:
            self.yFac *= -1

        if self.posx <= 0 and self.firstTime:
            self.firstTime = 0
            return 1
        elif self.posx >= WIDTH and self.firstTime:
            self.firstTime = 0
            return -1
        else:
            return 0

    def reset(self):
        self.posx = WIDTH // 2
        self.posy = HEIGHT // 2
        self.xFac *= -1
        self.firstTime = 1

    # Used to reflect the ball along the X-axis
    def hit(self):
        self.xFac *= -1

    def getRect(self):
        return self.ball


# Game Manager


def main():
    running = True
    use_ball2 = True

    # Defining the objects
    geek1 = Striker(20, 0, 10, 100, 10, GREEN)
    geek2 = Striker(WIDTH - 30, 0, 10, 100, 10, GREEN)
    ball = Ball(WIDTH // 2, HEIGHT // 2, 7, 7, WHITE)
    ball2 = Ball(WIDTH // 2, HEIGHT // 2, 7, 10, RED)

    listOfGeeks = [geek1, geek2]

    # Initial parameters of the players
    geek1Score, geek2Score = 0, 0
    geek1YFac, geek2YFac = 0, 0

    while running:
        screen.fill(BLACK)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    geek2YFac = -1
                if event.key == pygame.K_DOWN:
                    geek2YFac = 1
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    geek2YFac = 0

        # Collision detection
        for geek in listOfGeeks:
            if pygame.Rect.colliderect(ball.getRect(), geek.getRect()):
                ball.hit()
            if use_ball2 == True:
                if pygame.Rect.colliderect(ball2.getRect(), geek.getRect()):
                    ball2.hit()

        # Updating the objects

        # -1 -> Geek_1 has scored
        # +1 -> Geek_2 has scored
        # 0 -> None of them scored

        ##AI PC
        if ball.posy > geek1.posy and abs(ball.posy - geek1.posy) > 10:
            geek1YFac = 1
            # print(ball.posy, geek1.posy)
        if ball.posy < geek1.posy and abs(ball.posy - geek1.posy) > 10:
            geek1YFac = -1

        if use_ball2 == True:
            if ball2.posy > geek1.posy and abs(ball2.posy - geek1.posy) > 10:
                geek1YFac = 1
            if ball2.posy < geek1.posy and abs(ball2.posy - geek1.posy) > 10:
                geek1YFac = -1

        geek1.update(geek1YFac)
        geek2.update(geek2YFac)
        point = ball.update()
        point = ball2.update()

        if point == -1:
            geek1Score += 1
        elif point == 1:
            geek2Score += 1

        if point:
            ball.reset()
            ball2.reset()

        # Someone has scored
        # a point and the ball is out of bounds.
        # So, we reset it's position
        # if point == 1 and ball.posx <= 0:
        #     ball.reset()
        # elif point == -1 and ball.posx >= WIDTH:
        #     ball.reset()
        # if point == 1 and ball2.posx <= 0:
        #     ball2.reset()
        # elif point == -1 and ball2.posx >= WIDTH:
        #     ball2.reset()

        # Displaying the objects on the screen
        geek1.display()
        geek2.display()
        ball.display()
        ball2.display()

        # Displaying the scores of the players
        geek1.displayScore("Konstanz Gamer : ", geek1Score, 100, 20, WHITE)
        geek2.displayScore("Collective Power : ", geek2Score, WIDTH - 100, 20, WHITE)

        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
    pygame.quit()
