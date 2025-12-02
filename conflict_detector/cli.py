import click

from .core import load_jsonl, process_tickets, write_output


@click.command()
@click.option("--input", "input_path", required=True, type=click.Path(exists=True, dir_okay=False), help="Input JSONL file")
@click.option("--output", "output_path", required=True, type=click.Path(dir_okay=False), help="Output file path")
@click.option("--conflicts-only", is_flag=True, default=False, help="Only output samples with conflicts")
@click.option("--format", "fmt", type=click.Choice(["json", "jsonl"]), default="jsonl", help="Output format")
def main(input_path: str, output_path: str, conflicts_only: bool, fmt: str):
    """Detect label conflicts, provide reasoning, and suggest resolved labels."""
    tickets = load_jsonl(input_path)
    outputs = process_tickets(tickets, conflicts_only=conflicts_only)
    write_output(output_path, outputs, fmt=fmt)
    total = len(tickets)
    conflicts = sum(1 for o in outputs if o.is_conflict)
    click.echo(f"Processed {total} tickets. Conflicts: {conflicts}. Output: {output_path}")


if __name__ == "__main__":
    main()
