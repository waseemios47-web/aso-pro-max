"""
Apple Search Ads API 认证模块（共用）

工作流：
  1. 从 .env 读 client_id / team_id / key_id / org_id + 私钥路径
  2. 用 ES256 + 私钥签 JWT，作为 client_secret
  3. 向 https://appleid.apple.com/auth/oauth2/token 换 access token
  4. 缓存 token（默认 1 小时有效）到 .secrets/token_cache.json，避免重复换取
  5. 返回可直接用于 v5 API 的 (access_token, headers) 元组

用法：
  from asa_auth import get_session
  session = get_session()
  resp = session.get("https://api.searchads.apple.com/api/v5/...")
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

import jwt
import requests

# 凭据存在用户 config 目录而非 skill 目录（避免 skill 重装/分发时混入个人凭据）
CONFIG_DIR = Path(os.environ.get(
    "ASO_PROMAX_CONFIG_DIR",
    Path.home() / ".config" / "aso-pro-max"
))
ENV_PATH = CONFIG_DIR / ".env"
TOKEN_CACHE = CONFIG_DIR / ".secrets" / "token_cache.json"
SKILL_DIR = Path(__file__).parent.parent  # 仅作其它用途引用

TOKEN_URL = "https://appleid.apple.com/auth/oauth2/token"
API_BASE = "https://api.searchads.apple.com/api/v5"
JWT_AUD = "https://appleid.apple.com"
JWT_TTL = 60 * 60  # 1 小时


def _load_env() -> dict[str, str]:
    if not ENV_PATH.exists():
        raise FileNotFoundError(
            f"Missing {ENV_PATH}. Copy .env.example to ~/.config/aso-pro-max/.env "
            f"and fill in credentials.\n"
            f"缺少 {ENV_PATH}。请拷贝 .env.example 为 ~/.config/aso-pro-max/.env 并填入凭据。"
        )
    env = {}
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip("'\"")
    required = ["ASA_CLIENT_ID", "ASA_TEAM_ID", "ASA_KEY_ID",
                "ASA_ORG_ID", "ASA_PRIVATE_KEY_PATH"]
    missing = [k for k in required if not env.get(k)]
    if missing:
        raise ValueError(f".env missing fields / .env 缺少字段: {missing}")
    return env


def _build_client_secret(env: dict[str, str]) -> str:
    """用 ES256 私钥签 JWT 当 client_secret。"""
    pem_path = Path(env["ASA_PRIVATE_KEY_PATH"]).expanduser()
    if not pem_path.exists():
        raise FileNotFoundError(f"Private key not found / 私钥不存在: {pem_path}")
    private_key = pem_path.read_text()

    now = int(time.time())
    payload = {
        "sub": env["ASA_CLIENT_ID"],
        "aud": JWT_AUD,
        "iat": now,
        "exp": now + JWT_TTL,
        "iss": env["ASA_TEAM_ID"],
    }
    headers = {"alg": "ES256", "kid": env["ASA_KEY_ID"]}
    return jwt.encode(payload, private_key, algorithm="ES256", headers=headers)


def _fetch_access_token(env: dict[str, str]) -> dict:
    client_secret = _build_client_secret(env)
    resp = requests.post(
        TOKEN_URL,
        headers={"Host": "appleid.apple.com",
                 "Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": env["ASA_CLIENT_ID"],
            "client_secret": client_secret,
            "scope": "searchadsorg",
        },
        timeout=30,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"换 token 失败: {resp.status_code} {resp.text}")
    data = resp.json()
    data["fetched_at"] = int(time.time())
    return data


def _load_cached_token() -> dict | None:
    if not TOKEN_CACHE.exists():
        return None
    try:
        data = json.loads(TOKEN_CACHE.read_text())
    except Exception:
        return None
    age = int(time.time()) - data.get("fetched_at", 0)
    expires_in = data.get("expires_in", 3600)
    # 提前 60 秒续期，避免边界
    if age < expires_in - 60:
        return data
    return None


def _save_token(data: dict) -> None:
    TOKEN_CACHE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_CACHE.write_text(json.dumps(data, indent=2))


def get_access_token(force_refresh: bool = False) -> str:
    if not force_refresh:
        cached = _load_cached_token()
        if cached:
            return cached["access_token"]
    env = _load_env()
    data = _fetch_access_token(env)
    _save_token(data)
    return data["access_token"]


def get_session() -> requests.Session:
    """返回带认证 header 的 requests.Session。"""
    env = _load_env()
    token = get_access_token()
    s = requests.Session()
    s.headers.update({
        "Authorization": f"Bearer {token}",
        "X-AP-Context": f"orgId={env['ASA_ORG_ID']}",
        "Content-Type": "application/json",
    })
    return s


def get_org_id() -> str:
    return _load_env()["ASA_ORG_ID"]


def get_adam_id() -> str | None:
    """读取 .env 中当前项目的 adamId（key 名 APP_ADAM_ID 或旧版 WEPICS_ADAM_ID）。"""
    env = _load_env()
    return env.get("APP_ADAM_ID") or env.get("WEPICS_ADAM_ID")


if __name__ == "__main__":
    # 调试：跑这个文件直接测试认证
    import sys
    try:
        token = get_access_token(force_refresh="--refresh" in sys.argv)
        print(f"✅ 认证成功")
        print(f"   token (前 40 字符): {token[:40]}...")
        print(f"   org_id: {get_org_id()}")
        print(f"   adam_id: {get_adam_id()}")
    except Exception as e:
        print(f"❌ 认证失败: {e}", file=sys.stderr)
        sys.exit(1)
