import requests
from comment_finder import find_target_comment
from like_rules import calculate_target_likes

API_KEY = "c8897bba6c4da59edea6a936a69d2ef0"
PANEL_URL = "https://smmcoder.com/api/v2"
SERVICE_ID = 8330

def process_video(video_url: str):
    result = find_target_comment(video_url)

    if not result.get("found"):
        return {"status": "error", "message": "Nije pronađen dobar komentar"}

    replies = result.get("replies", 0)
    target = calculate_target_likes(result["top_likes"])

    if target == 0:
        return {"status": "skip", "message": f"Top komentar prejak ({result['top_likes']} likes)"}

    my_likes = int(result.get("my_likes") or 0)
    to_send = max(0, target - my_likes)

    if to_send <= 0:
        return {"status": "ok", "message": "Već ima dovoljno lajkova"}

    payload = {
        "key": API_KEY,
        "action": "add",
        "service": SERVICE_ID,
        "link": result["comment_link"],
        "quantity": to_send,
        "username": result["username"]
    }

    try:
        r = requests.post(PANEL_URL, data=payload, timeout=25)
        return {
            "status": "sent",
            "comment_link": result["comment_link"],
            "likes_sent": to_send,
            "replies_on_comment": replies,
            "response": r.text[:200]
        }
    except Exception as e:
        return {"status": "error", "message": f"Panel error: {e}"}

