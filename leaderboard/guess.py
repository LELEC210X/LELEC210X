import requests

hostname = "http://localhost:5000"
key = "aqH27o66E8xz-IotBk11ZZo1ix7Vbs5H2pTXlSra"
guess = "fire"

response = requests.post(f"{hostname}/lelec210x/leaderboard/submit/{key}/{guess}", timeout=1)

# N.B.: the timeout is generally a good idea to avoid blocking infinitely (if an error occurs)
# but you can change its value. Note a too small value may not give the server enough time
# to reply.

import json

# All responses are JSON dictionaries
response_as_dict = json.loads(response.text)