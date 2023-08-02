import pygame
import cv2
import numpy as np
from collections import deque
import argparse
from color_identification import hsv_color_range
from imutils.video import WebcamVideoStream
from imutils.video import FPS
import imutils

pygame.init()

# Basic parameters of the screen
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong, close the window or press esc to end the game")

clock = pygame.time.Clock()

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
        self.striker_rect = pygame.Rect(posx, posy, width, height)

    @property
    def posy(self):
        return self._posy

    @posy.setter
    def posy(self, value):
        self._posy = max(0, min(value, HEIGHT - self.height))
        self.striker_rect.y = self._posy

    def display(self):
        pygame.draw.rect(screen, self.color, self.striker_rect)

    def update(self, y_fac):
        self.posy += self.speed * y_fac

    def display_score(self, text, score, x, y, color):
        text = font20.render(text + str(score), True, color)
        text_rect = text.get_rect(center=(x, y))
        screen.blit(text, text_rect)

    def get_rect(self):
        return self.striker_rect


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


## this method updates the position of striker based on ball's position


def AI_controller(ball, striker):
    y_fac = 0
    buffer_distance = 10
    if ball.posy > striker.posy and abs(ball.posy - striker.posy) > buffer_distance:
        y_fac = 1
    elif ball.posy < striker.posy and abs(ball.posy - striker.posy) > buffer_distance:
        y_fac = -1

    return y_fac


## this method is an advanced from the first one. Calculate the distance of balls and the striker and focus on the ball that nearer the striker
## balls class and striker class


def AI_controller_2balls(ball1, ball2, striker):
    y_fac = 0
    buffer_distance = 10
    ball1_arr = np.array((ball1.posx, ball1.posy))
    ball2_arr = np.array((ball2.posx, ball2.posy))
    striker_arr = np.array((striker._posx, striker._posy))
    dist_striker_ball1 = np.linalg.norm(striker_arr - ball1_arr)
    dist_striker_ball2 = np.linalg.norm(striker_arr - ball2_arr)
    if dist_striker_ball1 > dist_striker_ball2:
        if (
            ball2.posy > striker.posy
            and abs(ball2.posy - striker.posy) > buffer_distance
        ):
            y_fac = 1
        elif (
            ball2.posy < striker.posy
            and abs(ball2.posy - striker.posy) > buffer_distance
        ):
            y_fac = -1

    elif dist_striker_ball1 < dist_striker_ball2:
        if (
            ball1.posy > striker.posy
            and abs(ball1.posy - striker.posy) > buffer_distance
        ):
            y_fac = 1
        elif (
            ball1.posy < striker.posy
            and abs(ball1.posy - striker.posy) > buffer_distance
        ):
            y_fac = -1
    else:
        y_fac = 0

    return y_fac


## use openCV packages to identify particular colour
## input: frame, colour range, output: detected the area size and number of the detected contour
def color_track(img, lower_range, upper_range):
    min_area = 600
    num_cnt = 0
    area = 0
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_range, upper_range)
    _, mask1 = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
    cnts, _ = cv2.findContours(mask1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    OutArea = [cv2.contourArea(c) for c in cnts if cv2.contourArea(c) > min_area]
    num_cnt = len(OutArea)
    area = sum(OutArea)

    return num_cnt, area


def camera_controller_no_baseline(track1, track2):
    y_fac = max(-1, min(1, track2 - track1))
    return [y_fac]


def camera_controller_baseline(track1, track2, track1_init, track2_init):
    avg_track_list = [0, 0]
    pts.appendleft((int(track1), int(track2)))
    avg_track_list = np.nanmean(pts, axis=0)
    y_fac = max(-1, min(1, avg_track_list[0] - track1_init))
    y_fac1 = max(-1, min(1, avg_track_list[1] - track2_init))
    return [y_fac, y_fac1]


def main(game_modes):
    running = True
    counter = 0
    strikerL = Striker(20, 0, 10, 100, 10, GREEN)
    strikerR = Striker(WIDTH - 30, 0, 10, 100, 10, GREEN)
    ball = Ball(WIDTH // 2, HEIGHT // 2, 7, 4, WHITE)
    ball2 = Ball(WIDTH // 2, HEIGHT // 2, 7, 5, RED) if game_modes.two_balls else None

    if game_modes.multi_threaded_video_stream:
        cap = WebcamVideoStream(src=0).start()
        fps = FPS().start()
        pygame_fps = 60
        ## you need to manually test this program under demo mode to see how fast multiple threading speeds up the programme.
        ## And set a reasonable fps for the pygame update rate
    elif game_modes.play_with_camera:
        cap = cv2.VideoCapture(0)
        camera_fps = cap.get(cv2.CAP_PROP_FPS)
        pygame_fps = camera_fps
    else:
        pygame_fps = 30

    if game_modes.update_color_range and game_modes.play_with_camera:
        print(
            "[INFO] colour identification: use mouse cursor to adjust lower and upper bound of the threshold to isolate color spectrum. Isolated color will be shown as white in the Mask window. Press Q to return the result and leave this procedure"
        )
        lower_blue, upper_blue = hsv_color_range()
        print(f"[INFO] Colour 1 is in between {lower_blue} and {upper_blue}")
        lower_red, upper_red = hsv_color_range()
        print(f"[INFO] Colour 2 is in between {lower_red} and {upper_red}")
        lower_ranges = [np.array(lower_blue), np.array(lower_red)]
        upper_ranges = [np.array(upper_blue), np.array(upper_red)]
        print(f"[INFO] Complete updating the colour thresholds")
    else:
        ## setting for logitech webcam
        lower_ranges = [np.array([90, 31, 229]), np.array([0, 62, 78])]
        upper_ranges = [np.array([179, 255, 255]), np.array([91, 255, 255])]
        ## setting for build-in webcam
        # lower_ranges = [np.array([72, 98, 64]), np.array([129, 106, 62])]
        # upper_ranges = [np.array([131, 255, 255]), np.array([179, 255, 255])]
        print(
            f"[INFO] Use default colour thresholds. The first colour range is for blue and the second one is for red"
        )

    list_of_strikers = [strikerL, strikerR]
    strikerL_score, strikerR_score = 0, 0
    strikerL_y_fac, strikerR_y_fac = 0, 0
    area1_init = 0
    area2_init = 0
    while running:
        screen.fill(BLACK)
        if game_modes.demo_mode:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            if game_modes.two_balls:
                strikerL_y_fac = AI_controller_2balls(ball, ball2, strikerL)
                strikerR_y_fac = AI_controller_2balls(ball, ball2, strikerR)
            else:
                strikerL_y_fac = AI_controller(ball, strikerL)
                strikerR_y_fac = AI_controller(ball, strikerR)

        elif game_modes.play_with_camera:
            # initiate video capture with either openCV or imutils
            if game_modes.multi_threaded_video_stream:
                frame = cap.read()
                frame = imutils.resize(frame, width=480, height=640)
            else:
                ret, frame = cap.read()
                if not ret:
                    running = False
                    break
                frame = cv2.resize(frame, (640, 480))

            # do colour tracking here
            num_1, area_1 = color_track(frame, lower_ranges[0], upper_ranges[0])
            num_2, area_2 = color_track(frame, lower_ranges[1], upper_ranges[1])
            # do save initial value of area size or whatever you want to compare
            if counter == 0:
                area1_init = area_1
                area2_init = area_2

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            # entering controlling striker section
            if game_modes.single_player == True:
                if game_modes.use_baseline_value == True:
                    y_list = camera_controller_baseline(
                        area_1, area_2, area1_init, area2_init
                    )
                else:
                    y_list = camera_controller_no_baseline(area_1, area_2)

                strikerR_y_fac = y_list[0]
                # AI PC
                if game_modes.two_balls:
                    strikerL_y_fac = AI_controller_2balls(ball, ball2, strikerL)
                else:
                    strikerL_y_fac = AI_controller(ball, strikerL)
            else:
                if game_modes.use_baseline_value == True:
                    y_list = camera_controller_baseline(
                        area_1, area_2, area1_init, area2_init
                    )
                else:
                    y_list = camera_controller_no_baseline(area_1, area_2)

                strikerR_y_fac = y_list[0]
                if len(y_list) > 1:
                    strikerL_y_fac = y_list[1]
        else:
            if game_modes.single_player == True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                    y_list = keyboard_controller(event, pygame)
                    strikerR_y_fac = y_list[0]
                if game_modes.two_balls:
                    strikerL_y_fac = AI_controller_2balls(ball, ball2, strikerL)
                else:
                    strikerL_y_fac = AI_controller(ball, strikerL)
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                    ## there is a bug  in the pygame that when wrapping up in a function, some key press was prioritised by others
                    y_list = keyboard_controller(event, pygame)
                    strikerR_y_fac = y_list[0]
                    strikerL_y_fac = y_list[1]

        ##update the position of the paddles
        strikerR.update(strikerR_y_fac)
        strikerL.update(strikerL_y_fac)
        counter += 1
        ##collide rules of balls
        for striker in list_of_strikers:
            if pygame.Rect.colliderect(ball.get_rect(), striker.get_rect()):
                ball.hit()
            if game_modes.two_balls and pygame.Rect.colliderect(
                ball2.get_rect(), striker.get_rect()
            ):
                ball2.hit()

        ##update the position of the balls
        point1 = ball.update()
        point2 = ball2.update() if game_modes.two_balls else None

        if point1 == -1:
            strikerR_score += 1
        elif point1 == 1:
            strikerL_score += 1

        if game_modes.two_balls and point2:
            if point2 == -1:
                strikerR_score += 1
            elif point2 == 1:
                strikerL_score += 1

        if point1:
            ball.reset()
        if game_modes.two_balls and point2:
            ball2.reset()

        strikerL.display()
        strikerR.display()
        ball.display()
        if game_modes.two_balls:
            ball2.display()

        strikerL.display_score("Konstanz Gamer : ", strikerL_score, 100, 20, WHITE)
        strikerR.display_score(
            "Collective Power : ", strikerR_score, WIDTH - 100, 20, WHITE
        )

        pygame.display.update()
        clock.tick(pygame_fps)
        if game_modes.multi_threaded_video_stream:
            fps.update()
    if game_modes.multi_threaded_video_stream:
        fps.stop()
        cv2.destroyAllWindows()
        cap.stop()
        print(
            "[INFO] Approx. FPS: {:.2f} under multi-threading method. Can use this value to speed up the pygame update rate".format(
                fps.fps()
            )
        )


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-b",
        "--two_balls",
        type=bool,
        default=True,
        help="Whether to use two ball or not. If false, one ball is used",
    )
    ap.add_argument(
        "-p",
        "--single_player",
        type=bool,
        default=True,
        help="Whether having single player in the game or not. If false, two players join",
    )
    ap.add_argument(
        "-c",
        "--play_with_camera",
        type=bool,
        default=False,
        help="Whether to control striker with camera or not. If false, keyboard up and down are used",
    )
    ap.add_argument(
        "-d",
        "--demo_mode",
        type=bool,
        default=False,
        help="Whether to watch two AI play in the demo mode or not. If false, initiates the play mode",
    )
    ap.add_argument(
        "-u",
        "--update_color_range",
        type=bool,
        default=False,
        help="Whether to update colour range for video tracking or not. If false, defaults values to track blue and red are used",
    )
    ap.add_argument(
        "-m",
        "--multi_threaded_video_stream",
        type=bool,
        default=False,
        help="Use imutil package to speed up video stream. If false, default setting use openCV VideoCapture",
    )
    ap.add_argument(
        "-v",
        "--use_baseline_value",
        type=bool,
        default=False,
        help="Use calculating striker movement based on baseline value from the first frame",
    )
    game_modes = ap.parse_args()
    main(game_modes)
    pygame.quit()
