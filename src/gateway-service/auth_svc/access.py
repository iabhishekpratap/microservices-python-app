import os, requests

def login(request):
    auth = request.authorization
    if not auth:
        return None, ("missing credentials", 401)

    basicAuth = (auth.username, auth.password)
    try:
        response = requests.post(
            f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/login", auth=basicAuth
        )
        return response.text, None if response.status_code == 200 else (None, (response.text, response.status_code))
    except Exception as e:
        return None, ("auth service unreachable", 500)
