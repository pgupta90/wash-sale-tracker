#!/usr/bin/env python3
import sys
import os
import uuid
import pickle
import time
import requests
import robin_stocks.robinhood as r
from config import load_config

CLIENT_ID = "c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS"
TOKEN_URL = "https://api.robinhood.com/oauth2/token/"
PATHFINDER_USER_MACHINE_URL = "https://api.robinhood.com/pathfinder/user_machine/"
PATHFINDER_INQUIRY_URL = "https://api.robinhood.com/pathfinder/inquiries/{}/user_view/"
PROMPT_STATUS_URL = "https://api.robinhood.com/push/{}/get_prompts_status/"
DEVICE_TOKEN_FILE = os.path.expanduser("~/.tokens/robinhood_device_token")
PICKLE_FILE = os.path.expanduser("~/.tokens/robinhood.pickle")


def get_device_token():
    os.makedirs(os.path.dirname(DEVICE_TOKEN_FILE), exist_ok=True)
    if os.path.exists(DEVICE_TOKEN_FILE):
        with open(DEVICE_TOKEN_FILE) as f:
            token = f.read().strip()
            if token:
                return token
    token = str(uuid.uuid4())
    with open(DEVICE_TOKEN_FILE, "w") as f:
        f.write(token)
    return token


def save_session(token_data: dict, device_token: str):
    os.makedirs(os.path.expanduser("~/.tokens"), exist_ok=True)
    session = {
        "token_type": token_data.get("token_type", "Bearer"),
        "access_token": token_data["access_token"],
        "refresh_token": token_data.get("refresh_token", ""),
        "expires_in": token_data.get("expires_in", 86400),
        "scope": token_data.get("scope", "internal"),
        "detail": "logged in using pickle",
        "backup_code": None,
        "device_token": device_token,
    }
    with open(PICKLE_FILE, "wb") as f:
        pickle.dump(session, f)


def setup_robin_stocks_session(access_token: str, token_type: str = "Bearer"):
    r.helper.SESSION.headers.update({"Authorization": f"{token_type} {access_token}"})


def login_once(base_payload: dict, headers: dict):
    res = requests.post(TOKEN_URL, data=base_payload, headers=headers, timeout=30)
    try:
        return res.json()
    except Exception:
        return {"detail": res.text, "status_code": res.status_code}


def get_verification_status(inquiry_id: str, retries: int = 5):
    url = PATHFINDER_INQUIRY_URL.format(inquiry_id)
    last_error = None

    for attempt in range(retries):
        try:
            res = requests.get(url, timeout=30)
            if res.status_code >= 500:
                last_error = f"{res.status_code} {res.text}"
                print(f"[debug] inquiry GET failed ({attempt + 1}/{retries}): {last_error}")
                time.sleep(5 * (attempt + 1))
                continue

            res.raise_for_status()
            return res.json()

        except requests.RequestException as e:
            last_error = str(e)
            print(f"[debug] inquiry GET exception ({attempt + 1}/{retries}): {e}")
            time.sleep(5 * (attempt + 1))

    raise RuntimeError(f"Inquiry endpoint unavailable after retries: {last_error}")


def wait_for_verification(device_token: str, workflow_id: str, timeout_seconds: int = 300):
    payload = {
        "device_id": device_token,
        "flow": "suv",
        "input": {"workflow_id": workflow_id},
    }

    res = requests.post(PATHFINDER_USER_MACHINE_URL, json=payload, timeout=30)
    res.raise_for_status()
    machine_data = res.json()

    machine_id = machine_data.get("id") or machine_data.get("machine_id") or workflow_id
    print(f"[debug] user_machine response: {machine_data}")
    print(f"[debug] polling inquiry for machine_id={machine_id}")

    start = time.time()
    last_status = None
    validated_prompt_id = None

    while time.time() - start < timeout_seconds:
        time.sleep(5)

        try:
            data = get_verification_status(machine_id)
        except Exception as e:
            print(f"[debug] inquiry poll failed: {e}")
            continue

        workflow = data.get("verification_workflow") or {}
        last_status = workflow.get("workflow_status")
        challenge = data.get("context", {}).get("sheriff_challenge", {}) or {}

        print(f"[debug] inquiry response: {data}")
        print(f"[debug] workflow_status={last_status}, challenge={challenge}")

        if last_status == "workflow_status_approved":
            print("[debug] verification approved")
            return validated_prompt_id or True

        if challenge.get("status") == "validated":
            validated_prompt_id = challenge.get("id") or validated_prompt_id
            print("[debug] challenge validated")
            return validated_prompt_id or True

        if challenge.get("type") == "prompt":
            prompt_id = challenge.get("id") or machine_id
            prompt_res = requests.get(PROMPT_STATUS_URL.format(prompt_id), timeout=30)
            prompt_data = prompt_res.json() if prompt_res.ok else {"error": prompt_res.text}
            print(f"[debug] prompt status response: {prompt_data}")

            if prompt_res.ok:
                prompt_status = prompt_data.get("challenge_status") or prompt_data.get("status")
                if prompt_status == "validated":
                    validated_prompt_id = prompt_id
                    print("[debug] prompt validated — advancing Pathfinder state machine...")

                    # Tell Pathfinder the challenge is complete and advance the workflow
                    advance_url = PATHFINDER_INQUIRY_URL.format(machine_id)
                    advance_res = requests.post(
                        advance_url,
                        json={"sequence": 0, "user_input": {"status": "continue"}},
                        timeout=30,
                    )
                    print(f"[debug] pathfinder advance: status={advance_res.status_code} body={advance_res.text[:300]}")

                    # The advance POST response itself may confirm approval
                    try:
                        advance_data = advance_res.json()
                        tc = advance_data.get("type_context") or {}
                        if tc.get("result") == "workflow_status_approved":
                            print("[debug] workflow approved (confirmed in advance response)")
                            return validated_prompt_id
                    except Exception:
                        pass

                    # 410 Gone on the inquiry means the machine was consumed = approved
                    if advance_res.status_code == 410:
                        print("[debug] workflow approved (410 Gone = machine consumed)")
                        return validated_prompt_id

                    # Fallback: poll briefly for approval
                    print("[debug] polling for workflow_status_approved...")
                    deadline = time.time() + 30
                    while time.time() < deadline:
                        time.sleep(5)
                        try:
                            check = get_verification_status(machine_id)
                        except Exception as e:
                            # 410 Gone = machine consumed = approved
                            if "410" in str(e) or "Gone" in str(e):
                                print("[debug] workflow approved (410 Gone in poll)")
                                return validated_prompt_id
                            print(f"[debug] approval poll error: {e}")
                            continue
                        print(f"[debug] approval poll response: {check}")
                        tc = check.get("type_context") or {}
                        wf = check.get("verification_workflow") or {}
                        if (
                            tc.get("result") == "workflow_status_approved"
                            or wf.get("workflow_status") == "workflow_status_approved"
                            or check.get("state_name") == "Success"
                        ):
                            print("[debug] workflow approved!")
                            return validated_prompt_id
                    print("[debug] proceeding after advance (approval assumed)")
                    return validated_prompt_id

                if prompt_status == "expired":
                    raise RuntimeError(
                        "Challenge expired — the push notification timed out.\n"
                        "Delete ~/.tokens/robinhood_device_token and re-run to get a fresh one."
                    )

        if last_status == "workflow_status_internal_pending":
            continue

    raise TimeoutError(f"Verification timed out. Last status: {last_status}")


def login_with_retry(base_payload: dict, headers: dict, retries: int = 8):
    last_data = None
    print(
        f"[debug] login_with_retry: challenge header="
        f"{'SET: ' + headers.get('X-ROBINHOOD-CHALLENGE-RESPONSE-ID') if headers.get('X-ROBINHOOD-CHALLENGE-RESPONSE-ID') else 'NOT SET'}"
    )

    for attempt in range(retries):
        print(f"[debug] login_with_retry attempt {attempt + 1}/{retries}")
        data = login_once(base_payload, headers)
        last_data = data

        print(f"[debug] login retry {attempt + 1} response keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")
        print(f"[debug] login retry {attempt + 1} response: {data}")

        if "access_token" in data:
            print(f"[debug] got access_token on attempt {attempt + 1}")
            return data

        if data.get("mfa_required"):
            print(f"[debug] mfa_required on attempt {attempt + 1} — returning for TOTP prompt")
            return data

        wf = data.get("verification_workflow") or {}
        wf_status = wf.get("workflow_status")

        if wf_status == "workflow_status_internal_pending":
            wait = min(5 * (attempt + 1), 20)
            print(f"[debug] still pending; sleeping {wait}s before retry")
            time.sleep(wait)
            continue

        if "verification_workflow" in data:
            print(f"[debug] unexpected workflow status={wf_status}, returning")
            return data

        print(f"[debug] unrecognised response shape on attempt {attempt + 1}, returning")
        return data

    print(f"[debug] exhausted all retries, last response: {last_data}")
    return last_data


def main():
    config = load_config()
    creds = config.get("robinhood", {})
    username = creds.get("username", "")
    password = creds.get("password", "")

    if not username or username == "your_email@example.com":
        print("ERROR: Update config.yaml with your real Robinhood credentials first.")
        sys.exit(1)

    # Keep device token across runs so Robinhood recognises this as a trusted device

    device_token = get_device_token()

    base_payload = {
        "client_id": CLIENT_ID,
        "expires_in": 86400,
        "grant_type": "password",
        "password": password,
        "scope": "internal",
        "username": username,
        "device_token": device_token,
        "challenge_type": "email",
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    print(f"Logging in as {username}...")
    data = login_once(base_payload, headers)
    print(f"[debug] initial response keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")
    print(f"[debug] initial response: {data}")

    validated_challenge_ids = set()

    for round_num in range(5):
        if "access_token" in data:
            break

        if data.get("mfa_required"):
            print(f"[debug] round {round_num + 1}: mfa_required")
            mfa_code = input("Enter your 6-digit Google Authenticator code: ").strip()
            totp_payload = dict(base_payload)
            totp_payload["mfa_code"] = mfa_code
            data = login_once(totp_payload, headers)
            print(f"[debug] post-MFA response keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")
            print(f"[debug] post-MFA response: {data}")
            continue

        if "verification_workflow" in data:
            wf = data["verification_workflow"] or {}
            workflow_id = wf.get("id")
            wf_status = wf.get("workflow_status")
            print(f"[debug] round {round_num + 1}: verification_workflow id={workflow_id} status={wf_status}")

            if not workflow_id:
                print("[debug] no workflow_id, cannot proceed")
                break

            if round_num == 0:
                print("Robinhood requested device verification. Approve it in the Robinhood app.")
                try:
                    challenge_id = wait_for_verification(device_token, workflow_id, timeout_seconds=300)
                except TimeoutError as e:
                    print(f"\n[debug] Timed out waiting for push approval: {e}")
                    print("Authentication stuck — push notification was not approved in time.")
                    sys.exit(1)
                except RuntimeError as e:
                    print(f"\n{e}")
                    sys.exit(1)

                print(f"[debug] wait_for_verification returned: {challenge_id!r} (type={type(challenge_id).__name__})")
                if challenge_id and isinstance(challenge_id, str):
                    validated_challenge_ids.add(challenge_id)
                    headers["X-ROBINHOOD-CHALLENGE-RESPONSE-ID"] = challenge_id
                    print(f"[debug] set challenge header: {challenge_id}")

                data = login_once(base_payload, headers)
                print(f"[debug] post-respond retry response: {data}")

                if data.get("verification_workflow", {}).get("workflow_status") == "workflow_status_internal_pending":
                    print("[debug] still pending after respond — retrying with backoff")
                    for attempt in range(6):
                        wait_secs = 10 * (attempt + 1)
                        print(f"[debug] sleeping {wait_secs}s before retry {attempt + 1}/6...")
                        time.sleep(wait_secs)
                        data = login_once(base_payload, headers)
                        print(f"[debug] retry {attempt + 1} response: {data}")
                        wf2 = data.get("verification_workflow") or {}
                        if "access_token" in data or wf2.get("workflow_status") != "workflow_status_internal_pending":
                            break

                print(f"[debug] post-verification round {round_num + 1} response keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                print(f"[debug] post-verification round {round_num + 1} response: {data}")
                continue

            print(f"[debug] round {round_num + 1}: waiting for Robinhood to process approval, retrying token endpoint")
            advanced = False
            for attempt in range(6):
                wait_secs = 10 * (attempt + 1)
                print(f"[debug] sleeping {wait_secs}s before retry {attempt + 1}/6...")
                time.sleep(wait_secs)
                data = login_once(base_payload, headers)
                print(f"[debug] retry {attempt + 1} response: {data}")
                if "access_token" in data or data.get("mfa_required"):
                    advanced = True
                    break
                wf2 = data.get("verification_workflow") or {}
                if wf2.get("workflow_status") != "workflow_status_internal_pending":
                    advanced = True
                    break

            if not advanced:
                print("\nAuthentication stuck — Robinhood's workflow did not advance after retries.")
                sys.exit(1)

            print(f"[debug] post-verification round {round_num + 1} response keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")
            print(f"[debug] post-verification round {round_num + 1} response: {data}")
            continue

        if "challenge" in data:
            challenge = data["challenge"] or {}
            challenge_id = challenge.get("id")
            challenge_type = challenge.get("challenge_type") or challenge.get("type")
            print(f"[debug] round {round_num + 1}: challenge type={challenge_type} id={challenge_id}")
            if challenge_id:
                input("Approve/respond in the Robinhood app, then press Enter here to retry...")
                headers["X-ROBINHOOD-CHALLENGE-RESPONSE-ID"] = challenge_id
                data = login_once(base_payload, headers)
                print(f"[debug] post-challenge response: {data}")
                continue

        print(f"[debug] round {round_num + 1}: unrecognised response shape {list(data.keys()) if isinstance(data, dict) else data}")
        break

    if "access_token" not in data:
        wf = data.get("verification_workflow") or {}
        if wf.get("workflow_status") == "workflow_status_internal_pending":
            print("Authentication is still pending on Robinhood's side. Re-run in a minute.")
        else:
            print(f"Authentication failed: {data.get('detail', data)}")
        sys.exit(1)

    save_session(data, device_token)

    print()
    print("Authentication successful! Session saved to ~/.tokens/robinhood.pickle")
    print("The backend will now log in automatically on every restart.")
    print()
    print("Start the backend:  python3 -m backend.main")


if __name__ == "__main__":
    main()