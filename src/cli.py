"""Command-line interface for File Oracle."""

import asyncio
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.syntax import Syntax
from rich.table import Table

from src.config import settings
from src.oracle import FileOracle

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main() -> None:
    """File Oracle - AI-powered file reading and processing application."""
    pass


@main.command()
@click.option(
    "--directory",
    "-d",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Directory to watch for files",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    help="Output directory for generated files",
)
@click.option(
    "--provider",
    "-p",
    type=click.Choice(["nvidia", "openrouter"]),
    help="AI provider to use",
)
def interactive(
    directory: Path | None,
    output: Path | None,
    provider: str | None,
) -> None:
    """Start interactive mode with the AI assistant."""
    asyncio.run(_interactive_mode(directory, output, provider))


async def _interactive_mode(
    directory: Path | None,
    output: Path | None,
    provider: str | None,
) -> None:
    """Run interactive mode."""
    console.print(
        Panel.fit(
            "[bold cyan]File Oracle[/bold cyan]\n"
            "AI-powered file reading and processing",
            border_style="cyan",
        )
    )

    oracle = FileOracle(
        watch_directory=directory,
        output_directory=output,
        ai_provider=provider,
    )

    console.print(f"\n[green]✓[/green] Watch directory: {oracle.watch_directory}")
    console.print(f"[green]✓[/green] Output directory: {oracle.output_directory}")
    console.print(f"[green]✓[/green] AI Provider: {oracle.assistant.provider}")
    console.print(f"[green]✓[/green] Model: {oracle.assistant.model}\n")

    history: list[dict[str, str]] = []

    console.print("[yellow]Commands:[/yellow]")
    console.print("  /list - List files in watch directory")
    console.print("  /read <pattern> - Read files matching pattern")
    console.print("  /generate <filename> - Generate a new file")
    console.print("  /modify <filename> - Modify an existing file")
    console.print("  /task - Execute a complex task")
    console.print("  /quit - Exit interactive mode\n")

    while True:
        try:
            user_input = Prompt.ask("[bold blue]You[/bold blue]")

            if not user_input.strip():
                continue

            if user_input.strip() == "/quit":
                console.print("[yellow]Goodbye![/yellow]")
                break

            if user_input.strip() == "/list":
                files = oracle.list_files()
                if files:
                    table = Table(title="Files in Watch Directory")
                    table.add_column("File", style="cyan")
                    table.add_column("Size", style="green")
                    for file in files:
                        size = file.stat().st_size
                        table.add_row(file.name, f"{size:,} bytes")
                    console.print(table)
                else:
                    console.print("[yellow]No files found[/yellow]")
                continue

            if user_input.startswith("/read"):
                parts = user_input.split(maxsplit=1)
                pattern = parts[1] if len(parts) > 1 else "*"
                files_content = await oracle.read_files(pattern)
                if files_content:
                    for file_path, content in files_content.items():
                        console.print(f"\n[cyan]File: {file_path}[/cyan]")
                        syntax = Syntax(content[:500], "text", theme="monokai")
                        console.print(syntax)
                        if len(content) > 500:
                            console.print("[dim]...(truncated)[/dim]")
                else:
                    console.print("[yellow]No files found[/yellow]")
                continue

            if user_input.startswith("/generate"):
                parts = user_input.split(maxsplit=1)
                if len(parts) < 2:
                    console.print("[red]Usage: /generate <filename>[/red]")
                    continue

                filename = parts[1]
                description = Prompt.ask("Describe what to generate")

                with console.status("[bold green]Generating file..."):
                    file_path = await oracle.generate_file(description, filename)

                console.print(f"[green]✓[/green] Generated: {file_path}")
                continue

            if user_input.startswith("/modify"):
                parts = user_input.split(maxsplit=1)
                if len(parts) < 2:
                    console.print("[red]Usage: /modify <filename>[/red]")
                    continue

                filename = parts[1]
                modification = Prompt.ask("Describe the modification")

                with console.status("[bold green]Modifying file..."):
                    file_path = await oracle.modify_file(filename, modification)

                console.print(f"[green]✓[/green] Modified: {file_path}")
                continue

            if user_input.startswith("/task"):
                task_description = Prompt.ask("Describe the task")

                with console.status("[bold green]Executing task..."):
                    files = await oracle.execute_task(task_description)

                if files:
                    console.print(f"[green]✓[/green] Created/modified {len(files)} file(s):")
                    for filename, path in files.items():
                        console.print(f"  - {path}")
                else:
                    console.print("[yellow]No files were created[/yellow]")
                continue

            # Regular chat
            with console.status("[bold green]Thinking..."):
                response = await oracle.chat(user_input, history)

            console.print(f"[bold green]Assistant[/bold green]: {response}\n")

            # Update history
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": response})

        except KeyboardInterrupt:
            console.print("\n[yellow]Use /quit to exit[/yellow]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


@main.command()
@click.argument("request")
@click.option(
    "--directory",
    "-d",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Directory to watch for files",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    help="Output directory for generated files",
)
@click.option(
    "--provider",
    "-p",
    type=click.Choice(["nvidia", "openrouter"]),
    help="AI provider to use",
)
@click.option(
    "--no-context",
    is_flag=True,
    help="Don't include file contents as context",
)
def ask(
    request: str,
    directory: Path | None,
    output: Path | None,
    provider: str | None,
    no_context: bool,
) -> None:
    """Ask a question or make a request."""
    asyncio.run(_ask_command(request, directory, output, provider, not no_context))


async def _ask_command(
    request: str,
    directory: Path | None,
    output: Path | None,
    provider: str | None,
    include_context: bool,
) -> None:
    """Execute ask command."""
    oracle = FileOracle(
        watch_directory=directory,
        output_directory=output,
        ai_provider=provider,
    )

    with console.status("[bold green]Processing request..."):
        response = await oracle.process_request(request, include_files=include_context)

    console.print(Panel(response, title="Response", border_style="green"))


@main.command()
@click.argument("description")
@click.argument("filename")
@click.option(
    "--language",
    "-l",
    help="Programming language",
)
@click.option(
    "--directory",
    "-d",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Directory to watch for files",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    help="Output directory for generated files",
)
@click.option(
    "--provider",
    "-p",
    type=click.Choice(["nvidia", "openrouter"]),
    help="AI provider to use",
)
def generate(
    description: str,
    filename: str,
    language: str | None,
    directory: Path | None,
    output: Path | None,
    provider: str | None,
) -> None:
    """Generate a new file."""
    asyncio.run(_generate_command(description, filename, language, directory, output, provider))


async def _generate_command(
    description: str,
    filename: str,
    language: str | None,
    directory: Path | None,
    output: Path | None,
    provider: str | None,
) -> None:
    """Execute generate command."""
    oracle = FileOracle(
        watch_directory=directory,
        output_directory=output,
        ai_provider=provider,
    )

    with console.status("[bold green]Generating file..."):
        file_path = await oracle.generate_file(description, filename, language)

    console.print(f"[green]✓[/green] Generated: {file_path}")


@main.command()
@click.argument("filename")
@click.argument("modification")
@click.option(
    "--save-as",
    help="Save as a different filename",
)
@click.option(
    "--directory",
    "-d",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Directory to watch for files",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    help="Output directory for generated files",
)
@click.option(
    "--provider",
    "-p",
    type=click.Choice(["nvidia", "openrouter"]),
    help="AI provider to use",
)
def modify(
    filename: str,
    modification: str,
    save_as: str | None,
    directory: Path | None,
    output: Path | None,
    provider: str | None,
) -> None:
    """Modify an existing file."""
    asyncio.run(_modify_command(filename, modification, save_as, directory, output, provider))


async def _modify_command(
    filename: str,
    modification: str,
    save_as: str | None,
    directory: Path | None,
    output: Path | None,
    provider: str | None,
) -> None:
    """Execute modify command."""
    oracle = FileOracle(
        watch_directory=directory,
        output_directory=output,
        ai_provider=provider,
    )

    with console.status("[bold green]Modifying file..."):
        file_path = await oracle.modify_file(filename, modification, save_as)

    console.print(f"[green]✓[/green] Modified: {file_path}")


@main.command()
@click.option(
    "--directory",
    "-d",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Directory to list files from",
)
@click.option(
    "--pattern",
    default="*",
    help="Glob pattern to match files",
)
def list_files(directory: Path | None, pattern: str) -> None:
    """List files in the watch directory."""
    watch_dir = directory or settings.watch_directory
    oracle = FileOracle(watch_directory=watch_dir)

    files = oracle.list_files(pattern)

    if files:
        table = Table(title=f"Files in {watch_dir}")
        table.add_column("File", style="cyan")
        table.add_column("Size", style="green")
        table.add_column("Modified", style="yellow")

        for file in files:
            stat = file.stat()
            from datetime import datetime

            modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            table.add_row(file.name, f"{stat.st_size:,} bytes", modified)

        console.print(table)
    else:
        console.print(f"[yellow]No files found matching pattern: {pattern}[/yellow]")


if __name__ == "__main__":
    main()
