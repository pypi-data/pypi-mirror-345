# c_tools.py
# Import modules
import requests, psutil, time
from PIL import Image
from io import BytesIO

# Download a file
def download(url: str, path: str) -> None:
    """
    Download a file from the internet.

    :param url: URL of the file to download
    :param path: Path to save the file to
    :raises Exception: If there is an error downloading the file
    """
    try:
        response = requests.get(url)
        with open(path, 'wb') as file:
            file.write(response.content)
    except Exception as e:
        raise Exception(f"Error downloading file: {e}")

# Download an image
def download_image(url: str) -> Image:
    """
    Download an image from the internet.

    :param url: URL of the image to download
    :return: PIL Image object
    :raises Exception: If there is an error downloading the image
    """
    try:
        response = requests.get(url)
        return Image.open(BytesIO(response.content))
    except Exception as e:
        raise Exception(f"Error downloading image: {e}")

# Check if connected to the internet
def isnetwork() -> bool:
    """
    Check if the computer is connected to the internet.

    This function checks if the computer is connected to the internet by trying to connect to Google's public DNS server.
    If the connection is successful, the function returns True, otherwise it returns False.

    :return: True if connected to the internet, False otherwise
    """
    import socket
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

# Check if a URL is reachable
def check_url(url: str, timeout: int = 5) -> int | bool:
    """
    Check if a URL is reachable and return its HTTP status code.
    :param url: URL to check.
    :param timeout: Timeout in seconds.
    :return: HTTP status code or False if unreachable.
    """
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return response.status_code
    except requests.RequestException:
        return False

# Measure network speed
def speedtest(duration: float = 1.0) -> dict:
    """
    Measure network download and upload speed.
    :param duration: Time to measure in seconds.
    :return: Dictionary with 'download' and 'upload' speeds in MB/s.
    """
    start = psutil.net_io_counters()
    time.sleep(duration)
    end = psutil.net_io_counters()
    download = (end.bytes_recv - start.bytes_recv) / (1024 * 1024 * duration)
    upload = (end.bytes_sent - start.bytes_sent) / (1024 * 1024 * duration)
    return {'download': download, 'upload': upload}