# Stock Video Downloader Pro

A professional tool for searching and downloading stock videos from Pexels and Pixabay, featuring an AI assistant for generating search prompts.

![Stock Downloader](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green)

## Features

- 🎥 **Multi-Source Search**: Search videos on Pexels and Pixabay simultaneously.
- 🤖 **AI Assistant**: Integrated Google Gemini AI to generate professional search prompts from your scenario descriptions.
- ⬇️ **Batch Download**: Download multiple videos at once with progress tracking.
- 🎨 **Modern UI**: Sleek, dark-themed interface for a professional experience.
- ⚙️ **Easy Configuration**: Simple settings panel to manage your API keys.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/stock-parser-downloader.git
   cd stock-parser-downloader
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Configuration

You will need API keys for the services you want to use:

- **Pexels**: [Get API Key](https://www.pexels.com/api/)
- **Pixabay**: [Get API Key](https://pixabay.com/api/docs/)
- **Google Gemini**: [Get API Key](https://makersuite.google.com/app/apikey)

Enter these keys in the **Settings** tab of the application.

## Architecture

The project follows a modular SOLID architecture:

- `src/models`: Data models
- `src/services`: Business logic and API clients
- `src/ui`: User interface components
- `src/utils`: Helper utilities

## Credits

Original concept by the user.