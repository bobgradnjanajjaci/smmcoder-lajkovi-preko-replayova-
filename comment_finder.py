import re
import time
import requests

HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

# Proširene ključne riječi (bolje prepoznavanje)
REQUIRED_PHRASES = [
    "encrypted money code",
    "encryptedmoneycode",
    "encrypted code",
    "ethan rothwell"
]

REQUEST_TIMEOUT = 7
MAX_PAGES = 4
RETRY_COUNT = 2
RETRY_DELAY = 4

_session = requests.Session()

def normalize(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def has_target_phrase(text: str) -> bool:
    norm = normalize(text)
    return any(phrase in norm for phrase in REQUIRED_PHRASES)

def expand_url(url: str) -> str:
    if "/video/" in url:
        return url
    try:
        r = _session.head(url, headers=HEADERS, allow_redirects=True, timeout=REQUEST_TIMEOUT)
        return r.url or url
    except:
        try:
            r = _session.get(url, headers=HEADERS, allow_redirects=True, timeout=REQUEST_TIMEOUT)
            return r.url
        except:
            return url

def extract_video_id(url: str):
    m = re.search(r"/video/(\d+)", url)
    return m.group(1) if m else None

def fetch_comments(video_id: str):
    comments = []
    cursor = 0
    for _ in range(MAX_PAGES):
        try:
            r = _session.get(
                "https://www.tiktok.com/api/comment/list/",
                headers=HEADERS,
                params={"aid": 1988, "count": 50, "cursor": cursor, "aweme_id": video_id},
                timeout=REQUEST_TIMEOUT,
            )
            if r.status_code != 200:
                break

            data = r.json()
            batch = data.get("comments") or []
            comments.extend(batch)

            if not data.get("has_more"):
                break
            cursor = int(data.get("cursor") or 0)
        except:
            break
    return comments

def pick_best_comment(comments):
    """Bira komentar sa najviše replayova koji sadrži ključnu frazu"""
    best = None
    best_replies = -1
    top_likes = 0

    for c in comments[:80]:   # gledamo prvih 60 komentara
        try:
            text = c.get("text") or ""
            likes = int(c.get("digg_count") or 0)
            replies = int(c.get("reply_comment_total") or c.get("reply_count") or 0)
            top_likes = max(top_likes, likes)

            if not has_target_phrase(text):
                continue

            # Prioritet = broj replayova (glavni kriterij)
            if replies > best_replies:
                best_replies = replies
                best = {
                    "cid": c.get("cid"),
                    "likes": likes,
                    "replies": replies,
                    "username": c.get("user", {}).get("unique_id"),
                    "text": text,
                }
        except:
            continue

    return best, top_likes, best_replies

def build_comment_link(video_url: str, cid: str) -> str:
    base = video_url.split("?")[0]
    return f"{base}?cid={cid}"

def find_target_comment(video_url: str) -> dict:
    video_url = expand_url(video_url)
    video_id = extract_video_id(video_url)

    if not video_id:
        return {"found": False, "reason": "no_video_id"}

    for attempt in range(RETRY_COUNT + 1):
        comments = fetch_comments(video_id)

        if comments:
            best, top_likes, best_replies = pick_best_comment(comments)

            if best:
                comment_link = build_comment_link(video_url, best["cid"])
                return {
                    "found": True,
                    "video_id": video_id,
                    "comment_link": comment_link,
                    "my_likes": best["likes"],
                    "top_likes": top_likes,
                    "replies": best_replies,
                    "username": best["username"],
                    "matched_text": best["text"],
                    "attempt": attempt + 1,
                }

        if attempt < RETRY_COUNT:
            time.sleep(RETRY_DELAY)

    return {"found": False, "reason": "no_match"}




