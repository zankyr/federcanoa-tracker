from pathlib import Path

import click
from loguru import logger

from .monitor import WebsiteMonitor


@click.command()
@click.option('--config', '-c',
              type=click.Path(exists=True),
              help='Path to config file',
              default=None)
def main(config):
    """Monitor website for new documents and send notifications."""
    try:
        # If no config specified, look for config.json in the same directory as the script
        if config is None:
            config = Path(__file__).parent / 'config.json'

        logger.info(f"Starting monitor with config: {config}")
        monitor = WebsiteMonitor(config)
        monitor.check_website()
        logger.info("Monitor run completed")
    except Exception as e:
        logger.error(f" {str(e)}")
        raise click.ClickException(str(e))

if __name__ == '__main__':
    main()