import typer
from typing import Dict
from hotmart_python.api import Authenticator
from tests.utils.utils import read_config

app = typer.Typer()


@app.command()
def authenticate():
    """
    Testa o método authenticate da classe Authenticator.
    """
    try:
        config: Dict = read_config()
        client_id: str = config['client_id']
        client_secret: str = config['client_secret']
        basic: str = config['basic']
        authenticator: Authenticator = Authenticator(client_id, client_secret, basic)
        authenticator.authenticate()
        typer.echo("PASS: Successful authentication")
    except Exception as e:
        typer.echo(f"Erro: {e}")
        raise typer.Exit(code=1)


@app.command()
def say_hi(name):
    print(f"Hello {name}")


if __name__ == "__main__":
    app()
