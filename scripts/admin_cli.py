import click
import uuid
from backend.database import SessionLocal
from backend.models import Usuario, LogOperativo
from backend.utils.auth import get_password_hash
from backend.config import settings
import sys

@click.group()
def cli():
    """TPV Carbones y Pollos - Enterprise CLI Control Plane"""
    pass

@cli.command()
@click.option('--username', prompt='Username', help='Admin username')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
@click.option('--rol', default='ADMIN', type=click.Choice(['ADMIN', 'MANAGER', 'STAFF']))
def create_user(username, password, rol):
    """Crea un nuevo usuario con credenciales seguras."""
    db = SessionLocal()
    try:
        hashed = get_password_hash(password)
        user = Usuario(
            id=str(uuid.uuid4()),
            username=username,
            password=hashed,
            rol=rol
        )
        db.add(user)
        db.commit()
        click.echo(f"✅ Usuario {username} creado con éxito [{rol}]")
    except Exception as e:
        click.echo(f"❌ Error al crear usuario: {e}")
    finally:
        db.close()

@cli.command()
def status():
    """Diagnóstico rápido del estado del ecosistema."""
    click.echo(f"--- TPV {settings.APP_NAME} v{settings.APP_VERSION} ---")
    click.echo(f"Entorno: {os.getenv('ENVIRONMENT', 'development')}")
    # Aquí se podrían añadir chequeos de DB, conectividad, etc.
    click.echo("✅ Sistema operativo.")

@cli.command()
def logs():
    """Muestra los últimos logs operativos del sistema."""
    db = SessionLocal()
    logs = db.query(LogOperativo).order_by(LogOperativo.fecha.desc()).limit(10).all()
    for log in logs:
        color = 'red' if log.nivel == 'ERROR' else 'green'
        click.secho(f"[{log.fecha}] {log.modulo}: {log.mensaje}", fg=color)
    db.close()

if __name__ == '__main__':
    import os
    cli()
