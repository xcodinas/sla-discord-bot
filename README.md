# Solo leveling Discord BOT
- You can extract the text from the battle tier image and assign roles depending on the combat value

## Requirements

- Python 3.6+
- OpenCV
- pytesseract
- googletrans

## Installation

### Install Python Packages

Install the required Python packages using `pip`:

```bash
pip install opencv-python pytesseract googletrans==4.0.0-rc1
```

### Install Tesseract

You need to have Tesseract 5.3.4 installed in order to this to work

#### Windows

1. Download and install Tesseract from [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki).
2. Add Tesseract to your system's PATH or specify the path in the script.

#### Linux

Install Tesseract using the package manager:

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

## Usage

1. Run the script:

```bash
python script.py
```

## Testing

```bash
python -m unittest discover -s tests
```
