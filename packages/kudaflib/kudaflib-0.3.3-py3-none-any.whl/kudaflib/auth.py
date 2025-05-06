import typer
import os
import dotenv
from datetime import datetime, timedelta
from rich.console import Console
from typing_extensions import Annotated
from pathlib import Path
from kudaflib.logic.auth_cc_flow import get_access_token_cc_flow, token_exchange_cc_flow


dotenv.load_dotenv()
console = Console()
    
app = typer.Typer(
    pretty_exceptions_enable=True,
    pretty_exceptions_short=False,
    pretty_exceptions_show_locals=True,
)


@app.callback()
def callback():
    """
    Kudaf Metadata CLI Tools
    """
    ...


@app.command()
def newclient_ccflow_token(
    client_id: Annotated[str, typer.Option(
        help="Client ID for the Client Credentials Flow"
    )] = os.environ.get('client_id', ""),
    client_secret: Annotated[str, typer.Option(
        help="Client Secret for the Client Credentials Flow"
    )] = os.environ.get('client_secret', ""),
    datasource_id: Annotated[str, typer.Option(
        help="Datasource ID for the Feide Datasource"
    )] = os.environ.get('datasource_id', ""),
):
    """
    Generate a new Access Token and JWT Token for a new Feide Datasource 
    (overwrites the existing .state file for the previous datasource)
    The three parameters are required to generate a new JWT Token, 
    they can be passed as arguments or set as environment variables
    """
    # Open .state file to read from it and create it if it doesn't exist
    filename = Path(".state")
    filename.touch(exist_ok=True)
    with open(".state", "r+") as f:
        # Clear file contents, if any
        f.truncate(0)

    ccflow_token(client_id=client_id, client_secret=client_secret, datasource_id=datasource_id)


@app.command()
def ccflow_token(
    client_id: Annotated[str, typer.Option(
        help="Client ID for the Client Credentials Flow"
    )] = os.environ.get('client_id', ""),
    client_secret: Annotated[str, typer.Option(
        help="Client Secret for the Client Credentials Flow"
    )] = os.environ.get('client_secret', ""),
    datasource_id: Annotated[str, typer.Option(
        help="Datasource ID for the Feide Datasource"
    )] = os.environ.get('datasource_id', ""),
):
    """
    Generate a new JWT Token using the existing Access Token 
    (if still valid, otherwise generates a new one)
    The three parameters are required to generate a new JWT Token, 
    they can be passed as arguments or set as environment variables
    """
    FEIDE_DATASOURCES_URL: str = 'https://n.feide.no/datasources/'

    FEIDE_DATASOURCES_AUDIENCE: str = FEIDE_DATASOURCES_URL + datasource_id

    # Open a file called .state, create it if it doesn't exist
    access_code = None
    state = None
    # Open .state file to read from it and create it if it doesn't exist
    filename = Path(".state")
    filename.touch(exist_ok=True)
    with open(".state", "r+") as f:
        # Read the first line of the file, if it exists, check if it's empty
        try:
            state = f.readline().strip()
        except Exception as e:
            print(f"Error reading state file: {e.args}")
            state = None
        
        if state:
            access_code, expires = state.split(",")
            if datetime.now() < datetime.fromisoformat(expires):
                print(f"Access code: {access_code} is still valid")
            else:
                state = None

        if not state:
            access_code, expires_in = get_access_token_cc_flow(
                client_id=client_id,
                client_secret=client_secret,
            )
            with open(".state", "w") as f:
                print(f"Writing new Access Code: {access_code}")
                # Overwrite the file with the new access code and expiration date
                new_dt = datetime.now() + timedelta(seconds=expires_in)
                f.write(f"{access_code},{new_dt.isoformat()}")

    if access_code is None:
        print("Sorry, an error has occured: Access Token did not complete successfully")
        exit()  # Exit the program

    # If the access code is still valid, use it to get a JWT token
    jwt_token, expires = token_exchange_cc_flow(
        access_token=access_code,
        client_id=client_id,
        client_secret=client_secret,
        feide_datasources_audience=FEIDE_DATASOURCES_AUDIENCE,
    )
    if expires is None: # If the token exchange fails
        print("Sorry, an error has occured: Token Exchange did not complete successfully")
    else:
        print(f"JWT: {jwt_token}")
        print(f"Expires: {expires}")   
    