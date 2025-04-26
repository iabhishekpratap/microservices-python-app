import os, requests

def token(request):
    if "Authorization" not in request.headers:
        return None, ("missing credentials", 401)

    token = request.headers["Authorization"]
    if not token:
        return None, ("missing credentials", 401)

    try:
        response = requests.post(
            f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/validate",
            headers={"Authorization": token},
        )
        return response.text, None if response.status_code == 200 else (None, (response.text, response.status_code))
    except Exception:
        return None, ("auth service unreachable", 500)
