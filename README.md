# DASH MPD Checker

The DASH MPD Checker is a Python script that allows you to check DASH (Dynamic Adaptive Streaming over HTTP) media presentation description (MPD) files and their corresponding chunk URLs. The script provides various functionalities to validate DASH content and retrieve essential information about audio and video chunks.

## Prerequisites

- Python 3.x
- XML ElementTree module

## Installation

1. Clone the repository to your local machine.
2. Install the required Python packages:

   ```bash
   pip install xml.etree.ElementTree
## Usage
Navigate to the project directory and run the script:

python dash_checker.py

The script will display a menu with the following options:

         * Check URL Chunk: Check if a specific URL is a valid chunk URL.
         * Total Number of Chunks and Range: Display the total number of audio and video chunks, along with their start and end times.
         * Print Chunk URLs (saves the file in the same directory as the manifest): Generate an HTML file with all the chunk URLs.
         * Follow the on-screen instructions and provide the required inputs as prompted.
