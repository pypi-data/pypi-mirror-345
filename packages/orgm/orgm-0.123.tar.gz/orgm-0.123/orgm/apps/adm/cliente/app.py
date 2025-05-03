import typer
from typing import List
from rich.console import Console

# Importar la función que define los argumentos y la lógica
from orgm.apps.ai.prompt import ai_prompt
# Crear consola para salida con Rich
console = Console()

# Crear aplicación Typer para comandos de IA
app = typer.Typer(help="Comandos para interactuar con servicios de IA")

# Registrar ai_prompt directamente con el nombre 'prompt'
# El docstring de ai_prompt se usará como ayuda
app.command(name="prompt")(ai_prompt)



@app.callback(invoke_without_command=True)
def ai_callback(ctx: typer.Context):
    """
    Operaciones relacionadas con la IA. Si no se especifica un subcomando, muestra un menú interactivo.
    """
    if ctx.invoked_subcommand is None:
        # Ejecutar el menú de IA
        from orgm.apps.ai.menu import menu
        menu()

if __name__ == "__main__":
    app()