def make_event(method, path, status_code, event_type="http_request"):
    """Classify the received HTTP response without inventing an actor or cause."""
    if event_type in {"login_failure", "login_success"}:
        return event_type
    if method == "GET" and path == "/" and status_code == 200:
        return "post_list"
    if status_code >= 400:
        return "request_error"
    return "http_request"
