# Transcriber

A flexible Python package for transcribing audio and video from various sources (SoundCloud, YouTube, or local files) into multiple text formats (txt, docx, srt). The transcriber supports multiple speech recognition models (defaulting to Whisper "large-v3"). It leverages GPU acceleration for faster processing and utilizes concurrency through async and multiprocessing to improve performance.

## Features

- **Multiple Input Sources**: Transcribe from SoundCloud, YouTube, or local audio/video files
- **Multiple Models**: Support for both `faster-whisper` and standard `whisper` models
- **GPU Acceleration**: Utilize GPU processing for faster transcription
- **Concurrent Processing**: Batch processing and VAD filtering for improved performance
- **Various Output Formats**: Export transcriptions to multiple formats
- **Progress Tracking**: Rich progress bars showing transcription status
- **Configurable**: Extensive configuration options via environment variables or settings

## Requirements

- Python 3.11 or higher
- GPU support (optional but recommended for better performance)

## Installation

- Install the package from PyPI:

    ```bash
    uv pip install Transcriber
    ```

## Configuration

- Copy the example environment file:

    ```bash
    cp .env.example .env
    ```

- Configure the settings in `.env`:

    ```env
    # Input settings
    INPUT__URLS_OR_PATHS=["Audio_To_Transcribe"]
    INPUT__SKIP_IF_OUTPUT_EXIST=false

    # Output settings
    OUTPUT__OUTPUT_FORMATS=["all"]
    OUTPUT__OUTPUT_DIR="Transcripts"

    # Whisper model settings
    WHISPER__LANGUAGE="ar"

    # Logging settings
    LOGGING__LOG_LEVEL="DEBUG"
    LOGGING__ENABLE_LOGFIRE=true
    LOGGING__LOGFIRE_TOKEN="<your_logfire_token>"
    ```

## Usage

### Basic Usage

```python
from Transcriber.transcriber import transcribe

# Configure the transcriber via .env or parameters, then:
transcribe(
    urls_or_paths=["path/to/audio.mp3", "https://youtube.com/watch?v=example"],
    output_dir="Transcripts",
    output_formats=["txt", "srt"],
    language="ar",
    log_level="INFO",
    enable_logfire=True,  # Optional
    logfire_token="<your_logfire_token>"  # Optional, you can get it from https://logfire.pydantic.dev/login
)
```

### Command Line Usage

```bash
uv run --with Transcriber transcribe
```

### Example Configuration

```python
# Example settings in your .env file
INPUT__URLS_OR_PATHS=["path/to/audio.mp3", "https://youtube.com/watch?v=example"]
OUTPUT__OUTPUT_FORMATS=["txt", "srt"]
WHISPER__LANGUAGE="en"
```

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper)
- [Faster Whisper](https://github.com/guillaumekln/faster-whisper)
