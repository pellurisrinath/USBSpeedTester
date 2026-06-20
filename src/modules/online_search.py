import urllib.request
import urllib.parse
import re
import sys

def search_device_specs(device_name):
    """
    Performs a lightweight web search via DuckDuckGo HTML interface 
    to retrieve specifications and speed metrics for a given device name.
    """
    if not device_name or device_name.lower() in ["unknown", "unknown usb disk", "usb mass storage device", "usb composite device"]:
        return []
        
    # Construct a targeted search query
    query = f"{device_name} flash drive read write speed specifications specs"
    url = "https://html.duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
    
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    )
    
    try:
        # 30-second timeout for the web search to avoid blocking
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8')
            
            # Extract snippets using regex
            snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
            results = []
            for snippet in snippets[:4]:
                clean = re.sub(r'<[^>]+>', '', snippet)
                clean = clean.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&#x27;', "'")
                clean = clean.strip()
                if clean:
                    results.append(clean)
            return results
    except Exception as e:
        print(f"Online specs search failed for '{device_name}': {e}", file=sys.stderr)
        return None
