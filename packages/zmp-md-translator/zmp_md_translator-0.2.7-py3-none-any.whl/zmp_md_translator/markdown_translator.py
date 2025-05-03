"""High-performance markdown translator using OpenAI's GPT models."""

import asyncio
import os
import time
import re
from typing import List, Optional, Dict, Tuple

import aiofiles
import colorlog
from openai import AsyncOpenAI

from .settings import Settings
from .types import ProgressCallback, TranslationProgress, TranslationStatus


class MarkdownTranslator:
    """High-performance markdown translator using OpenAI's GPT models."""

    MODEL_TOKEN_LIMITS = {
        "gpt-3.5-turbo": 4096,
        "gpt-4": 8192,
        "gpt-4o-mini": 128000,
    }

    CHARS_PER_TOKEN = 4

    def __init__(
        self,
        settings: Optional[Settings] = None,
        progress_callback: Optional[ProgressCallback] = None,
    ):
        """Initialize the translator with settings and callbacks."""
        self.settings = settings or Settings()
        self._setup_logger()
        self.client = AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)

        self.api_semaphore = asyncio.Semaphore(self.settings.MAX_CONCURRENT_REQUESTS)
        self.progress_callback = progress_callback
        self.completed_tasks = 0

    def _setup_logger(self):
        """Set up logging system with color formatting and timestamps."""
        logger = colorlog.getLogger("markdown_translator")
        if not logger.handlers:
            handler = colorlog.StreamHandler()
            formatter = colorlog.ColoredFormatter(
                "%(log_color)s[%(asctime)s] %(message)s",
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bg_white",
                },
                datefmt="%Y-%m-%d %H:%M:%S.%f",
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel("INFO")

    async def _report_progress(
        self,
        status: TranslationStatus,
        total: int,
        current_file: Optional[str] = None,
        message: Optional[str] = None,
    ):
        """
        Report translation progress through the callback function.

        Args:
            status (TranslationStatus): Current translation status
            total (int): Total number of files to process
            current_file (Optional[str]): Name of the file being processed
            message (Optional[str]): Additional status message
        """
        if self.progress_callback:
            progress = TranslationProgress(
                status=status,
                current=self.completed_tasks,
                total=total,
                current_file=current_file,
                message=message,
            )
            await self.progress_callback(progress)

    async def translate_repository(
        self,
        source_path: str,
        target_dir: str | None,
        target_languages: list[str],
        selected_solution: str | None = None,
    ) -> None:
        """
        Translate markdown files from a source directory or a single file.

        Args:
            source_path (str): Directory containing markdown files or path to a single markdown file.
            target_dir (Optional[str]): Directory to store translations. Defaults to "i18n".
            target_languages (List[str]): List of language codes to translate to.
            selected_solution (Optional[str]): Selected solution for determining target directory structure.
        """
        logger = colorlog.getLogger("markdown_translator")
        start_time = time.time()
        total_tasks = 0

        try:
            await self._report_progress(TranslationStatus.PREPARING, 0)

            # Validate source path
            if not os.path.exists(source_path):
                raise FileNotFoundError(f"Source path does not exist: {source_path}")

            # Check if source is file or directory
            is_file = os.path.isfile(source_path)

            # Determine target base directory
            target_base = target_dir or "i18n"
            base_dir = os.path.abspath(target_base)

            # Use selected_solution if provided
            if not selected_solution:
                raise ValueError("selected_solution is required for translation")
            source_basename = selected_solution.lower()

            # Store the selected_solution in settings for image path normalization
            # This makes it available to other methods like _translate_single_chunk
            self.settings.selected_solution = selected_solution

            # Build language-specific target prefixes based on source_basename
            lang_target_prefixes = {}
            for lang in target_languages:
                if source_basename == "zcp":
                    prefix = os.path.join(
                        base_dir,
                        lang,
                        "docusaurus-plugin-content-docs-zcp",
                        "current",
                    )
                elif source_basename == "apim":
                    prefix = os.path.join(
                        base_dir,
                        lang,
                        "docusaurus-plugin-content-docs-apim",
                        "current",
                    )
                elif source_basename == "amdp":
                    prefix = os.path.join(
                        base_dir,
                        lang,
                        "docusaurus-plugin-content-docs-amdp",
                        "current",
                    )
                else:
                    prefix = os.path.join(
                        base_dir,
                        lang,
                        "docusaurus-plugin-content-docs",
                        "current",
                    )

                # Create the target directory
                os.makedirs(prefix, exist_ok=True)
                lang_target_prefixes[lang] = prefix

            # Find markdown files
            source_files = []
            source_base = os.path.dirname(source_path) if is_file else source_path
            docs_base = None

            # Find the 'docs' directory in the path
            path_parts = source_base.split(os.sep)
            for i, part in enumerate(path_parts):
                if part == "docs":
                    # Get path after 'docs' but skip the solution name (zcp, apim, amdp)
                    remaining_parts = path_parts[i + 1 :]
                    if (
                        remaining_parts
                        and remaining_parts[0].lower() == source_basename
                    ):
                        docs_base = os.sep.join(
                            remaining_parts[1:]
                        )  # Skip the solution name
                    else:
                        docs_base = os.sep.join(remaining_parts)
                    break

            if is_file:
                # For single file, use only the file name as relative path (do NOT join with docs_base)
                file_name = os.path.basename(source_path)
                rel_path = file_name
                source_files.append(rel_path)
                source_path = os.path.dirname(
                    source_path
                )  # Update source_path to parent dir
            else:
                # For directory, walk through and find all markdown files
                for root, _, files in os.walk(source_path):
                    for file in files:
                        if file.endswith((".md", ".mdx")):
                            file_abs = os.path.join(root, file)
                            # Get path relative to source directory
                            rel_path = os.path.relpath(file_abs, source_path)
                            # If the first directory is the solution name, remove it
                            rel_parts = rel_path.split(os.sep)
                            if rel_parts and rel_parts[0].lower() == source_basename:
                                rel_path = os.sep.join(rel_parts[1:])
                            source_files.append(rel_path)

            total_tasks = len(source_files) * len(target_languages)
            if total_tasks == 0:
                logger.info("No markdown files found to translate")
                return True

            # Log progress
            files_count = len(source_files)
            langs_count = len(target_languages)
            logger.info(
                f"Found {files_count} file{'s' if files_count > 1 else ''} to translate "
                f"into {langs_count} language{'s' if langs_count > 1 else ''}"
            )
            logger.info(
                f"Starting translation of {files_count} file{'s' if files_count > 1 else ''} "
                f"to {langs_count} language{'s' if langs_count > 1 else ''} ({total_tasks} tasks)"
            )

            # Process translations
            await self._report_progress(TranslationStatus.TRANSLATING, total_tasks)
            all_tasks = []
            skipped_files = 0

            for file_path in source_files:
                content = await self._read_file(os.path.join(source_path, file_path))

                # Check if the file has content to translate
                if not content.strip():
                    logger.info(f"Skipping empty file: {file_path}")
                    skipped_files += 1

                    # Create target directories and copy the file directly without translation
                    for lang in target_languages:
                        target_prefix = lang_target_prefixes[lang]

                        # For single file, do not join with docs_base
                        if is_file:
                            target_rel_path = file_path
                        else:
                            if docs_base:
                                target_rel_path = os.path.join(docs_base, file_path)
                            else:
                                target_rel_path = file_path

                        # Join the target prefix with the source file's relative path
                        target_path = os.path.join(target_prefix, target_rel_path)

                        # Ensure target directory exists
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)

                        # Copy the file as-is without translation
                        async with aiofiles.open(
                            target_path, "w", encoding="utf-8"
                        ) as f:
                            await f.write(content)

                        logger.info(f"Copied empty file to: {target_path}")

                        # Count as completed for progress tracking
                        self.completed_tasks += 1

                    # Continue to the next file
                    continue

                # Normalize image paths in the source content - make sure they include solution subdirectory
                content = self._normalize_image_paths(content, source_basename)

                content_size = len(content)
                file_tasks = []

                for lang in target_languages:
                    target_prefix = lang_target_prefixes[lang]

                    # For single file, do not join with docs_base
                    if is_file:
                        target_rel_path = file_path
                    else:
                        if docs_base:
                            target_rel_path = os.path.join(docs_base, file_path)
                        else:
                            target_rel_path = file_path

                    # Join the target prefix with the source file's relative path
                    target_path = os.path.join(target_prefix, target_rel_path)

                    # Ensure target directory exists
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)

                    file_tasks.append(
                        self._translate_and_write(
                            content=content,
                            content_size=content_size,
                            target_path=target_path,
                            lang=lang,
                            total_tasks=total_tasks,
                            start_time=time.time(),
                        )
                    )
                all_tasks.append(asyncio.gather(*file_tasks))

            # Process in batches
            batch_size = self.settings.MAX_CONCURRENT_REQUESTS
            for i in range(0, len(all_tasks), batch_size):
                batch = all_tasks[i : i + batch_size]
                await asyncio.gather(*batch)

            # Log completion
            elapsed = time.time() - start_time
            if total_tasks > 0:
                per_file = elapsed / (
                    total_tasks - (skipped_files * len(target_languages))
                )
                logger.info(
                    f"Translation completed in {elapsed:.2f}s ({per_file:.2f}s/file), "
                    f"skipped {skipped_files} empty files"
                )

            await self._report_progress(TranslationStatus.COMPLETED, total_tasks)
            logger.info("All translations completed successfully")
            return True

        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            await self._report_progress(
                TranslationStatus.FAILED, total_tasks, message=str(e)
            )
            raise

    async def _translate_and_write(
        self,
        content: str,
        content_size: int,
        target_path: str,
        lang: str,
        total_tasks: int,
        start_time: float,
    ):
        """
        Translate content and write to target file while tracking performance.

        Handles chunking of large files, parallel translation of chunks,
        and maintains file system structure.

        Args:
            content (str): Content to translate
            content_size (int): Size of content in characters
            target_path (str): Path where translated file will be written
            lang (str): Target language code
            total_tasks (int): Total number of translation tasks
            start_time (float): Start time for performance tracking

        Raises:
            Exception: If translation or file writing fails
        """
        logger = colorlog.getLogger("markdown_translator")

        try:
            # Pre-create directory
            os.makedirs(os.path.dirname(target_path), exist_ok=True)

            async with self.api_semaphore:
                logger.info(
                    f"content_size: {content_size}, MAX_CHUNK_SIZE: {self.settings.MAX_CHUNK_SIZE}"
                )
                if content_size > self.settings.MAX_CHUNK_SIZE:
                    chunks = self._split_into_chunks(
                        content, self.settings.MAX_CHUNK_SIZE
                    )
                    # Process chunks in parallel
                    translations = await asyncio.gather(
                        *[self._translate_single_chunk(chunk, lang) for chunk in chunks]
                    )
                    translated_content = "\n".join(translations)
                else:
                    translated_content = await self._translate_single_chunk(
                        content, lang
                    )

            # Write translation
            async with aiofiles.open(target_path, "w", encoding="utf-8") as f:
                await f.write(translated_content)

            elapsed = time.time() - start_time
            rel_path = os.path.relpath(target_path)
            logger.info(f"✓ {rel_path} [{lang}] ({elapsed:.2f}s)")

            self.completed_tasks += 1
            await self._report_progress(
                TranslationStatus.TRANSLATING,
                total_tasks,
                current_file=f"{rel_path} [{lang}]",
            )

        except Exception as e:
            logger.error(f"Failed to translate to {lang}: {str(e)}")
            raise

    async def _read_file(self, path: str) -> str:
        """
        Read file content asynchronously.

        Args:
            path (str): Path to the file to read

        Returns:
            str: Content of the file

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file cannot be read
        """
        async with aiofiles.open(path, "r", encoding="utf-8") as f:
            return await f.read()

    def _calculate_chunk_size(self, content_size: int) -> int:
        """
        Calculate optimal chunk size based on content size and model limits.

        Adjusts chunk size dynamically based on content size to optimize
        translation performance and token usage.

        Args:
            content_size (int): Size of content in characters

        Returns:
            int: Optimal chunk size in characters
        """
        model_token_limit = self.MODEL_TOKEN_LIMITS.get(
            self.settings.OPENAI_MODEL, 4096
        )
        base_size = (model_token_limit // 2) * self.CHARS_PER_TOKEN

        # Adjust chunk size based on content size
        if content_size < 1000:
            return base_size
        elif content_size < 3000:
            return base_size * 2
        else:
            return base_size * 3  # Larger chunks for big files

    def _split_into_chunks(self, content: str, max_chunk_size: int = 2000) -> List[str]:
        """
        Split content into chunks while preserving markdown structure and handling front matter correctly.

        This method ensures that:
        1. Front matter only appears in the first chunk
        2. Special elements like code blocks and other markdown structures are kept intact
        3. Subsequent chunks are properly marked to avoid front matter confusion
        """
        logger = colorlog.getLogger("markdown_translator")
        logger.debug(f"Splitting content into chunks of size {max_chunk_size}")
        logger.debug(f"Content: {content}")
        logger.debug(f"Max chunk size: {max_chunk_size}")
        logger.debug(f"Content length: {len(content)}")

        lines = content.splitlines()
        chunks = []
        current_chunk = []
        current_size = 0
        i = 0

        # First, detect and handle front matter
        has_front_matter = False
        front_matter_end = -1
        if len(lines) >= 2 and lines[0].strip() == "---":
            has_front_matter = True
            # Find the closing front matter marker
            for j in range(1, len(lines)):
                if lines[j].strip() == "---":
                    front_matter_end = j
                    break

        # Process the document
        while i < len(lines):
            line = lines[i]
            line_size = len(line)

            # Check if this line contains special markdown elements we don't want to split
            is_special_line = (
                line.strip().startswith("#")  # Headers
                or line.strip().startswith("```")  # Code blocks
                or line.strip().startswith("|")  # Table rows
                or line.strip().startswith("- ")  # List items
                or line.strip().startswith("* ")  # List items
                or line.strip().startswith("> ")  # Blockquotes
            )

            # Special handling for front matter
            if has_front_matter and i <= front_matter_end:
                # Always include front matter lines in the first chunk
                current_chunk.append(line)
                current_size += line_size + 1
                i += 1
                continue

            # Check if adding this line would exceed max size
            if current_size + line_size > max_chunk_size and current_chunk:
                # Finish current chunk
                chunks.append("\n".join(current_chunk))
                current_chunk = []
                current_size = 0

                # If this is not the first chunk and we're about to start a new one,
                # add a marker to indicate it's a continuation
                if chunks:
                    current_chunk.append("<!-- CHUNK_CONTINUATION -->")
                    current_size += 25  # Length of the marker

            # Special handling for very long lines
            if line_size > max_chunk_size:
                # If the line is too long, just add it as its own chunk
                if current_chunk:
                    chunks.append("\n".join(current_chunk))
                    current_chunk = []
                    current_size = 0
                    if chunks:
                        current_chunk.append("<!-- CHUNK_CONTINUATION -->")
                        current_size += 25
                chunks.append(line)
            else:
                # For normal-sized lines, just add to current chunk
                current_chunk.append(line)
                current_size += line_size + 1  # +1 for newline

            # Handle special cases - code blocks, tables
            if is_special_line:
                # If we've started a special block, ensure we don't split it
                # Look ahead to see if there's a corresponding closing element
                if line.strip().startswith("```"):
                    # Look for the matching closing delimiter
                    closing_delimiter = line.strip()
                    j = i + 1
                    found_closing = False

                    while j < len(lines) and not found_closing:
                        if lines[j].strip() == closing_delimiter:
                            found_closing = True
                            # Add all lines until the closing delimiter
                            for k in range(i + 1, j + 1):
                                current_chunk.append(lines[k])
                                current_size += len(lines[k]) + 1
                            i = j  # Skip ahead
                        j += 1

            i += 1

        # Add the last chunk if there is one
        if current_chunk:
            chunks.append("\n".join(current_chunk))

        return chunks

    async def _translate_single_chunk(self, chunk: str, target_language: str) -> str:
        """Translate a single chunk of text using the OpenAI API."""
        # Pre-process to protect image links from translation
        chunk, image_map = self._extract_image_links(chunk)

        # IMPORTANT: Extract and protect ALL HTML content with a much simpler, direct approach
        chunk, html_segments_map = self._protect_html_content(chunk)

        # Check if this is a continuation chunk
        is_continuation = "<!-- CHUNK_CONTINUATION -->" in chunk
        if is_continuation:
            # Remove the continuation marker before translation
            chunk = chunk.replace("<!-- CHUNK_CONTINUATION -->", "").strip()

        # Build the system message content with clear rules for headers and tables
        system_content = (
            f"You are a technical documentation translator specializing in MDX format. "
            f"Translate the following text from English to {target_language}.\n\n"
            "        CRITICAL RULES:\n\n"
            "        1. Front Matter Rules:\n"
            "           - Front matter is the section between --- markers at the top of the file\n"
            "           - CRITICAL: The front matter title MUST remain in its original English form\n"
            "           - Example for title preservation:\n"
            "             Input:  \"title: '3. Building a Demo Application'\"\n"
            "             Output: \"title: '3. Building a Demo Application'\"  (keep in English)\n"
            "           - NEVER translate ANY front matter values, including:\n"
            "             * title: must stay in original English (e.g., \"title: '3. Building a Demo Application'\")\n"
            '             * id: must stay in English (e.g., "id: building-demo-application")\n'
            "             * ALL other front matter fields and values\n"
            "           - Examples of complete front matter preservation:\n"
            '             Input:  "---\n'
            "                    id: 3-building-a-demo-application\n"
            "                    title: '3. Building a Demo Application'\n"
            "                    sidebar_position: 3\n"
            '                    ---"\n'
            '             Output: "---\n'
            "                    id: 3-building-a-demo-application\n"
            "                    title: '3. Building a Demo Application'\n"
            "                    sidebar_position: 3\n"
            '                    ---"\n\n'
            "        2. Header Translation Rules:\n"
            "           - You MUST translate ALL headers (lines starting with #)\n"
            "           - For headers with section IDs:\n"
            "             * Translate the text part BEFORE the section ID\n"
            "             * Keep the section ID (part with {#...}) in English\n"
            "             * Keep the exact number of # characters\n"
            "           - Examples:\n"
            '             Input:  "## Creating Build Pipelines {#creating-build-pipelines}"\n'
            "             Output: \"## [translated text for 'Creating Build Pipelines'] {#creating-build-pipelines}\"\n"
            "             \n"
            '             Input:  "### Demo Application {#demo-application}"\n'
            "             Output: \"### [translated text for 'Demo Application'] {#demo-application}\"\n"
            "             \n"
            '             Input:  "## Running Each Pipeline {#running-each-pipeline}"\n'
            "             Output: \"## [translated text for 'Running Each Pipeline'] {#running-each-pipeline}\"\n"
            "           - For headers without section IDs:\n"
            "             * Translate the entire header text\n"
            "             * Keep the exact number of # characters\n"
            "           - Examples:\n"
            '             Input:  "## Overview"\n'
            "             Output: \"## [translated text for 'Overview']\"\n\n"
            "        3. Paragraph Translation Rules:\n"
            "           - Translate ALL paragraphs and text content\n"
            "           - Translate ALL bullet points and list items\n"
            "           - Translate ALL blockquotes (lines starting with >)\n"
            "           - Translate ALL inline text between HTML tags\n"
            "           - Translate ALL text in tables except for technical terms\n"
            "           - Translate ALL text in code block comments\n"
            '           - NEVER leave any English text untranslated unless it\'s explicitly listed in "Keep in English"\n'
            "           - Examples:\n"
            '             Input:  "This is a paragraph about Cloud Z CP features."\n'
            '             Output: "[translated text] about Cloud Z CP features."\n'
            "             \n"
            '             Input:  "- First bullet point about API usage"\n'
            '             Output: "- [translated text] about API usage"\n'
            "             \n"
            '             Input:  "> Important note about SDK implementation"\n'
            '             Output: "> [translated text] about SDK implementation"\n'
            "             \n"
            '             Input:  "<b>Warning:</b> Check your configuration"\n'
            '             Output: "<b>[translated text]:</b> [translated text]"\n\n'
            "        4. Table Rules:\n"
            "           - Keep table structure and alignment exactly as is\n"
            "           - Keep table header row formatting (| --- |)\n"
            "           - Keep <b> tags in table cells exactly as is\n"
            "           - Translate cell content but preserve:\n"
            "             * Technical terms (e.g., Administrator, Developer, Pipeline)\n"
            "             * Yes/No values\n"
            "             * O/X values\n"
            "             * Technical status values (e.g., Connected, Pending)\n"
            "           - Examples:\n"
            '             Input:  "| Feature | Description | Status |"\n'
            '             Output: "| [translated text] | [translated text] | [translated text] |"\n\n'
            "        5. Keep in English:\n"
            "           - ALL front matter content (title, id, etc. must stay in original English)\n"
            "           - All section IDs (text after {#})\n"
            "           - All technical product names (e.g., Cloud Z CP, AWS EKS)\n"
            "           - All technical component names (e.g., API, SDK)\n"
            "           - All code snippets and commands\n"
            "           - All file paths and URLs\n"
            "           - All placeholders (e.g., __HTML_123__)\n"
            "           - All environment variables (e.g., $HOME, $PATH)\n"
            "           - All command-line arguments (e.g., --help, -v)\n"
            "           - All configuration keys and values\n"
            "           - All error codes and status codes\n\n"
            "        6. HTML/Markdown Preservation:\n"
            "           - Keep all HTML tags exactly as is (<b>, </b>, etc.)\n"
            "           - Keep all markdown syntax (*, -, >, etc.)\n"
            "           - Keep all code block markers (```) and language identifiers\n"
            "           - Keep all image paths exactly as is\n"
            "           - Keep all link references and URLs\n"
            "           - Keep all formatting characters\n\n"
            "        Original text:\n"
            f"        {chunk}\n\n"
            "        Translated text:"
        )

        response = await self.client.chat.completions.create(
            model=self.settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_content,
                },
                {"role": "user", "content": chunk},
            ],
            temperature=0.0,
            max_tokens=self.settings.MAX_RESPONSE_TOKENS,
        )

        translated_text = response.choices[0].message.content.strip()

        # Remove any continuation markers from the translated text
        translated_text = translated_text.replace(
            "<!-- CHUNK_CONTINUATION -->", ""
        ).strip()

        # Restore all HTML content directly, with absolutely no modifications
        translated_text = self._restore_html_content(translated_text, html_segments_map)

        # Restore original image paths
        translated_text = self._restore_image_links(translated_text, image_map)

        # Get the selected solution from settings if available
        selected_solution = getattr(self.settings, "selected_solution", None)
        if selected_solution:
            # Re-normalize paths after translation to ensure they're correct
            translated_text = self._normalize_image_paths(
                translated_text, selected_solution
            )

        return translated_text

    def _extract_image_links(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Extract image links from markdown content and replace with placeholders.

        This ensures image paths remain exactly the same during translation.
        Also validates image paths to ensure they include the solution subdirectory.

        Args:
            text (str): The markdown content

        Returns:
            Tuple[str, Dict[str, str]]: Modified text with placeholders and mapping of placeholders to original image paths
        """
        # Regular expression to find markdown image references: ![alt text](/path/to/image.png)
        image_pattern = re.compile(r"(!\[.*?\]\()(.*?)(\))", re.DOTALL)
        image_map = {}
        placeholder_counter = 0

        def replace_match(match):
            nonlocal placeholder_counter
            prefix = match.group(1)  # ![alt text](
            image_path = match.group(2)  # /path/to/image.png
            suffix = match.group(3)  # )

            # Create a unique placeholder
            placeholder = f"__IMGPATH_{placeholder_counter}__"
            placeholder_counter += 1

            # Save the original path to restore later
            image_map[placeholder] = image_path

            # Return with placeholder instead of real path
            return f"{prefix}{placeholder}{suffix}"

        # Replace all image paths with placeholders
        modified_text = image_pattern.sub(replace_match, text)

        return modified_text, image_map

    def _restore_image_links(self, text: str, image_map: Dict[str, str]) -> str:
        """
        Restore original image paths from placeholders.

        Args:
            text (str): Translated text with image placeholders
            image_map (Dict[str, str]): Mapping of placeholders to original image paths

        Returns:
            str: Text with original image paths restored
        """
        result = text

        # Replace each placeholder with its original path
        for placeholder, original_path in image_map.items():
            result = result.replace(placeholder, original_path)

        return result

    def _normalize_image_paths(self, text: str, selected_solution: str) -> str:
        """
        Normalize image paths in markdown content to ensure they include
        the solution subdirectory.

        Args:
            text (str): The markdown content
            selected_solution (str): The solution name (e.g., 'zcp', 'apim', 'amdp')

        Returns:
            str: Text with normalized image paths
        """
        if not selected_solution:
            return text  # Can't normalize without knowing the solution

        solution_lower = selected_solution.lower()
        logger = colorlog.getLogger("markdown_translator")

        # 1. Find any image paths that directly reference a UUID pattern file but are missing the solution and/or user-guide path
        # Pattern to match markdown image with a UUID-like filename without proper path
        # Looking for patterns like ![alt](/img/1abb7135-d33b-80a7-9eff-f5ae2eaced37.png)
        uuid_pattern = re.compile(
            r"(!\[.*?\]\()(/img/)([^/]*?)([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}|\d[a-f0-9]{7}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})([^/]*?\.\w+)(\))",
            re.DOTALL | re.IGNORECASE,
        )

        # Function to fix paths with UUIDs by preserving the original path structure
        def fix_uuid_path(match):
            prefix = match.group(1)  # ![alt text](
            img_prefix = match.group(2)  # /img/
            path_prefix = match.group(3)  # Any prefix before UUID
            uuid_part = match.group(4)  # UUID part
            file_suffix = match.group(5)  # .png or other extension
            suffix = match.group(6)  # )

            # If there's already a solution in the path, don't duplicate it
            if path_prefix and solution_lower in path_prefix.lower():
                # Preserve the original path structure
                return (
                    f"{prefix}{img_prefix}{path_prefix}{uuid_part}{file_suffix}{suffix}"
                )

            # No solution in path, add the solution but preserve the rest of the path
            return f"{prefix}{img_prefix}{solution_lower}/{path_prefix}{uuid_part}{file_suffix}{suffix}"

        # 2. Handle the standard solution subdirectory missing case
        image_pattern = re.compile(
            r"(!\[.*?\]\()(/img/)((?!zcp|apim|amdp)[^/].*?)(\))",
            re.DOTALL | re.IGNORECASE,
        )

        # Function to fix paths that don't have the solution subdirectory
        def fix_path(match):
            prefix = match.group(1)  # ![alt text](
            img_prefix = match.group(2)  # /img/
            path = match.group(3)  # rest of the path
            suffix = match.group(4)  # )

            # Add the solution subdirectory if it's missing
            return f"{prefix}{img_prefix}{solution_lower}/{path}{suffix}"

        # 3. Also handle paths that start with static/img/ instead of /img/
        static_pattern = re.compile(
            r"(!\[.*?\]\()(static/img/)((?!zcp|apim|amdp)[^/].*?)(\))",
            re.DOTALL | re.IGNORECASE,
        )

        def fix_static_path(match):
            prefix = match.group(1)  # ![alt text](
            img_prefix = match.group(2)  # static/img/
            path = match.group(3)  # rest of the path
            suffix = match.group(4)  # )

            # Add the solution subdirectory if it's missing
            return f"{prefix}{img_prefix}{solution_lower}/{path}{suffix}"

        # First handle UUID-specific pattern for better precision
        normalized_text = uuid_pattern.sub(fix_uuid_path, text)

        # Then apply the standard fixes
        normalized_text = image_pattern.sub(fix_path, normalized_text)
        normalized_text = static_pattern.sub(fix_static_path, normalized_text)
        logger.info(f"Normalized text: {normalized_text}")
        return normalized_text

    def _protect_html_content(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Protect ALL HTML content from translation by replacing it with simple numbered placeholders.

        This method takes a completely different approach from previous versions:
        - It finds ALL HTML content (not just tags)
        - It makes ZERO attempts to balance, fix, or understand the HTML structure
        - It simply replaces all HTML content with placeholders and stores the original for restoration

        Args:
            text (str): The markdown content with HTML content

        Returns:
            Tuple[str, Dict[str, str]]: Modified text with placeholders and mapping of placeholders to original HTML content
        """
        # First, let's identify code blocks and protect them from HTML processing
        code_blocks = {}
        code_block_counter = 0

        # Pattern to match markdown code blocks with language identifier
        code_block_pattern = re.compile(r"(```[a-zA-Z0-9_+-]*\n[\s\S]*?```)", re.DOTALL)

        # Replace code blocks with placeholders to protect them
        def replace_code_block(match):
            nonlocal code_block_counter
            placeholder = f"__CODE_BLOCK_{code_block_counter}__"
            code_blocks[placeholder] = match.group(1)
            code_block_counter += 1
            return placeholder

        # Replace code blocks with placeholders
        protected_text = code_block_pattern.sub(replace_code_block, text)

        # Now process HTML content in the non-code parts
        html_map = {}
        counter = 0

        # First, find all HTML tags in the text
        html_tags = []

        # Find all opening tags
        opening_tag_pattern = re.compile(r"<[^/][^>]*>")
        for match in opening_tag_pattern.finditer(protected_text):
            tag = match.group(0)
            tag_match = re.match(r"<([a-zA-Z0-9]+)", tag)
            if tag_match:  # Add null check
                tag_name = tag_match.group(1)
                html_tags.append((match.start(), match.end(), tag, tag_name, "opening"))

        # Find all closing tags
        closing_tag_pattern = re.compile(r"</[^>]+>")
        for match in closing_tag_pattern.finditer(protected_text):
            tag = match.group(0)
            tag_match = re.match(r"</([a-zA-Z0-9]+)>", tag)
            if tag_match:  # Add null check
                tag_name = tag_match.group(1)
                html_tags.append((match.start(), match.end(), tag, tag_name, "closing"))

        # Find all self-closing tags
        self_closing_pattern = re.compile(r"<[^>]+/>")
        for match in self_closing_pattern.finditer(protected_text):
            tag = match.group(0)
            html_tags.append((match.start(), match.end(), tag, None, "self-closing"))

        # Sort tags by position
        html_tags.sort(key=lambda x: x[0])

        # Now find complete HTML elements (opening tag + content + closing tag)
        processed_text = protected_text
        offset = 0

        # Process each tag
        for i, (start, end, tag, tag_name, tag_type) in enumerate(html_tags):
            if tag_type == "opening" and tag_name:  # Ensure tag_name exists
                # Find the matching closing tag
                matching_closing = None
                for j in range(i + 1, len(html_tags)):
                    if html_tags[j][3] == tag_name and html_tags[j][4] == "closing":
                        matching_closing = html_tags[j]
                        break

                if matching_closing:
                    # We found a complete HTML element
                    element_start = start
                    element_end = matching_closing[1]
                    html_content = protected_text[element_start:element_end]

                    # Create a placeholder
                    placeholder = f"__HTML_{counter}__"
                    html_map[placeholder] = html_content
                    counter += 1

                    # Replace the HTML content with the placeholder
                    processed_text = (
                        processed_text[: element_start + offset]
                        + placeholder
                        + processed_text[element_end + offset :]
                    )

                    # Update offset
                    offset += len(placeholder) - len(html_content)

            elif tag_type == "self-closing":
                # Handle self-closing tags
                placeholder = f"__HTML_{counter}__"
                html_map[placeholder] = tag
                counter += 1

                # Replace the self-closing tag with the placeholder
                processed_text = (
                    processed_text[: start + offset]
                    + placeholder
                    + processed_text[end + offset :]
                )

                # Update offset
                offset += len(placeholder) - len(tag)

        # Now restore the code blocks
        final_text = processed_text
        for placeholder, code_block in code_blocks.items():
            final_text = final_text.replace(placeholder, code_block)

        return final_text, html_map

    def _restore_html_content(self, text: str, html_map: Dict[str, str]) -> str:
        """
        Restore all HTML content from placeholders with absolutely no modifications.

        Args:
            text (str): Translated text with HTML placeholders
            html_map (Dict[str, str]): Mapping of placeholders to original HTML content

        Returns:
            str: Text with original HTML content restored exactly as it was
        """
        result = text

        # Replace each placeholder with its original HTML content, exactly as it was
        for placeholder, original_html in html_map.items():
            result = result.replace(placeholder, original_html)

        # Ensure code blocks have proper language identifiers
        # This is a safety check to make sure code blocks are properly formatted
        code_block_pattern = re.compile(r"```\s*\n", re.DOTALL)
        result = code_block_pattern.sub("```\n", result)

        return result
