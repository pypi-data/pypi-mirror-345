# ZMP Markdown Translator

![Platform Badge](https://img.shields.io/badge/platform-zmp-red)
![Component Badge](https://img.shields.io/badge/component-translator-red)
![CI Badge](https://img.shields.io/badge/ci-github_action-green)
![License Badge](https://img.shields.io/badge/license-MIT-green)
![PyPI - Version](https://img.shields.io/pypi/v/zmp-md-translator)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/zmp-md-translator)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/zmp-md-translator)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/zmp-md-translator)

A high-performance markdown translator that supports multiple languages and preserves markdown formatting. Uses OpenAI's GPT models for translation.

## Features

- Translates entire directories of markdown files
- Preserves markdown formatting and structure
- Supports multiple target languages simultaneously
- Handles large files through automatic chunking
- Maintains Docusaurus-compatible directory structures
- Shows real-time progress with colorized output
- Enforces consistent translation rules for technical documentation

## Translation Rules

The translator follows strict rules to ensure consistent and accurate translations:

### Preserved in English
- Front matter between `---` markers (including id, title, sidebar_position)
- All section headers (including those with HTML tags)
- All HTML-wrapped headers and subheadings
- Product names (e.g., Cloud Z CP)
- Platform names (e.g., Kubernetes)
- Service names (e.g., Container Management Service)
- Tool names (e.g., Chrome, Gitea)
- Version numbers and technical specifications
- Table headers in markdown tables
- Section IDs in curly braces

### Translated to Target Language
- All paragraphs and content text
- Descriptions and explanations
- UI messages and instructions
- List items and bullet points
- Table content (except headers)
- Sentences containing product names (while keeping the names in English)

### Consistency Requirements
- No mixed language content within sentences
- Complete translation of all paragraphs
- Preservation of markdown structure and formatting
- Exact maintenance of whitespace and line numbers

## Installation

```bash
# Using Poetry (recommended)
poetry install

# Or using pip
pip install zmp-md-translator
```

## Usage

### Basic Command Structure

```bash
zmp-translate \
  --source-dir SOURCE_PATH \
  --target-dir TARGET_DIR \
  --languages LANG_CODES \
  --solution SOLUTION_TYPE
```

Required parameters:
- `SOURCE_PATH`: Path to a markdown file or directory containing markdown files
- `LANG_CODES`: Comma-separated list of target language codes
- `SOLUTION_TYPE`: Type of documentation (zcp, apim, or amdp)

Optional parameters:
- `TARGET_DIR`: Target directory for translations (default: "i18n")
- `--model`: OpenAI model to use (overrides .env setting)
- `--chunk-size`: Maximum chunk size for translation
- `--concurrent`: Maximum concurrent requests

### Example Usage

```bash
# Translate a directory
zmp-translate \
  --source-dir "./repo/docs/zcp/v2.0" \
  --target-dir "./repo/i18n" \
  --languages "ko,ja,zh" \
  --solution zcp

# Translate a single file
zmp-translate \
  --source-dir "./repo/docs/zcp/v2.0/FAQ.mdx" \
  --target-dir "./repo/i18n" \
  --languages "ko" \
  --solution zcp
```

Using short options:
```bash
# Directory translation
zmp-translate -s "./repo/docs/zcp/v2.0" -t "./repo/i18n" -l "ko,ja,zh" --solution zcp

# Single file translation
zmp-translate -s "./repo/docs/zcp/v2.0/FAQ.mdx" -t "./repo/i18n" -l "ko" --solution zcp
```

### Output Directory Structure

The translator creates a Docusaurus-compatible directory structure:

```
i18n/
├── ko/
│   └── docusaurus-plugin-content-docs-zcp/
│       └── current/
│           └── v2.0/
│               ├── FAQ.mdx
│               └── ...
├── ja/
│   └── docusaurus-plugin-content-docs-zcp/
│       └── current/
│           └── v2.0/
│               ├── FAQ.mdx
│               └── ...
└── zh/
    └── docusaurus-plugin-content-docs-zcp/
        └── current/
            └── v2.0/
                ├── FAQ.mdx
                └── ...
```

### Supported Language Codes

The following language codes are supported:

| Code | Language    |
|------|------------|
| ko   | Korean     |
| fr   | French     |
| ja   | Japanese   |
| es   | Spanish    |
| de   | German     |
| zh   | Chinese    |
| ru   | Russian    |
| it   | Italian    |
| pt   | Portuguese |
| ar   | Arabic     |

### Environment Configuration

Create a `.env` file in your project root:

```env
# OpenAI Configuration
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=your-model-here

# Performance Settings
MAX_CHUNK_SIZE=4000
MAX_CONCURRENT_REQUESTS=5
```

## Development

```bash
# Install dependencies
poetry install

# Run tests
poetry run test

# Run with watch mode (development)
poetry run watch
```

## License

This project is distributed under the MIT License. See the [LICENSE](LICENSE) file for more information.
