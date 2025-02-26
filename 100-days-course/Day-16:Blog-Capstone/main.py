from flask import Flask, render_template
import requests
from post import Post
app = Flask(__name__)

@app.route('/')
def home():
    res = requests.get("https://api.npoint.io/c790b4d5cab58020d391")
    res.raise_for_status()
    res = res.json()

    return render_template("index.html", blog_posts = res)

@app.route('/post/<int:index>')
def get_post(index):
    res = requests.get("https://api.npoint.io/c790b4d5cab58020d391")
    res.raise_for_status()
    res = res.json()
    for post_data in res:
        if post_data["id"] == index: 
            post = Post(post_data["id"], post_data["title"], post_data["subtitle"], post_data["body"])

    return render_template("post.html", post = post)

if __name__ == "__main__":
    app.run(debug=True)
