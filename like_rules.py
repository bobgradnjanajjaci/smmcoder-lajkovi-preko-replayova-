def calculate_target_likes(top_likes: int) -> int:
    if top_likes >= 10000:
        return 0
    if top_likes < 300:
        return 300
    if top_likes < 1000:
        return int(top_likes * 1.3)
    elif top_likes < 3000:
        return int(top_likes * 2)
    elif top_likes < 8000:
        return top_likes + 1000
    else:
        return top_likes

