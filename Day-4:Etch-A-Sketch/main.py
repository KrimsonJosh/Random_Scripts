from turtle import Turtle, Screen


tim = Turtle()

screen = Screen()
screen.listen() #listens to user keys to change events

def moveForward():
    tim.forward(10)
def moveBackward():
    tim.backward(10)
def moveLeft():
    tim.left(10)
def moveRight():
    tim.right(10)
def clear():
    tim.clear()
    tim.penup()
    tim.home()
    tim.pendown()

screen.onkey(key = "W", fun = moveForward)
screen.onkey(key = "S", fun = moveBackward)
screen.onkey(key = "A", fun = moveLeft)
screen.onkey(key = "D", fun = moveRight)
screen.onkey(key = "C", fun = clear)
screen.exitonclick()