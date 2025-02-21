from flask import Flask 
import random
app = Flask(__name__) 

randomNumber = random.randint(0,9)

def TooLowDecorator(func):
    def wrapper(number):
        if number < randomNumber:
            return ("<h1 style = color: blue>TOO LOW!</h1> \
                    <img src = https://media.giphy.com/media/jD4DwBtqPXRXa/giphy.gif> </img>")
        return func(number)
    return wrapper
def TooHighDecorator(func):
    def wrapper(number):
        if number > randomNumber:
            return ("<h1 style = color: red>TOO HIGH!</h1> \
                    <img src = https://media.giphy.com/media/3o6ZtaO9BZHcOjmErm/giphy.gif> </img>")
        return func(number)
    return wrapper

@app.route('/')
def guessANumber():
    return("<h1>Guess a number between 0 - 9.</h1> \
           <img src = https://media.giphy.com/media/3o7aCSPqXE5C6T8tBC/giphy.gif> </img>")

@app.route('/<int:number>')
@TooLowDecorator 
@TooHighDecorator
def higherOrLower(number):
    return ("<h1 style='color: green'>CORRECT!</h1>"
            "<img src='https://media.giphy.com/media/4T7e4DmcrP9du/giphy.gif'>")





if __name__ == "__main__":
    app.run(debug = True)
