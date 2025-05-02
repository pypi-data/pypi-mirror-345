# anyvec

AnyVec is an open-source Python package that makes it easy to vectorize any type of file — text, images, audio, video, or code — through a single, unified interface. Traditionally, embedding different data types (like text vs. images) requires different models and disparate code paths. AnyVec abstracts away these complexities, allowing you to work with a unified API for all your vectorization needs, regardless of file type.

---

## How It Works

AnyVec automatically detects the file type and processes it using the appropriate extractor.

---

## Supported File Types

| Category         | Extensions / MIME Types                                                                                                                                           |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Text**         | .txt, .md, .rtf, .json, .xml, .csv, .tsv, .log, .html, .markdown, .rst, .yaml, .yml                                                                               |
| **Image**        | .png, .jpg, .jpeg, .bmp, .gif, .tiff, .tif, .webp, .ico, .svg, .jfif, .heic, .avif                                                                                |
| **Audio**        | .mp3, .wav, .ogg, .m4a, .flac, .aac, .webm, .mp4a, .mpeg, .mp4, .x-wav, .x-flac, .mp4a-latm                                                                       |
| **Video**        | .mp4, .webm, .ogg, .mov, .mkv, .avi, .wmv, .mpeg, .mpg, .x-msvideo, .x-ms-wmv, .x-matroska, .quicktime                                                            |
| **Spreadsheet**  | .xlsx, .xls, .ods                                                                                                                                                 |
| **Word**         | .docx, .dotx, .dotm, .docm, .odt                                                                                                                                  |
| **Presentation** | .pptx, .ppsx, .pptm, .odp                                                                                                                                         |
| **PDF**          | .pdf                                                                                                                                                              |
| **EPUB**         | .epub                                                                                                                                                             |
| **Postscript**   | .ps                                                                                                                                                               |
| **Code**         | .py, .js, .ts, .tsx, .jsx, .java, .cpp, .c, .h, .hpp, .cs, .go, .rb, .php, .pl, .sh, .swift, .scala, .lua, .f90, .f95, .erl, .exs, .bat, .sql, .lisp, .vb, .ipynb |

> For the most up-to-date list, see the `mime_handlers` dictionary in the codebase.

### Processing Flow

1. **File Type Detection:** AnyVec uses MIME type and file extension to determine the file type.
2. **Extraction:** The relevant extractor parses text, images, or audio from the file.
3. **Vectorization:** The extracted content is sent to a CLIP-like model via API for embedding.
4. **Unified Output:** You get back text and image vectors, regardless of input type.

---

### Detailed Processing Flow

**Text Files:**

- Extracts raw text using format-appropriate parsers.
- Returns extracted text for vectorization.

**Image Files:**

- Returns the image data as base64-encoded JPEGs or PNGs.
- Optionally, OCR (optical character recognition) can be performed for text extraction.

**Audio Files:**

- Audio bytes are sent to a transcription server (e.g., OpenAI Whisper).
- The server returns the transcribed text, which is then vectorized.
- Requires `whisper` and `ffmpeg` to be installed.

**Video Files:**

- The video is processed in two ways:
  1. **Audio Extraction & Transcription:**
     - Audio is extracted from the video using MoviePy (`from moviepy import VideoFileClip`).
     - The extracted audio is sent to the `/transcribe` endpoint in your docker container (compatible with Whisper or similar servers).
     - The returned transcript is used for vectorization.
  2. **Frame Extraction:**
     - Frames are extracted at 1-second intervals (and the first frame) using OpenCV.
     - Frames are returned as base64-encoded JPEGs for downstream processing or vectorization.
- Both transcript (text) and frames (images) are returned.

**Return Values:**

- For text, audio, and video: returns extracted text (or transcript) and/or images (frames).
- For images: returns images and optionally OCR text.

---

## Quick Start / Usage

### Installation

```bash
pip install anyvec
# or, with Poetry
poetry add anyvec
```

### Basic Example

```python
from anyvec.processing.processor import Processor

with open("path/to/your/file.pdf", "rb") as f:
    file_bytes = f.read()

processor = Processor(client=object())  # Replace with your actual client
text, images = processor.process(file_bytes, "file.pdf")

print("Extracted text:", text)
print("Extracted images:", images)
```

- For audio and video files, make sure you have [Whisper](https://github.com/openai/whisper) installed (see below).
- For image and document files, no extra dependencies are required.

---

## Building the CLIP Docker Image

**First, clone this repository and change into the project directory:**

```bash
git clone https://github.com/mxy680/clip-inference.git
cd clip-inference
```

Then, to build the Docker image for the CLIP component, run the following commands from the project root:

```bash
cd clip
LOCAL_REPO="multi2vec-clip" \
  TEXT_MODEL_NAME="sentence-transformers/clip-ViT-B-32-multilingual-v1" \
  CLIP_MODEL_NAME="clip-ViT-B-32" \
  ./scripts/build.sh
```

## Running the CLIP Docker Container

After building the image, run the container and map port 8000 on your host to port 8080 in the container (where the API runs):

```bash
docker run --rm -it -p 8000:8080 multi2vec-clip
```

The API will then be available at http://localhost:8000.

To run the container in detached mode (in the background), use:

```bash
docker run -d -p 8000:8080 multi2vec-clip
```

The API will still be available at http://localhost:8000 while the container runs in the background.

---
