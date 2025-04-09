from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def fetch_steam_profile_data(steam_id):
    url = f"https://steamcommunity.com/profiles/{steam_id}"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return "Failed to access profile page.", None, None, None, [], []

    soup = BeautifulSoup(response.text, "html.parser")

    # --- Profile Info ---
    profile_name_tag = soup.find("span", class_="actual_persona_name")
    profile_name = profile_name_tag.text.strip() if profile_name_tag else "Unknown"

    avatar_tag = soup.find("div", class_="playerAvatarAutoSizeInner")
    profile_avatar = avatar_tag.img["src"] if avatar_tag and avatar_tag.img else ""

    level_tag = soup.find("span", class_="friendPlayerLevelNum")
    profile_level = level_tag.text.strip() if level_tag else "Unknown"

    # --- Friends ---
    friend_blocks = soup.find_all("div", class_="friendBlock")
    friends = []
    for friend in friend_blocks:
        name_div = friend.find("div", class_="friendBlockContent")
        name = name_div.get_text(strip=True).split("Offline")[0].split("Online")[0].strip()

        status_tag = friend.find("span", class_="friendSmallText")
        status = status_tag.text.strip() if status_tag else "Unknown"

        avatar_tag = friend.find("img")
        avatar_url = avatar_tag["src"] if avatar_tag else ""

        profile_link_tag = friend.find("a", class_="friendBlockLinkOverlay")
        profile_link = profile_link_tag["href"] if profile_link_tag else ""

        friends.append({
            "Name": name,
            "Status": status,
            "Avatar": avatar_url,
            "Profile Link": profile_link
        })

    # --- Recently Played Games ---
    recent_games_section = soup.find("div", class_="recentgame_quicklinks")
    games = []

    if recent_games_section:
        game_blocks = soup.find_all("div", class_="recent_game")
        for game in game_blocks:
            name_tag = game.find("div", class_="game_name")
            name = name_tag.text.strip() if name_tag else "Unknown"

            hours_tag = game.find("div", class_="game_info_details")
            hours = hours_tag.text.strip() if hours_tag else "Unknown"

            img_tag = game.find("img")
            img_url = img_tag["src"] if img_tag else ""

            games.append({
                "Name": name,
                "Playtime": hours,
                "Image": img_url
            })

    return None, profile_name, profile_avatar, profile_level, friends, games

@app.route("/", methods=["GET", "POST"])
def index():
    steam_id = ""
    error = None
    profile_name = profile_avatar = profile_level = None
    friends = []
    games = []

    if request.method == "POST":
        steam_id = request.form["steam_id"]
        error, profile_name, profile_avatar, profile_level, friends, games = fetch_steam_profile_data(steam_id)

    return render_template("index.html",
                           steam_id=steam_id,
                           error=error,
                           profile_name=profile_name,
                           profile_avatar=profile_avatar,
                           profile_level=profile_level,
                           friends=friends,
                           games=games)

if __name__ == "__main__":
    app.run(debug=True)
