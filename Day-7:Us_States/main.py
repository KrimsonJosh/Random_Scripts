import pandas
import numpy as np
import turtle

screen = turtle.Screen()
screen.title("US States game")
screen.addshape("blank_states_img.gif")
turtle.shape("blank_states_img.gif")


data = pandas.read_csv("50_states.csv")
states = data.state.to_list()

guessed_states = []
while len(guessed_states) < 50:
    answer_state = screen.textinput(title = "Guess the state", prompt = "What's another states name?\n").title()

    if answer_state == "Exit":
        break
    if answer_state in states:
        t = turtle.Turtle()
        t.hideTurtle()
        t.penup()
        row = data[data.state] == answer_state
        t.goto(row.x.item(), row.y.item())
        t.write(answer_state)
        guessed_states.append(answer_state)

wasntguessed = [i for i in states if i not in guessed_states]
df = pandas.DataFrame(wasntguessed)
df.to_csv('states_to_learn.csv', index = False)
