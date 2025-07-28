import os
from dotenv import load_dotenv


load_dotenv()
WHITELISTED_USERS = set(
    map(int, filter(None, os.getenv("WHITELISTED_USERS", "").split(",")))
)


print(WHITELISTED_USERS)