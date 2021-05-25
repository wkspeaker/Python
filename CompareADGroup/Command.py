import os

cmd = os.popen("net user swang /domain")

text = cmd.read()

print(text)