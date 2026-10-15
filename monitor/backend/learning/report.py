from learning.http_rules import assess


def build_report(events, threshold, after_id, reference_time):
    result = assess(events, threshold)
    records = result["views"] + result["following_errors"]
    return {
        "rule": "HTTP 게시글 목록 조회",
        "source": "http_live",
        "after_id": after_id,
        "reference_time": reference_time.isoformat(),
        "window_seconds": 60,
        "observed_count": result["count"],
        "threshold": threshold,
        "candidate": result["candidate"],
        "verdict": "검토 후보" if result["candidate"] else "기준 미해당",
        "reason": f"목록 조회 {result['count']}회와 기준 {threshold}회를 비교했습니다. 뒤따른 404는 조회 횟수에 포함하지 않았습니다.",
        "view_ids": result["view_ids"],
        "following_error_ids": [event["id"] for event in result["following_errors"]],
        "evidence": [event["id"] for event in records],
        "records": records,
    }
