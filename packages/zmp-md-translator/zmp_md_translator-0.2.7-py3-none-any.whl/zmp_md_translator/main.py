#!/usr/bin/env python3
"""CLI application for translating markdown repositories."""

import argparse
import asyncio
import sys
import click
import colorlog

from dotenv import load_dotenv

from zmp_md_translator import MarkdownTranslator, Settings
from zmp_md_translator.types import TranslationProgress


async def progress_callback(progress: TranslationProgress):
    """Handle progress updates."""
    if progress.current_file:
        sys.stderr.write(
            f"\rProcessing {progress.current_file} "
            f"({progress.current}/{progress.total})"
        )
        sys.stderr.flush()


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Translate markdown files in a repository or a single markdown file to multiple languages."
    )
    parser.add_argument(
        "--source-dir",
        "-s",
        required=True,
        help="Source directory containing markdown files or path to a single markdown file",
    )
    parser.add_argument(
        "--target-dir",
        "-t",
        default="i18n",
        help="Target directory for translations (default: i18n)",
    )
    parser.add_argument(
        "--languages",
        "-l",
        required=True,
        help="Comma-separated list of target language codes (e.g., ko,ja,fr)",
    )
    parser.add_argument(
        "--model",
        "-m",
        help="OpenAI model to use (overrides .env setting)",
    )
    parser.add_argument(
        "--chunk-size",
        "-c",
        type=int,
        help="Maximum chunk size for translation (overrides .env setting)",
    )
    parser.add_argument(
        "--concurrent",
        "-n",
        type=int,
        help="Maximum concurrent requests (overrides .env setting)",
    )
    parser.add_argument(
        "--solution",
        type=click.Choice(["zcp", "apim", "amdp"], case_sensitive=False),
        help="Selected solution for determining target directory structure",
    )
    return parser.parse_args()


async def main():
    """Run the translator CLI."""
    # Load environment variables
    load_dotenv()

    # Parse command line arguments
    args = parse_args()

    # Create settings with CLI overrides
    settings = Settings()
    if args.model:
        settings.OPENAI_MODEL = args.model
    if args.chunk_size:
        settings.MAX_CHUNK_SIZE = args.chunk_size
    if args.concurrent:
        settings.MAX_CONCURRENT_REQUESTS = args.concurrent

    # Initialize translator
    translator = MarkdownTranslator(
        settings=settings,
        progress_callback=progress_callback,
    )

    # Parse languages
    target_languages = [lang.strip() for lang in args.languages.split(",")]

    try:
        # Run translation
        await translator.translate_repository(
            target_languages=target_languages,
            source_dir=args.source_dir,
            target_dir=args.target_dir,
            selected_solution=args.solution,
        )
        return 0
    except Exception as e:
        logger = colorlog.getLogger("markdown_translator")
        logger.error(f"Error: {str(e)}")
        return 1


@click.command()
@click.option(
    "-s",
    "--source-dir",
    required=True,
    help="Source directory containing markdown files or path to a single markdown file",
)
@click.option(
    "-t",
    "--target-dir",
    default="i18n",
    help="Target directory for translations",
)
@click.option(
    "-l",
    "--languages",
    required=True,
    help="Comma-separated list of target language codes",
)
@click.option(
    "-m",
    "--model",
    help="OpenAI model to use (overrides .env setting)",
)
@click.option(
    "-c",
    "--chunk-size",
    type=int,
    help="Maximum chunk size for translation (overrides .env setting)",
)
@click.option(
    "-n",
    "--concurrent",
    type=int,
    help="Maximum concurrent requests (overrides .env setting)",
)
@click.option(
    "--solution",
    type=click.Choice(["zcp", "apim", "amdp"], case_sensitive=False),
    required=True,
    help="Selected solution for determining target directory structure",
)
def run_cli(
    source_dir: str,
    target_dir: str,
    languages: str,
    model: str | None = None,
    chunk_size: int | None = None,
    concurrent: int | None = None,
    solution: str | None = None,
) -> None:
    """
    CLI interface for the markdown translator.
    """
    try:
        asyncio.run(
            _run_async(
                source_dir=source_dir,
                target_dir=target_dir,
                languages=languages,
                model=model,
                chunk_size=chunk_size,
                concurrent=concurrent,
                solution=solution,
            )
        )
    except KeyboardInterrupt:
        logger = colorlog.getLogger("markdown_translator")
        logger.error("Translation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger = colorlog.getLogger("markdown_translator")
        logger.error(f"Error: {str(e)}")
        sys.exit(1)


async def _run_async(
    source_dir: str,
    target_dir: str,
    languages: str,
    model: str | None = None,
    chunk_size: int | None = None,
    concurrent: int | None = None,
    solution: str | None = None,
) -> None:
    """
    Async implementation of the CLI interface.
    """
    # Initialize settings
    settings = Settings()
    if model:
        settings.openai_model = model
    if chunk_size:
        settings.max_chunk_size = chunk_size
    if concurrent:
        settings.max_concurrent_requests = concurrent

    # Initialize translator
    translator = MarkdownTranslator(settings)

    # Split languages string into list
    target_languages = [lang.strip() for lang in languages.split(",")]

    # Run translation
    await translator.translate_repository(
        source_path=source_dir,
        target_dir=target_dir,
        target_languages=target_languages,
        selected_solution=solution,
    )


if __name__ == "__main__":
    run_cli()
