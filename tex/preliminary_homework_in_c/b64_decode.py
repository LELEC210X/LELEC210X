import base64
import sys

b64 = sys.argv[1]
b64_bytes = b64.encode("ascii")
message_bytes = base64.b64decode(b64_bytes)
message = message_bytes.decode("ascii")

print(message)
