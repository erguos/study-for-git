from fastapi import Depends, Header, HTTPException

from .utils.auth import verify_token


def get_current_user(authorization: str = Header(default="")):
    """Extract and validate the Bearer token -> return payload dict."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录或缺少令牌")
    token = authorization[len("Bearer "):].strip()
    try:
        return verify_token(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


def require_admin(user: dict = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user
