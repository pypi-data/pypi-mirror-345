import streamlit.components.v1 as components
import os
import requests


_RELEASE = True
if not _RELEASE:
    _component_func = components.declare_component(
        "google_sign_in",
        url="http://localhost:3001",
    )
else:
    here = os.path.dirname(os.path.abspath(__file__))
    build_path = os.path.join(here, "frontend/build")
    _component_func = components.declare_component(
        "google_sign_in",
        path=build_path,
    )


def st_google_sign_in(client_id: str):
    """在 Streamlit App 中顯示 Google 登入按鈕，回傳 userinfo dict。"""
    # 把 client_id 傳到前端
    token = _component_func(clientId=client_id)
    if not token:
        return None

    # 用 token 去換 userinfo
    resp = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {token}"},
        timeout=5,
    )
    if resp.ok:
        return resp.json()
    else:
        raise RuntimeError("Failed to fetch user info: " + resp.text)
