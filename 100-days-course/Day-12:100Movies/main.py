import requests
from bs4 import BeautifulSoup

URL = "https://web.archive.org/web/20200518073855/https://www.empireonline.com/movies/features/best-movies-2/"

# Write your code below this line 👇

response = requests.get(URL)
response.raise_for_status()
response = response.text

soup = BeautifulSoup(response, 'html.parser')

songs = soup.find_all(name = "h3", class_ = "title")
songTexts = [song.getText() for song in songs]
print(songTexts)

songTexts.reverse()

with open("file.txt", "w") as file:
    for i in songTexts:
        file.write(f"{i}\n")


# songNames = [x[1] for x in songs]
# print(songNames)

