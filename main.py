from dotenv import load_dotenv, find_dotenv
import os

# Load chakoshi environment configuration file
env_path = find_dotenv()
if not env_path:
    # Environment configuration file not found.
    print("Environment configuration file could not be found.")
else:
    # Loading environment configuration file: {env_path}
    print(f"Loading environment configuration file: {env_path}")
    load_dotenv(dotenv_path=env_path)

from chakoshi_server.server import build_server

if __name__ == "__main__":
    build_server().run_stdio()
