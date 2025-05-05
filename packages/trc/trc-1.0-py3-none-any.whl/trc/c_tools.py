# Import modules
import requests
from PIL import Image
from io import BytesIO

# Download a file
def download(url: str, path: str) -> None:
    try:
        response = requests.get(url)
        with open(path, 'wb') as file:
            file.write(response.content)
    except Exception as e:
        print(f"Error downloading file: {e}")

# Download an image
def download_image(url: str) -> Image:
    try:
        response = requests.get(url)
        return Image.open(BytesIO(response.content))
    except Exception as e:
        print(f"Error downloading image: {e}")

# Check if connected to the internet
def isnetwork() -> bool:
    import socket
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False