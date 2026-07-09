"""JSONGuard CLI — Catch broken JSON before it ships."""

import json as _json
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="jsonguard")
def main():
    """JSONGuard — Validate, format, and lint JSON files."""
    pass


@main.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--schema", "-s", default=None, help="JSON Schema file to validate against (premium)")
def check(path, schema):
    """Validate JSON syntax and structure."""
    console.print()
    console.print(Panel(f"[bold]JSONGuard Check[/bold] — [cyan]{path}[/cyan]", border_style="blue"))

    try:
        with open(path, encoding="utf-8") as f:
            data = _json.load(f)
    except _json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON:[/red] {e}")
        return
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        return

    size = Path(path).stat().st_size
    info = _analyze(data)

    console.print(f"[green]Valid JSON[/green] — {_size_fmt(size)}")
    console.print(f"  Keys: {info['keys']}, Arrays: {info['arrays']}, Depth: {info['max_depth']}")

    if info["duplicate_keys"]:
        console.print(f"  [yellow]Warning:[/yellow] {info['duplicate_keys']} duplicate key(s)")
    if info["empty_arrays"]:
        console.print(f"  [yellow]Info:[/yellow] {info['empty_arrays']} empty array(s)")

    if schema:
        try:
            import jsonschema
        except ImportError:
            console.print("[red]jsonschema not installed.[/red] Run: pip install jsonschema")
            return
        schema_path = Path(schema)
        if not schema_path.exists():
            console.print(f"[red]Schema file not found:[/red] {schema}")
            return
        with open(schema_path, encoding="utf-8") as sf:
            schema_doc = _json.load(sf)
        try:
            jsonschema.validate(instance=data, schema=schema_doc)
            console.print("[green]✓ Schema valid[/green]")
        except jsonschema.ValidationError as ve:
            console.print(f"[red]✗ Schema mismatch:[/red] {ve.message}")
            if ve.path:
                console.print(f"    at {'.'.join(map(str, ve.path))}")


@main.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--output", "-o", default=None, help="Output file (overwrites input if omitted)")
@click.option("--indent", "-i", default=2, help="Indentation spaces")
@click.option("--sort-keys/--preserve-order", default=False, help="Sort keys alphabetically")
def format(path, output, indent, sort_keys):
    """Pretty-print and format JSON."""
    console.print()
    console.print(Panel(f"[bold]JSONGuard Format[/bold] — [cyan]{path}[/cyan]", border_style="blue"))

    with open(path, encoding="utf-8") as f:
        data = _json.load(f)

    formatted = _json.dumps(data, indent=indent, ensure_ascii=False, sort_keys=sort_keys)
    out_path = output or path

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(formatted)
        if not formatted.endswith("\n"):
            f.write("\n")

    console.print(f"[green]Formatted[/green] → {out_path} ({_size_fmt(len(formatted))})")


@main.command()
@click.argument("path", type=click.Path(exists=True))
def view(path):
    """Pretty-print JSON to terminal."""
    with open(path, encoding="utf-8") as f:
        data = _json.load(f)

    console.print()
    console.print(Panel(f"[bold]{path}[/bold]", border_style="blue"))
    console.print(Syntax(_json.dumps(data, indent=2, ensure_ascii=False), "json", theme="monokai"))


def _analyze(data, depth=0):
    """Analyze JSON structure."""
    info = {"keys": 0, "arrays": 0, "max_depth": depth, "duplicate_keys": 0, "empty_arrays": 0}

    if isinstance(data, dict):
        info["keys"] = len(data)
        info["max_depth"] = depth
        seen = set()
        for k in data:
            if k in seen:
                info["duplicate_keys"] += 1
            seen.add(k)
        for v in data.values():
            child = _analyze(v, depth + 1)
            info["keys"] += child["keys"]
            info["arrays"] += child["arrays"]
            info["max_depth"] = max(info["max_depth"], child["max_depth"])
            info["empty_arrays"] += child["empty_arrays"]
    elif isinstance(data, list):
        info["arrays"] = 1
        if not data:
            info["empty_arrays"] = 1
        for item in data:
            child = _analyze(item, depth + 1)
            info["keys"] += child["keys"]
            info["arrays"] += child["arrays"]
            info["max_depth"] = max(info["max_depth"], child["max_depth"])
            info["empty_arrays"] += child["empty_arrays"]

    return info


def _size_fmt(size):
    if size < 1024:
        return f"{size} B"
    return f"{size / 1024:.1f} KB"


if __name__ == "__main__":
    main()
