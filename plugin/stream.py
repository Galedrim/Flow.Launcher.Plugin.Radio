import re

from urllib import request
from streamlink.session import Streamlink  

def is_youtube_stream(url):
    try:
        with request.urlopen(url) as response:
            if response.getcode() != 200:
                return False

            page_content = response.read().decode('utf-8')
            is_live_pattern = r'"isLive"\s*:\s*true'
            return bool(re.search(is_live_pattern, page_content))

    except Exception:
        return False

def get_best_stream(url):
    try:
        session = Streamlink()
        session.set_option("stream-timeout", 30)
        available_streams = session.streams(url)
        best_stream = available_streams.get("best")
        return best_stream
    
    except Exception :
        return None

