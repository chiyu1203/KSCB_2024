import turtle

screen = turtle.Screen().bgcolor("black")
turtle.setup(800, 600, 1, 75)
turtle.tracer(0)
score_a = 0
score_b = 0
paddle1 = turtle.Turtle()
paddle1.speed(0)
paddle1.shape("square")
paddle1.color("white")
paddle1.shapesize(stretch_wid=4, stretch_len=1)
paddle1.penup()
paddle1.goto(-350, 0)
paddle2 = turtle.Turtle()
paddle2.speed(0)
paddle2.shape("square")
paddle2.color("white")
paddle2.shapesize(stretch_wid=4, stretch_len=1)
paddle2.penup()
paddle2.goto(350, 0)

ball1 = turtle.Turtle()
ball1.speed(0)
ball1.shape("circle")
ball1.color("red")
ball1.penup()
ball1.goto(0, -20)
ball1.dx = 0.2
ball1.dy = -0.2

ball2 = turtle.Turtle()
ball2.speed(0)
ball2.shape("circle")
ball2.color("red")
ball2.penup()
ball2.goto(0, 20)
ball2.dx = -0.2
ball2.dy = 0.2

balls = [ball1, ball2]
pen = turtle.Turtle()
pen.speed(0)
pen.color("grey")
pen.penup()
pen.hideturtle()
pen.goto(0, 260)
pen.write(
    "Collective Power: 0    Konstanz Gamer: 0",
    align="center",
    font=("Bold", 20, "normal"),
)


def paddle1_up():
    y = paddle1.ycor()
    y += 20
    paddle1.sety(y)


def paddle1_down():
    y = paddle1.ycor()
    y -= 20
    paddle1.sety(y)


def paddle2_up():
    y = paddle2.ycor()
    y += 20
    paddle2.sety(y)


def paddle2_down():
    y = paddle2.ycor()
    y -= 20
    paddle2.sety(y)


turtle.listen()
turtle.onkeypress(paddle1_up, "Up")
turtle.onkeypress(paddle1_down, "Down")

while True:
    turtle.update()
    for ball in balls:
        ball.setx(ball.xcor() + ball.dx)
        ball.sety(ball.ycor() + ball.dy)
        if ball.ycor() > 290:
            ball.sety(290)
            ball.dy *= -1
        if ball.ycor() < -290:
            ball.sety(-290)
            ball.dy *= -1
        if ball.xcor() > 390:
            ball.goto(0, 0)
            ball.dx *= -1
            score_a += 1
            pen.clear()
            pen.write(
                "Collective Power: {}    Konstanz Gamer: {}".format(score_a, score_b),
                align="center",
                font=("Bold", 20, "normal"),
            )
        if ball.xcor() < -390:
            ball.goto(0, 0)
            ball.dx *= -1
            score_b += 1
            pen.clear()
            pen.write(
                "Collective Power: {}    Konstanz Gamer: {}".format(score_a, score_b),
                align="center",
                font=("Bold", 20, "normal"),
            )
        if (ball.xcor() > 340 and ball.xcor() < 350) and (
            ball.ycor() < paddle2.ycor() + 40 and ball.ycor() > paddle2.ycor() - 40
        ):
            ball.setx(340)
            ball.dx *= -1
        if (ball.xcor() < -340 and ball.xcor() > -350) and (
            ball.ycor() < paddle1.ycor() + 40 and ball.ycor() > paddle1.ycor() - 40
        ):
            ball.setx(-340)
            ball.dx *= -1
        any_ball = balls[0]
        for ball in balls:
            if ball.xcor() > any_ball.xcor():
                any_ball = ball
        if (
            paddle2.ycor() < any_ball.ycor()
            and abs(paddle2.ycor() - any_ball.ycor()) > 10
        ):
            paddle2_up()
        elif (
            paddle2.ycor() > any_ball.ycor()
            and abs(paddle2.ycor() - any_ball.ycor()) > 10
        ):
            paddle2_down()

turtle.mainloop()
