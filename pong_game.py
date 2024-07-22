import pygame
import json
import cv2
import numpy as np
import argparse
import imutils
from imutils.video import WebcamVideoStream
from imutils.video import FPS
from color_identification import hsv_color_range
from collections import deque
from pathlib import Path

'''
In total, there are 3 modes in this game, PC vs. PC (observer_mode), Player vs. PC (single_player), Player vs. Player and different way of controlling the strikers.
To enter a specific mode, you need to give the argument in the Terminal or Cmd when calling the game.
For example, 
entering observer mode to watch PC vs. PC
python pong_game.py -o

entering observer mode to watch PC vs. PC hitting two balls
python pong_game.py -o -b

entering single-player mode and control the striker with keyboard
python pong_game.py -s

entering single-player mode and control the striker with computer vision
python pong_game.py -s -c

entering double-player mode and update pygram refresh rate (for example, 60 frame per second)
python pong_game.py -f 60

When using computer vision to control the striker(s), there are two more arguments you can play around  

If you want to update the colour spectrum for colour tracking (in single, computer-vision mode)
python pong_game.py -s -c -u

If you want to set baseline values based on the first image of the software for colour tracking (in double, computer-vision mode)
python pong_game.py -c -v

For more details, check out the bottom of this code or use -h to ask for help on the Cmd or Terminal
'''

pygame.init()

# Basic parameters of the screen
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))

clock = pygame.time.Clock()

# Colors
BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255, 255, 255)
GREEN = pygame.Color(0, 255, 0)
RED = pygame.Color(255, 0, 0)

# Font that is used to render the text
font20 = pygame.font.Font("freesansbold.ttf", 20)

rolling_average_buffer = deque(maxlen=10)#rolling average butter

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
    y_fac, y_fac2 = 0, 0
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            y_fac = -1
        if event.key == pygame.K_DOWN:
            y_fac = 1
        if event.key == pygame.K_LEFT:
            y_fac2 = -1
        if event.key == pygame.K_RIGHT:
            y_fac2 = 1
    if event.type == pygame.KEYUP:
        if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
            y_fac = 0
        if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
            y_fac2 = 0
    return [y_fac, y_fac2]


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
    min_area = 30
    max_area =300
    num_cnt = 0
    area = 0
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_range, upper_range)
    _, mask1 = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
    cnts, _ = cv2.findContours(mask1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    print(cnts)
    OutArea = [cv2.contourArea(c) for c in cnts if cv2.contourArea(c) > min_area and cv2.contourArea(c) < max_area]
    num_cnt = len(OutArea)
    area = sum(OutArea)

    return num_cnt, area

def camera_controller(track1, track2, track1_init=None, track2_init=None):
    if track1_init is None or track2_init is None:
        if game_modes.single_player:
            y_fac = max(-1, min(1, track2 - track1))#compare the absolute size or area of two stream and rescale the difference in between 1 and -1
            y_fac2=0 #this value is not used later on in single player mode
        else:
            target1=100#needs to set arbitrary values so that the two tracks know what to compare with
            target2=200
            y_fac = max(-1, min(1, track1 -target1))
            y_fac2 = max(-1, min(1, track2 -target2))    
    else:
        avg_track_list = [0, 0]
        rolling_average_buffer.appendleft((int(track1), int(track2)))#save the incoming data stream into a buffer so that we can take the mean of them and output noise-robust data stream
        avg_track_list = np.nanmean(rolling_average_buffer, axis=0)       
        if game_modes.single_player:
            track1_diff=avg_track_list[0] - track1_init
            track2_diff=avg_track_list[1] - track2_init
            y_fac = max(-1, min(1, track2_diff - track1_diff))#compare the difference in changes of two stream and rescale the difference in between 1 and -1
            y_fac2=0 #this value is not used later on in single player mode
        else:
            y_fac = max(-1, min(1, avg_track_list[0] - track1_init))#compare the difference the current value and its own initial value and rescale the difference in between 1 and -1
            y_fac2 = max(-1, min(1, avg_track_list[1] - track2_init))
    return [y_fac, y_fac2]


def main(game_modes):
    running = True
    counter = 0
    strikerL = Striker(20, 0, 10, 100, 10, GREEN)
    strikerR = Striker(WIDTH - 30, 0, 10, 100, 10, GREEN)
    ball = Ball(WIDTH // 2, HEIGHT // 2, 7, 3, WHITE)
    ball2 = Ball(WIDTH // 2, HEIGHT // 2, 7, 5, RED) if game_modes.two_balls else None
    if game_modes.pygame_fps:
        pygame_fps=game_modes.pygame_fps   
    else:
        pygame_fps=120 #the default frame per second pygame update its game


    if game_modes.play_with_camera:
        print("Controlling the Striker with your camera")
        colour_profile = Path('color_ranges.json')
        if colour_profile.is_file()==False or game_modes.update_color_range:
          
            print(
            "[INFO] colour identification: use mouse cursor to adjust lower and upper bound of the threshold to isolate color spectrum. Isolated color will be shown as white in the Mask window. Press S to save and Q to exit"
        )
            hsv_color_range()
            print(f"[INFO] Complete updating the colour thresholds in the colour profile and use the new colour profile")
        else:
            print(f"[INFO] Use the existing colour profile.")
        
        print(
                f"[INFO] Load colour thresholds from colour profile. The default colour range is for blue and the second one is for red"
            )
        with open('color_ranges.json', 'r') as jsonfile:
            data = json.load(jsonfile)
        #Setting up camera streamming
        lower_ranges = [np.array(data[0].get('lower_range')), np.array(data[1].get('lower_range'))]
        upper_ranges = [np.array(data[0].get('upper_range')), np.array(data[1].get('upper_range'))]
        cap = WebcamVideoStream(src=0).start()
        fps = FPS().start()
        pygame.display.set_caption("Pong game with camera: Close this window or press ESC to end the game")

    elif game_modes.observer_mode:
        pygame.display.set_caption("Pong game Observer mode: 2 PC players are playing against each others. Close this window or press ESC to end the game")
        print(
            "[INFO] Welcome to Observer mode. Here, 2 PC players are playing against each others. You can change how 1 PC player responds to the ball(s) and compare what would be the best strategy to play this game."
        )
    else:
        pygame.display.set_caption("Pong game with keyboard: Up and Down are for player 1 (the right striker). Close this window or press ESC to end the game")
        print("Controlling the Striker with the keyboard. Use Up and Down to control player 1 (the right striker's movement). RIGHT and LEFT button are set to control the second player's movement (the left striker) by default, if player 2 is available")


    list_of_strikers = [strikerL, strikerR]
    strikerL_score, strikerR_score = 0, 0
    strikerL_y_fac, strikerR_y_fac = 0, 0
    area1_init = 0
    area2_init = 0
    while running:
        screen.fill(BLACK)
        if game_modes.observer_mode:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            # telling the PC(s) how to play this game
            if game_modes.two_balls:
                strikerL_y_fac = AI_controller_2balls(ball, ball2, strikerL)
                strikerR_y_fac = AI_controller_2balls(ball, ball2, strikerR)
            else:
                strikerL_y_fac = AI_controller(ball, strikerL)
                strikerR_y_fac = AI_controller(ball, strikerR)

        elif game_modes.play_with_camera:
            # initiate video capture with imutils
            frame = cap.read()
            frame = imutils.resize(frame, width=480, height=640)
            # do colour tracking here
            num_1, area_1 = color_track(frame, lower_ranges[0], upper_ranges[0])
            num_2, area_2 = color_track(frame, lower_ranges[1], upper_ranges[1])
            # save initial value of area size or whatever you want to compare
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
                    y_list = camera_controller(
                        area_1, area_2, area1_init, area2_init
                    )#compare the difference in changes of area1 and area2 to control the striker.
                else:
                    y_list = camera_controller(num_1, num_2)##this is the mode used in the demo, comparing the number of two cards and decide to striker R to move up or down

                strikerR_y_fac = y_list[0]
                # telling the PC how to play this game
                if game_modes.two_balls:
                    strikerL_y_fac = AI_controller_2balls(ball, ball2, strikerL)
                else:
                    strikerL_y_fac = AI_controller(ball, strikerL)
            else:
                if game_modes.use_baseline_value == True:
                    y_list = camera_controller(
                        area_1, area_2, area1_init, area2_init
                    )#comparing area1 and area2 with their initial values to control the two strikers.
                else:
                    y_list = camera_controller(area_1, area_2)
                    print("this is yet developed....One idea is to set a target value (a default value) for the area of two colour to compare or design rules of moving strikers based on where the centriod of the cards are")

                strikerR_y_fac = y_list[0]
                if len(y_list) > 1:
                    strikerL_y_fac = y_list[1]
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            if game_modes.single_player == True:
                y_list = keyboard_controller(event, pygame)
                strikerR_y_fac = y_list[0]
                # telling the PC how to play this game
                if game_modes.two_balls:
                    strikerL_y_fac = AI_controller_2balls(ball, ball2, strikerL)
                else:
                    strikerL_y_fac = AI_controller(ball, strikerL)
            else:
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
        ##scoring rules of the game
        if point1 == -1:
            strikerR_score += 1
        elif point1 == 1:
            strikerL_score += 1

        if game_modes.two_balls and point2:
            if point2 == -1:
                strikerR_score += 1
            elif point2 == 1:
                strikerL_score += 1
        ##reset the ball to its initial position after scoring
        if point1:
            ball.reset()
        if game_modes.two_balls and point2:
            ball2.reset()
        ##drawing the balls, scores and strikers
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
        if game_modes.play_with_camera:
            fps.update()
    ##output streaming information at the end of the game.
    if game_modes.play_with_camera:
        fps.stop()
        cv2.destroyAllWindows()
        cap.stop()
        print(f"[INFO] The PYGAME_FPS is {pygame_fps}. However, this camera captures frames at approx. FPS: {fps.fps()}. Try changing the argument PYGAME_FPS from 30, 60, 120, 240, to 1000 and observe how that would affect camera frame rate. Could you explain how the difference between pygame fps and camera frame rate might affect your gaming experience?")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-b",
        "--two_balls",
        action='store_true',
        help="Whether to use two ball or not. If it's  not provided, one ball is used",
    )
    ap.add_argument(
        "-s",
        "--single_player",
        action='store_true',
        help="Whether having single player in the game or not. If it's  not provided, entering two-player mode",
    )
    ap.add_argument(
        "-c",
        "--play_with_camera",
        action='store_true',
        help="Whether to control striker with camera or not. If it's  not provided, keyboard up and down are used",
    )
    ap.add_argument(
        "-o",
        "--observer_mode",
        action='store_true',
        help="Whether to watch two PC players playing or not. If it's  not provided, initiates the play mode",
    )
    ap.add_argument(
        "-u",
        "--update_color_range",
        action='store_true',
        help="Whether to update colour range for video tracking or not. If it's  not provided, defaults values to track blue and red are used",
    )
    ap.add_argument(
        "-v",
        "--use_baseline_value",
        action='store_true',
        help="Use calculating striker movement based on baseline value from the first frame",
    )
    ap.add_argument(
        "-f",
        "--pygame_fps",
        type=int,
        help="Use calculating striker movement based on baseline value from the first frame",
    )
    game_modes = ap.parse_args()
    main(game_modes)
    pygame.quit()
