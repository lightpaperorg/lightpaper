#!/usr/bin/env python3
"""Bootstrap first lightpaper account: Firebase user → account → API key.

Usage:
    export LIGHTPAPER_API_URL=https://lightpaper-tu5pdlncyq-uc.a.run.app
    export FIREBASE_PROJECT_ID=refreshing-rune-471208-e5
    python scripts/bootstrap_account.py

Prerequisites:
    pip install firebase-admin httpx

This script:
1. Creates a Firebase Auth user (or reuses existing)
2. Generates a custom token via Firebase Admin SDK
3. Exchanges the custom token for an ID token via Google Identity Toolkit REST API
4. Creates a lightpaper account (POST /v1/account)
5. Generates an API key (POST /v1/account/keys)
6. Prints the API key for use in the MCP server
"""

import json
import os
import sys

import firebase_admin
import httpx
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials as firebase_credentials

# --- Configuration ---
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "refreshing-rune-471208-e5")
API_URL = os.getenv("LIGHTPAPER_API_URL", "https://lightpaper-tu5pdlncyq-uc.a.run.app")
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY", "")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

# Bootstrap user details
BOOTSTRAP_EMAIL = os.getenv("BOOTSTRAP_EMAIL", "jon@lightpaper.org")
BOOTSTRAP_DISPLAY_NAME = os.getenv("BOOTSTRAP_DISPLAY_NAME", "Jonathan Gregory")
BOOTSTRAP_HANDLE = os.getenv("BOOTSTRAP_HANDLE", "jon")


def init_firebase():
    """Initialize Firebase Admin SDK with service account credentials if available."""
    if not firebase_admin._apps:
        if GOOGLE_APPLICATION_CREDENTIALS:
            cred = firebase_credentials.Certificate(GOOGLE_APPLICATION_CREDENTIALS)
            firebase_admin.initialize_app(cred, options={"projectId": FIREBASE_PROJECT_ID})
        else:
            firebase_admin.initialize_app(options={"projectId": FIREBASE_PROJECT_ID})


def get_or_create_firebase_user(email: str, display_name: str) -> str:
    """Create a Firebase Auth user or return existing UID."""
    try:
        user = firebase_auth.get_user_by_email(email)
        print(f"  Found existing Firebase user: {user.uid}")
        return user.uid
    except firebase_auth.UserNotFoundError:
        user = firebase_auth.create_user(
            email=email,
            display_name=display_name,
            email_verified=True,
        )
        print(f"  Created Firebase user: {user.uid}")
        return user.uid


def generate_custom_token(uid: str) -> str:
    """Generate a Firebase custom token for the user."""
    token = firebase_auth.create_custom_token(uid)
    return token.decode("utf-8") if isinstance(token, bytes) else token


def exchange_custom_token_for_id_token(custom_token: str) -> str:
    """Exchange Firebase custom token for an ID token via Identity Toolkit REST API.

    Requires FIREBASE_API_KEY (Web API key from Firebase Console → Project Settings).
    """
    if not FIREBASE_API_KEY:
        print("\n  ERROR: FIREBASE_API_KEY is required to exchange custom token for ID token.")
        print("  Find it in Firebase Console → Project Settings → General → Web API Key")
        print("  Then: export FIREBASE_API_KEY=your_key_here")
        sys.exit(1)

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={FIREBASE_API_KEY}"
    resp = httpx.post(
        url,
        json={
            "token": custom_token,
            "returnSecureToken": True,
        },
        timeout=30,
    )

    if resp.status_code != 200:
        print(f"  ERROR exchanging token: {resp.status_code} — {resp.text}")
        sys.exit(1)

    data = resp.json()
    return data["idToken"]


def create_account(id_token: str) -> dict:
    """Create a lightpaper account via POST /v1/account."""
    resp = httpx.post(
        f"{API_URL}/v1/account",
        headers={
            "Authorization": f"Bearer {id_token}",
            "Content-Type": "application/json",
        },
        json={
            "handle": BOOTSTRAP_HANDLE,
            "display_name": BOOTSTRAP_DISPLAY_NAME,
        },
        timeout=30,
    )

    if resp.status_code == 409:
        print("  Account already exists, fetching it...")
        resp = httpx.get(
            f"{API_URL}/v1/account",
            headers={"Authorization": f"Bearer {id_token}"},
            timeout=30,
        )
        if resp.status_code != 200:
            print(f"  ERROR fetching account: {resp.status_code} — {resp.text}")
            sys.exit(1)
        return resp.json()

    if resp.status_code != 201:
        print(f"  ERROR creating account: {resp.status_code} — {resp.text}")
        sys.exit(1)

    return resp.json()


def create_api_key(id_token: str) -> dict:
    """Generate an API key via POST /v1/account/keys."""
    resp = httpx.post(
        f"{API_URL}/v1/account/keys",
        headers={
            "Authorization": f"Bearer {id_token}",
            "Content-Type": "application/json",
        },
        json={
            "label": "bootstrap-mcp",
            "tier": "free",
        },
        timeout=30,
    )

    if resp.status_code != 201:
        print(f"  ERROR creating API key: {resp.status_code} — {resp.text}")
        sys.exit(1)

    return resp.json()


def main():
    print("=" * 60)
    print("lightpaper.org — Account Bootstrap")
    print("=" * 60)
    print(f"\n  API URL:     {API_URL}")
    print(f"  Firebase:    {FIREBASE_PROJECT_ID}")
    print(f"  Email:       {BOOTSTRAP_EMAIL}")
    print(f"  Handle:      {BOOTSTRAP_HANDLE}")

    # Step 0: Health check
    print("\n[0/5] Health check...")
    try:
        resp = httpx.get(f"{API_URL}/health", timeout=10)
        if resp.status_code == 200:
            print("  OK")
        else:
            print(f"  WARNING: /health returned {resp.status_code}")
    except httpx.ConnectError:
        print(f"  ERROR: Cannot connect to {API_URL}")
        sys.exit(1)

    # Step 1: Initialize Firebase
    print("\n[1/5] Initializing Firebase Admin SDK...")
    init_firebase()
    print("  OK")

    # Step 2: Create or get Firebase user
    print("\n[2/5] Creating Firebase user...")
    uid = get_or_create_firebase_user(BOOTSTRAP_EMAIL, BOOTSTRAP_DISPLAY_NAME)

    # Step 3: Generate custom token → exchange for ID token
    print("\n[3/5] Generating authentication token...")
    custom_token = generate_custom_token(uid)
    print("  Custom token generated")
    id_token = exchange_custom_token_for_id_token(custom_token)
    print("  ID token obtained")

    # Step 4: Create lightpaper account
    print("\n[4/5] Creating lightpaper account...")
    account = create_account(id_token)
    print(f"  Account ID: {account['id']}")
    print(f"  Handle:     @{account.get('handle', 'none')}")
    print(f"  Gravity:    Level {account.get('gravity_level', 0)}")

    # Step 5: Generate API key
    print("\n[5/5] Generating API key...")
    key_data = create_api_key(id_token)
    api_key = key_data["key"]
    print(f"  Key prefix: {key_data['prefix']}")
    print(f"  Label:      {key_data.get('label', 'none')}")

    # Summary
    print("\n" + "=" * 60)
    print("SUCCESS! Save these credentials:")
    print("=" * 60)
    print(f"\n  API Key: {api_key}")
    print("\n  For MCP server:")
    print(f"    export LIGHTPAPER_BASE_URL={API_URL}")
    print(f"    export LIGHTPAPER_API_KEY={api_key}")
    print("\n  For curl:")
    print(f'    curl -H "Authorization: Bearer {api_key}" {API_URL}/v1/account')
    print()

    # Also write to a local file for convenience
    secrets_path = os.path.join(os.path.dirname(__file__), ".bootstrap-secrets.json")
    with open(secrets_path, "w") as f:
        json.dump(
            {
                "api_key": api_key,
                "api_url": API_URL,
                "account_id": account["id"],
                "firebase_uid": uid,
                "handle": account.get("handle"),
            },
            f,
            indent=2,
        )
    print(f"  Secrets saved to: {secrets_path}")
    print("  (Add this file to .gitignore!)")


if __name__ == "__main__":
    main()
