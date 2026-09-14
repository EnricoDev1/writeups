s = open("chall.txt", "r").read()
print(s.encode('utf-16-le').decode('latin-1'))
