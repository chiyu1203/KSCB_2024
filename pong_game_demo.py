import pygame
import cv2
import numpy as np
from collections import deque
from track_chatGPT import color_check

update_color_config = False
if update_color_config:
    lower_blue, upper_blue = color_check()
    print(lower_blue, upper_blue)
    lower_red, upper_red = color_check()
    print(lower_red, upper_red)
    lower_ranges = [np.array(lower_blue), np.array(lower_red)]
    upper_ranges = [np.array(upper_blue), np.array(upper_red)]
else:
    lower_ranges = [np.array([96, 91, 83]), np.array([0, 80, 0])]
    upper_ranges = [np.array([158, 255, 179]), np.array([78, 255, 179])]

# print(lower_ranges, upper_ranges)
cap = cv2.VideoCapture(0)
pygame.init()

# Basic parameters of the screen
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

clock = pygame.time.Clock()
FPS = 60

# Colors
BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255, 255, 255)
GREEN = pygame.Color(0, 255, 0)
RED = pygame.Color(255, 0, 0)

# Font that is used to render the text
font20 = pygame.font.Font("freesansbold.ttf", 20)

pts = deque(maxlen=10)



class Striker:
    def __init__(self, posx, posy, width, height, speed, color):
        self._posx = posx
        self._posy = posy
        self.width = width
        self.height = height
        self.speed = speed
        self.color = color
        self.geek_rect = pygame.Rect(posx, posy, width, height)

    @property
    def posy(self):
        return self._posy

    @posy.setter
    def posy(self, value):
        self._posy = max(0, min(value, HEIGHT - self.height))
        self.geek_rect.y = self._posy

    def display(self):
        pygame.draw.rect(screen, self.color, self.geek_rect)

    def update(self, y_fac):
        self.posy += self.speed * y_fac

    def display_score(self, text, score, x, y, color):
        text = font20.render(text + str(score), True, color)
        text_rect = text.get_rect(center=(x, y))
        screen.blit(text, text_rect)

    def get_rect(self):
        return self.geek_rect


class Ball:
    def __init__(self, posx, posy, radius, speed, color):
        self.posx = posx
        self.posy = posy
        self.radius = radius
        self.speed = speed
        self.color = color
        self.x_fac = 1
        self.y_fac = -1
        self.ball = pygame.draw.circle(
            screen, self.color, (self.posx, self.posy), self.radius
        )
        self.first_time = True

    def display(self):
        self.ball = pygame.draw.circle(
            screen, self.color, (self.posx, self.posy), self.radius
        )

    def update(self):
        self.posx += self.speed * self.x_fac
        self.posy += self.speed * self.y_fac

        if self.posy <= 0 or self.posy >= HEIGHT:
            self.y_fac *= -1

        if self.posx <= 0 and self.first_time:
            self.first_time = False
            return -1
        elif self.posx >= WIDTH and self.first_time:
            self.first_time = False
            return 1
        else:
            return 0

    def reset(self):
        self.posx = WIDTH // 2
        self.posy = HEIGHT // 2
        self.x_fac *= -1
        self.first_time = True

    def hit(self):
        self.x_fac *= -1

    def get_rect(self):
        return self.ball


def keyboard_controller(event, pygame):
    y_fac, y_fac1 = 0, 0
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            y_fac = -1
        if event.key == pygame.K_DOWN:
            y_fac = 1
        if event.key == pygame.K_LEFT:
            y_fac1 = -1
        if event.key == pygame.K_RIGHT:
            y_fac1 = 1
    if event.type == pygame.KEYUP:
        if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
            y_fac = 0
        if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
            y_fac1 = 0
    return [y_fac, y_fac1]


def camera_controller(track1, track2):
    y_fac = max(-1, min(1, track2 - track1))
    return y_fac


def camera_controller2(track1, track2, track1_init, track2_init, counter):
    avg_track_list = [0, 0]
    pts.appendleft((int(track1), int(track2)))
    for i in np.arange(1, len(pts)):
        if pts[i - 1] is None or pts[i] is None:
            continue
        # check to see if enough points have been accumulated in
        # the buffer
        if counter >= 10 and i == 1 and pts[-10] is not None:
            avg_track_list = np.mean(pts, axis=0)
    # if avg_track_list[0] > track1_init:
    #     y_fac = 1
    # elif avg_track_list[0] < track1_init:
    #     y_fac = -1
    # else:
    #     y_fac = 0

    # if avg_track_list[1] > track2_init:
    #     y_fac1 = 1
    # elif avg_track_list[1] < track2_init:
    #     y_fac1 = -1
    # else:
    #     y_fac1 = 0
    y_fac = max(-1, min(1, avg_track_list[0] - track1_init))
    y_fac1 = max(-1, min(1, avg_track_list[1] - track2_init))
    return [y_fac, y_fac1]


def AI_controller(ball, geek):
    y_fac = 0
    if ball.posy > geek.posy and abs(ball.posy - geek.posy) > 10:
        y_fac = 1
    elif ball.posy < geek.posy and abs(ball.posy - geek.posy) > 10:
        y_fac = -1

    return y_fac


def AI_controller2(ball1, ball2, geek):
    y_fac = 0
    ball1_arr = np.array((ball1.posx, ball1.posy))
    ball2_arr = np.array((ball2.posx, ball2.posy))
    geek_arr = np.array((geek._posx, geek._posy))
    dist_geek_1 = np.linalg.norm(geek_arr - ball1_arr)
    dist_geek_2 = np.linalg.norm(geek_arr - ball2_arr)
    if dist_geek_1 > dist_geek_2:
        if ball2.posy > geek.posy and abs(ball2.posy - geek.posy) > 10:
            y_fac = 1
        elif ball2.posy < geek.posy and abs(ball2.posy - geek.posy) > 10:
            y_fac = -1

    elif dist_geek_1 < dist_geek_2:
        if ball1.posy > geek.posy and abs(ball1.posy - geek.posy) > 10:
            y_fac = 1
        elif ball1.posy < geek.posy and abs(ball1.posy - geek.posy) > 10:
            y_fac = -1
    else:
        y_fac = 0

    return y_fac


def color_track(img, lower_range, upper_range):
    num_cnt = 0
    area = 0
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_range, upper_range)
    _, mask1 = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
    cnts, _ = cv2.findContours(mask1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for c in cnts:
        x = 600
        if cv2.contourArea(c) > x:
            area += cv2.contourArea(c)
            num_cnt += 1
    return num_cnt, area


def main(game_modes):
    running = True
    counter = 0
    geek1 = Striker(20, 0, 10, 100, 10, GREEN)
    geek2 = Striker(WIDTH - 30, 0, 10, 100, 10, GREEN)
    ball = Ball(WIDTH // 2, HEIGHT // 2, 7, 3.5, WHITE)
    ball2 = (
        Ball(WIDTH // 2, HEIGHT // 2, 7, 5, RED)
        if game_modes.get("two_balls")
        else None
    )

    list_of_geeks = [geek1, geek2]
    geek1_score, geek2_score = 0, 0
    geek1_y_fac, geek2_y_fac = 0, 0
    area1_init = 0
    area2_init = 0
    while running:
        screen.fill(BLACK)
        if game_modes.get("demo_mode"):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            if game_modes.get("two_balls"):
                geek1_y_fac = AI_controller2(ball, ball2, geek1)
                geek2_y_fac = AI_controller2(ball, ball2, geek2)
            else:
                geek1_y_fac = AI_controller(ball, geek1)
                geek2_y_fac = AI_controller(ball, geek2)

        else:
            if game_modes.get("play_with_camera"):
                ret, frame = cap.read()
                if not ret:
                    running = False
                    break
                frame = cv2.resize(frame, (640, 480))
                num_1, area_1 = color_track(frame, lower_ranges[0], upper_ranges[0])
                num_2, area_2 = color_track(frame, lower_ranges[1], upper_ranges[1])
                if counter == 0:
                    area1_init = area_1
                    area2_init = area_2
                if game_modes.get("one_player") == True:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                running = False

                    geek2_y_fac = camera_controller(num_1, num_2)
                    # AI PC
                    if game_modes.get("two_balls"):
                        geek1_y_fac = AI_controller2(ball, ball2, geek1)
                    else:
                        geek1_y_fac = AI_controller(ball, geek1)
                else:
                    print("enjoy two players with the camera")
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                running = False
                    y_list = camera_controller2(
                        area_1, area_2, area1_init, area2_init, counter
                    )

                    geek2_y_fac = y_list[0]
                    geek1_y_fac = y_list[1]
            else:
                if game_modes.get("one_player") == True:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                running = False
                        y_list = keyboard_controller(event, pygame)
                        geek2_y_fac = y_list[0]
                    if game_modes.get("two_balls"):
                        geek1_y_fac = AI_controller2(ball, ball2, geek1)
                    else:
                        geek1_y_fac = AI_controller(ball, geek1)
                else:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                running = False
                        ## there is a bug  in the pygame that when wrapping up in a function, some key press was prioritised by others
                        y_list = keyboard_controller(event, pygame)
                        geek2_y_fac = y_list[0]
                        geek1_y_fac = y_list[1]

        ##update the position of the paddles
        geek2.update(geek2_y_fac)
        geek1.update(geek1_y_fac)
        counter +=1
        ##collide rules of balls
        for geek in list_of_geeks:
            if pygame.Rect.colliderect(ball.get_rect(), geek.get_rect()):
                ball.hit()
            if game_modes.get("two_balls") and pygame.Rect.colliderect(
                ball2.get_rect(), geek.get_rect()
            ):
                ball2.hit()

        ##update the position of the balls
        point1 = ball.update()
        point2 = ball2.update() if game_modes.get("two_balls") else None

        if point1 == -1:
            geek2_score += 1
        elif point1 == 1:
            geek1_score += 1

        if game_modes.get("two_balls") and point2:
            if point2 == -1:
                geek2_score += 1
            elif point2 == 1:
                geek1_score += 1

        if point1:
            ball.reset()
        if game_modes.get("two_balls") and point2:
            ball2.reset()

        geek1.display()
        geek2.display()
        ball.display()
        if game_modes.get("two_balls"):
            ball2.display()

        geek1.display_score("Konstanz Gamer : ", geek1_score, 100, 20, WHITE)
        geek2.display_score("Collective Power : ", geek2_score, WIDTH - 100, 20, WHITE)

        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    game_modes = {
        "two_balls": False,
        "one_player": True,
        "play_with_camera": True,
        "demo_mode": False,
    }
    main(game_modes)
    pygame.quit()
