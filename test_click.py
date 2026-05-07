import click

@click.command()
@click.option("--type", "periph_type",
              type = click.Choice(["uart", "gpio", "spi", "i2c"]),
              required = True,
              prompt = "What is your peripheral type?",
              help = "Peripheral type to generate a header for")

def periph(periph_type):
    click.echo(f"Generating header for {periph_type}...")


if __name__ == '__main__':
    periph()