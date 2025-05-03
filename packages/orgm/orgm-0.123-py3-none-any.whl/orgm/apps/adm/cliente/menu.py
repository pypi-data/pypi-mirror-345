from rich.console import Console
from rich.prompt import Prompt
import questionary
import sys
import subprocess

console = Console()

def menu():
    """Menú interactivo para comandos de IA."""
    
    console.print("[bold blue]===== Menú de Cliente =====[/bold blue]")
    
    opciones = [
        {"name": "🤖 Opcion 1", "value": "ai prompt"},
        {"name": "🔍 Ayuda", "value": "client -h"},
        {"name": "❌ Salir", "value": "exit"}
    ]
    
    try:
        seleccion = questionary.select(
            "Seleccione una opción:",
            choices=[opcion["name"] for opcion in opciones],
            use_indicator=True
        ).ask()
        
        if seleccion is None:  # Usuario presionó Ctrl+C
            return "exit"
            
        # Obtener el valor asociado a la selección
        comando = next(opcion["value"] for opcion in opciones if opcion["name"] == seleccion)
        
        if comando == "exit":
            console.print("[yellow]Saliendo...[/yellow]")
            sys.exit(0)

        elif comando == "client -h":
            subprocess.run(["orgm", "client", "-h"])
            return menu()
            
    except Exception as e:
        console.print(f"[bold red]Error en el menú: {e}[/bold red]")
        return "error"