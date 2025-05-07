"""
Entrypoint for CLI tool
"""

import json
import click

@click.command()
@click.option("--string", "-s", help="Raw JSON string")
@click.option("--file", "-f", type=click.File('r'), help="File containing JSON object")
@click.argument("input", required=False)

def main(string, file, input):
    ''' Beautify JSON object '''

    if string:
        data = string
    elif file:
        data = file.read()
    elif input:
        try:
            with open(input, 'r') as f:
                data = f.read()
        except FileNotFoundError:
            data = input
    else:
        print("error")
        raise click.UsageError("Error: please provide a JSON string or file")


    try:
        parsed = json.loads(data)
        click.echo(json.dumps(parsed, indent=4))
    except json.JSONDecodeError as e:
        raise click.ClickException(f"Invalid JSON: {e}")


if __name__ == "__main__":
    main()

