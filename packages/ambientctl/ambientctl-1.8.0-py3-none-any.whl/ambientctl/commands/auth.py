import click
import requests

from ambientctl.config import settings


def check_status():
    url = f"{settings.ambient_server}/auth/status"
    try:
        response = requests.get(url)
        response.raise_for_status()
        click.echo(response.json()["status"])
    except Exception as e:
        click.echo(f"error: {e}")
        return


def refresh_token():
    url = f"{settings.ambient_server}/auth/refresh"
    try:
        response = requests.post(url)
        response.raise_for_status()
        click.echo(response.json())
    except Exception as e:
        click.echo(f"error: {e}")
        return


def authorize_node():
    try:
        url = f"{settings.ambient_server}/auth/request"
        response = requests.post(url)
        response.raise_for_status()
        click.echo("Please visit the following URL to authorize the node:\n\n")
        click.echo(
            response.json().get("verification_uri_complete", None) or response.json()
        )
        click.echo("\n")
        url = f"{settings.ambient_server}/auth"
        response = requests.post(url)
        response.raise_for_status()
        click.echo(response.json())
    except Exception as e:
        click.echo(f"error: {e}")


def cycle_certificate():
    url = f"{settings.ambient_server}/auth/cycle-certificate"
    try:
        response = requests.post(url)
        response.raise_for_status()
        click.echo(response.json())
    except Exception as e:
        click.echo(f"error: {e}")
        return
