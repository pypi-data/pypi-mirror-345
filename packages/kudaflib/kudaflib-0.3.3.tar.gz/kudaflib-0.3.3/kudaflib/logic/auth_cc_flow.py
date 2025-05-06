import httpx
from datetime import datetime, timedelta
from json import JSONDecodeError


def get_access_token_cc_flow(
    client_id: str,
    client_secret: str,
):
    """
    Feide OAuth2 step 1: Access Token POST Request
    """
    import base64

    credentials = f"{client_id}:{client_secret}"
    b_creds = base64.b64encode(bytes(credentials, 'utf-8')) # bytes
    base64_str_creds = b_creds.decode('utf-8') # convert bytes to string

    basic_auth_headers = {
        "Authorization": f"Basic {base64_str_creds}",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    request_body = {
        "grant_type": "client_credentials",
    }

    try:
        response = httpx.post(
                url="https://auth.dataporten.no/oauth/token",
                headers=basic_auth_headers,
                data=request_body
            )
        response.raise_for_status()
    except httpx.TimeoutException as e:
        msg = f"A Timeout error occurred while validating token issuer signature at: {e.request.url!r}",
        print(msg)
    except httpx.NetworkError as e:
        msg = f"A Network error occurred while validating token issuer signature at: {e.request.url!r}",
        print(msg)
    except httpx.HTTPStatusError as e:
        msg = f"Error code: {e.response.status_code} Msg: {e.response.json()}",
        print(msg)
    except Exception as e:
        msg = f"An exception occurred validating token issuer signature: {e.args}"
        print(msg)

    try:
        jresp = response.json()
    except JSONDecodeError:
        jresp = {
            "error": response.status_code,
            "error_description": response.text,
        }

    if response.status_code == 200: 
        return jresp.get("access_token"), jresp.get("expires_in")
    else:
        return jresp


def token_exchange_cc_flow(
    access_token: str,
    client_id: str,
    client_secret: str,
    feide_datasources_audience: str,
    ):
    """
    Feide OAuth2 login step 2: Token Exchange POST Request
    """
    basic_auth_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    token_exchange_body = {
        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
        "audience": feide_datasources_audience, 
        "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
        "subject_token": access_token,
        "client_id": client_id,
        "client_secret": client_secret,
    }
    
    try:
        response = httpx.post(
                url="https://auth.dataporten.no/oauth/token",
                headers=basic_auth_headers,
                data=token_exchange_body
            )
        response.raise_for_status()
    except httpx.TimeoutException as e:
        msg = f"A Timeout error occurred while validating token issuer signature at: {e.request.url!r}",
        print(msg)
    except httpx.NetworkError as e:
        msg = f"A Network error occurred while validating token issuer signature at: {e.request.url!r}",
        print(msg)
    except httpx.HTTPStatusError as e:
        msg = f"Error code: {e.response.status_code} Msg: {e.response.json()}",
        print(msg)
    except Exception as e:
        msg = f"An exception occurred validating token issuer signature: {e.args}"
        print(msg)

    try:
        jresp = response.json()
    except JSONDecodeError:
        jresp = {
            "error_code": response.status_code,
            "error_msg": response.text,
        }

    if response.status_code == 200: 
        jwt_token = jresp.get("access_token")
        jwt_token_expires = datetime.now() + timedelta(seconds=jresp.get('expires_in'))

        # 
        return jwt_token, jwt_token_expires
    else:
        return jresp, None
