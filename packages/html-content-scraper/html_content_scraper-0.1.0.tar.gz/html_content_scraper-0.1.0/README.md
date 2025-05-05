HTML Content Scraper - README
=============================

Overview
--------

This Python script provides a set of tools for scraping and processing different types of content from web pages, including text, images, audio, and video. It's organized into three main classes: `html`, `run`, and `show`, each serving different purposes in the content scraping and display process.
Features
--------

### 1. `html` Class

* **Text Extraction**: Extracts text content from HTML elements (`div`, `p`, etc.) and saves it to text files.

* **Image Downloading**: Downloads images from specified HTML elements or all images on a page.

* **Audio Downloading**: Extracts and downloads audio files from HTML `audio` elements.

### 2. `run` Class

* **Direct Downloads**: Downloads media files (music, video, text) directly from provided URLs.

* **Video Processing**: Handles video content with optional URL prefixing.

### 3. `show` Class

* **Content Display**: Displays downloaded content, including text files, images, audio, and video.

Usage
-----

### Text Extraction

python

html.txt('br', url, class_name, next_page_class, tag='div', next_tag='div', base_url='https:/', index=None)

* `'br'` or `'p'`: Specifies the extraction mode.

* `url`: The starting URL to scrape.

* `class_name`: The class of the element containing the text.

* `next_page_class`: The class of the element containing the link to the next page.

### Image Downloading

python

html.img(url, container_class=None, prefix=None)

* `url`: The URL of the page containing images.

* `container_class`: Optional. The class of the container element holding the images.

* `prefix`: Optional. A URL prefix to prepend to image sources.

### Audio Downloading

python

html.audio(url, container_class=None)

* `url`: The URL of the page containing audio files.

* `container_class`: Optional. The class of the container element holding the audio files.

### Direct Media Download

python

run.music(url, output_name='1')  # For audio
run.video(url, output_name='1', prefix=None)  # For video
run.txt(url, output_name='1')  # For text

### Display Content

python

show.txt('连续', txt, start=1, end=1)  # Display multiple text files
show.txt('单个', txt)  # Display a single text file
show.image(img)  # Display an image
show.music(mp3)  # Play audio
show.video(mp4)  # Play video
Dependencies
------------

* `requests`: For making HTTP requests.

* `bs4` (BeautifulSoup): For parsing HTML.

* `lxml`: As a parser for BeautifulSoup.

* `PIL` (Pillow): For image display.

* `audioplayer`: For audio playback.

* `moviepy`: For video playback.

Notes
-----

* Ensure all dependencies are installed before running the script.

* The script includes error handling with basic `try-except` blocks.

* User-Agent is set to mimic a Chrome browser to avoid blocking by some websites.

Example
-------

python

# Download images from a webpage

html.img('https://example.com/gallery', 'image-container')

# Display the first downloaded image

show.image('1')

This tool is useful for scraping and organizing content from web pages efficiently. Adjust parameters as needed for specific use cases.HTML Content Scraper - README

Overview
--------

This Python script provides a set of tools for scraping and processing different types of content from web pages, including text, images, audio, and video. It's organized into three main classes: `html`, `run`, and `show`, each serving different purposes in the content scraping and display process.
Features
--------

### 1. `html` Class

* **Text Extraction**: Extracts text content from HTML elements (`div`, `p`, etc.) and saves it to text files.

* **Image Downloading**: Downloads images from specified HTML elements or all images on a page.

* **Audio Downloading**: Extracts and downloads audio files from HTML `audio` elements.

### 2. `run` Class

* **Direct Downloads**: Downloads media files (music, video, text) directly from provided URLs.

* **Video Processing**: Handles video content with optional URL prefixing.

### 3. `show` Class

* **Content Display**: Displays downloaded content, including text files, images, audio, and video.

Usage
-----

### Text Extraction

python

html.txt('br', url, class_name, next_page_class, tag='div', next_tag='div', base_url='https:/', index=None)

* `'br'` or `'p'`: Specifies the extraction mode.

* `url`: The starting URL to scrape.

* `class_name`: The class of the element containing the text.

* `next_page_class`: The class of the element containing the link to the next page.

### Image Downloading

python

html.img(url, container_class=None, prefix=None)

* `url`: The URL of the page containing images.

* `container_class`: Optional. The class of the container element holding the images.

* `prefix`: Optional. A URL prefix to prepend to image sources.

### Audio Downloading

python

html.audio(url, container_class=None)

* `url`: The URL of the page containing audio files.

* `container_class`: Optional. The class of the container element holding the audio files.

### Direct Media Download

python

run.music(url, output_name='1')  # For audio
run.video(url, output_name='1', prefix=None)  # For video
run.txt(url, output_name='1')  # For text

### Display Content

python

show.txt('连续', txt, start=1, end=1)  # Display multiple text files
show.txt('单个', txt)  # Display a single text file
show.image(img)  # Display an image
show.music(mp3)  # Play audio
show.video(mp4)  # Play video
Dependencies
------------

* `requests`: For making HTTP requests.

* `bs4` (BeautifulSoup): For parsing HTML.

* `lxml`: As a parser for BeautifulSoup.

* `PIL` (Pillow): For image display.

* `audioplayer`: For audio playback.

* `moviepy`: For video playback.

Notes
-----

* Ensure all dependencies are installed before running the script.

* The script includes error handling with basic `try-except` blocks.

* User-Agent is set to mimic a Chrome browser to avoid blocking by some websites.

Example
-------

python



# Download images from a webpage

html.img('https://example.com/gallery', 'image-container')

# Display the first downloaded image

show.image('1')

This tool is useful for scraping and organizing content from web pages efficiently. Adjust parameters as needed for specific use cases.
