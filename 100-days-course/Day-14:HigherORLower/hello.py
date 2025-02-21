from flask import Flask

app = Flask(__name__)

# Decorators

def make_bold(function):
    def wrapper():
        return "<b>" + function() + "</b>"
    return wrapper

def make_emphasis(function):
    def wrapper():
        return "<em>" + function() + "</em>"
    return wrapper

def make_underlined(function):
    def wrapper():
        return "<u>" + function() + "</u>"
    return wrapper

@app.route('/')
def hello_world():
    return '<h1 style="text-align: center">Hello, World!</h1> \
            <p> This is a paragraph</p> \
            <img src=https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExNWU5YmFoaXNvbzR1M2IxYjMyMHQxcXd1cnhnam4zanJ5Y2h6ZWVlcCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/YRVP7mapl24G6RNkwJ/giphy.gif width = 500px></img>'

@app.route('/bye')
@make_bold
def bye():
    return 'Bye'

@app.route('/username/<name>/<int:number>')
def greet(name, number):
    return f"Hello {name}, you are {number} years old"


if __name__ == "__main__":
    app.run(debug = True)
