import time

import requests

if __name__ == "__main__":
    while True:
        t = time.time()
        response = requests.get(
            "https://perceval.elen.ucl.ac.be/lelec2103/leaderboard/status"
        )
        elapsed = 1000 * (time.time() - t)
        print(f"[{response.status_code}] Took {elapsed:.2f} milliseconds")
