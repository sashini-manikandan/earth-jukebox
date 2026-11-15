# EARTH//SOUND 🌍

### NASA Earth Information Center Multi-Sensory Jukebox

**Turn Earth imagery into an interactive soundscape.**

EARTH//SOUND is an experimental, accessibility-minded sonification
experience that transforms Earth-observation visualizations into spatial
audio. It combines NASA Scientific Visualization Studio (SVS) imagery
and animations with browser-based Web Audio synthesis, Python-generated
stereo WAV exports, plain-language planetary context, image-based
diagnostics, and optional multimodal AI commentary.

The project explores a simple question:

> What if we could listen to patterns in the images we use to understand
> our planet?

EARTH//SOUND is an educational and creative prototype. It is **not an
official NASA product**, and it does not claim to measure climate
variables directly from rendered image pixels.

------------------------------------------------------------------------

## Table of contents

-   [Project at a glance](#project-at-a-glance)
-   [What you can do](#what-you-can-do)
-   [NASA visualization collection](#nasa-visualization-collection)
-   [How the sonification works](#how-the-sonification-works)
-   [Accessibility](#accessibility)
-   [Scientific integrity and
    limitations](#scientific-integrity-and-limitations)
-   [Technology stack](#technology-stack)
-   [Requirements](#requirements)
-   [Run locally](#run-locally)
    -   [macOS](#macos)
    -   [Windows](#windows)
    -   [Linux](#linux)
-   [Using the application](#using-the-application)
-   [Optional AI analyst setup](#optional-ai-analyst-setup)
-   [Video processing and
    performance](#video-processing-and-performance)
-   [Troubleshooting](#troubleshooting)
-   [Project structure](#project-structure)
-   [Data sources and attribution](#data-sources-and-attribution)
-   [Privacy and API keys](#privacy-and-api-keys)
-   [Roadmap ideas](#roadmap-ideas)
-   [Contributing](#contributing)
-   [License](#license)

------------------------------------------------------------------------

## Earth Jukebox — Team SUPERNOVA FAMILY

**Team SUPERNOVA FAMILY** is pioneering the **Earth Information Jukebox**, a dynamic platform designed to aggregate, harmonize, and stream global planetary data on demand.

By converting complex satellite telemetry, climate metrics, and ecological feeds into accessible, high-density digital streams, the initiative allows researchers, policymakers, and communities to select and visualize vital environmental insights.

EARTH//SOUND brings this vision to life through an interactive, multi-sensory experience: users can explore planetary visualizations, translate visual patterns into sound, and engage with environmental information through both audio and visual interfaces.

## Project at a glance

  -----------------------------------------------------------------------
  Item                                Details
  ----------------------------------- -----------------------------------
  Project                             EARTH//SOUND

  Type                                Interactive web application / data
                                      sonification prototype

  Interface                           Streamlit

  Audio                               Browser Web Audio API and Python
                                      stereo WAV synthesis

  Earth imagery                       NASA Scientific Visualization
                                      Studio (SVS) API and user uploads

  Optional AI                         OpenRouter, Google Gemini, or
                                      OpenAI vision-capable models

  Main entry point                    `app.py`

  Dependencies                        `requirements.txt`
  -----------------------------------------------------------------------

### The experience

1.  Select a NASA Earth visualization, compare two images, or upload
    your own image/video.
2.  The application extracts visual features such as luminance, colour,
    saturation, edges, and spatial variation.
3.  Those features are mapped to musical parameters.
4.  Explore the visualization with the interactive browser synthesizer,
    or render a stereo WAV file.
5.  Read the plain-language context and image-based diagnostics;
    optionally request an AI-generated visual analysis.

------------------------------------------------------------------------

## What you can do

### 1. Explore NASA Earth visualizations

Choose from the built-in NASA EIC/SVS collection. The application
retrieves visualization metadata and preview imagery from the NASA SVS
API. Where a suitable animation is available, it can download and sample
frames for a time-based sonification experience.

If the NASA service or a particular asset is unavailable, the app
attempts to use an offline demonstration fallback rather than treating
the missing network response as a successful data retrieval.

### 2. Compare two moments in time

Use **Before / After Change Comparison** to upload two PNG or JPEG
images. EARTH//SOUND creates a visual transition from the two images,
allowing areas of image difference to influence the resulting
soundscape.

This is a visual comparison, not an independently validated scientific
change-detection product.

### 3. Upload your own Earth imagery

Use **Upload an Image** to work with a PNG or JPEG visualization. This
is useful for satellite images, maps, environmental visualizations, and
other raster imagery.

### 4. Upload a video

Use **Upload a Video** to process supported MP4, MOV, or WEBM clips. The
app samples frames at intervals instead of treating every frame as a
separate full-resolution analysis input.

### 5. Interactive browser synthesizer

The browser player is embedded in the Streamlit page and uses the
browser's Web Audio capabilities. Its controls include:

-   **Enable Audio / Test Sound** --- initializes or resumes browser
    audio after a user gesture.
-   **Play Live Browser Synth** --- starts the live sonification. The
    Space key is also supported.
-   **Stop / Reset** --- stops playback and resets the player. The R key
    is also supported.
-   **Scale selector** --- choose Lydian, Pentatonic, Dorian, or
    Harmonic Minor.
-   **Toggle Latitude Bands** --- show or hide the visual latitude-band
    overlay.
-   **Ear-training cues** --- listen to short examples associated with
    low brightness, high brightness, a bright/lightning-like event, and
    west-to-east panning.
-   **Narration ON/OFF** --- toggle spoken narration using the browser's
    speech synthesis. The V key toggles narration.

The browser may block audio until the user interacts with the page.
Click **Enable Audio / Test Sound** before expecting sound from hover or
playback interactions.

### 6. Python stereo WAV synthesis and export

The application also provides a separate Python audio-rendering path:

1.  Select the sonification profile and harmonic scale in the sidebar.
2.  Adjust scan speed, longitude resolution, drone, transient accents,
    and WAV reverb.
3.  Click **Render Lossless Stereo WAV File**.
4.  Listen using the in-app player.
5.  Download the generated `earth_jukebox_soundscape.wav`.

The browser synthesizer and Python WAV renderer are separate
implementations. Their outputs are designed around related
visual-to-audio ideas, but they are not guaranteed to sound identical.

### 7. Image-based diagnostics

The diagnostics section summarizes properties of the processed image
sequence, including:

-   Mean image-brightness change
-   Brightness concentration
-   Brightest image cell
-   Number of sampled frames
-   A frame-by-band image-brightness heatmap

These metrics describe the rendered image and the app's feature
extraction. They should not be interpreted as direct measurements of
temperature, CO₂ concentration, air quality, forest height, ocean speed,
or another physical climate variable.

### 8. Optional AI Visual & Accessibility Analyst

If you provide an API key for a supported provider, you can request an
AI-generated explanation of the selected visualization and extracted
image patterns. Supported provider choices in the current interface are:

-   OpenRouter
-   Google Gemini
-   OpenAI

The report can also be used as the text source for the browser
narration. AI output is generated commentary, not a NASA-verified
scientific interpretation.

------------------------------------------------------------------------

## NASA visualization collection

The current built-in catalogue includes:

  Visualization                                    NASA SVS ID Theme
  ---------------------------------------------- ------------- ----------------
  Global Sea Surface Currents & Temperature               3912 Ocean
  Perpetual Ocean 2: Western Boundary Currents            5425 Ocean flows
  Change in Night Lights (2012--2023)                     5313 Human activity
  DYAMOND Global Carbon Dioxide                           5196 Atmosphere
  GEDI Forest Height                                      4950 Biodiversity
  Air Quality Model Runs (GEOS-CF)                        5533 Air quality
  GEOS Aerosols                                           5669 Atmosphere
  Lightning Events from the ISS (2017--2023)              5011 Weather
  Atmospheric River (3D Earth System Model)               4960 Water cycle

The catalogue metadata and source links are defined in `app.py`. NASA
assets and API responses are retrieved at runtime, so an internet
connection is required for the live NASA gallery.

------------------------------------------------------------------------

## How the sonification works

EARTH//SOUND analyzes the visual content of an image or sampled frame
sequence. The current feature extraction includes image properties such
as:

-   **Luminance:** how light or dark image regions are.
-   **Saturation and colour:** how intense the colours are and how they
    vary.
-   **Edges and spatial contrast:** where boundaries and sharper visual
    transitions occur.
-   **Brightness distribution:** how bright regions are distributed
    across the image.
-   **Green and hue information:** colour cues that can be useful for
    distinguishing visual patterns in some datasets.

The image is divided into a grid of horizontal bands and longitude-like
columns. Extracted features are mapped to audio characteristics such as
pitch, harmonic content, timbre, transient accents, timing, and stereo
position.

The mapping is an artistic/educational translation of **visual
proxies**. Unless a dataset is separately calibrated and geographically
registered for a specific measurement, the resulting sound does not
represent the underlying physical quantity in its original units.

### Available harmonic scales

  Scale            Intended character
  ---------------- --------------------
  Lydian           Cosmic wonder
  Pentatonic       Meditative Earth
  Dorian           Oceanic mystery
  Harmonic Minor   Climate urgency

The sidebar also exposes a sonification profile, longitude scan
resolution, scan speed, global drone/sub-bass, transient accents, and
WAV reverb settings.

------------------------------------------------------------------------

## Accessibility

Accessibility is part of the project design. Current features include:

-   Keyboard interaction in the browser player.
-   Arrow-key navigation through the interactive image grid.
-   Enter to hear the selected cell.
-   Screen-reader announcements describing the selected band, column,
    and image-brightness proxy.
-   A narration toggle using the browser's speech synthesis.
-   Plain-language planetary context to accompany visualizations.

The browser's speech synthesis depends on the operating system and
browser voices available on the user's device. Audio playback may also
require a user gesture due to browser autoplay policies.

This is an ongoing accessibility effort, not a claim of complete WCAG
conformance. Feedback and testing with assistive technologies are
welcome.

------------------------------------------------------------------------

## Scientific integrity and limitations

EARTH//SOUND is a sonification and science-communication prototype, not
a scientific instrument.

Please keep the following limitations in mind:

1.  **Pixels are not physical measurements.** Brightness, colour,
    saturation, and edges in a rendered visualization are not
    automatically equivalent to temperature, concentration, height,
    speed, or other physical units.
2.  **Geographic orientation matters.** The app's image bands are not
    guaranteed to correspond to actual geographic latitude unless the
    source image is correctly oriented and registered.
3.  **Visual differences are not causal explanations.** A difference
    between two uploaded images can be influenced by projection, colour
    palette, resolution, lighting, compression, or other rendering
    choices.
4.  **AI analysis can be wrong.** Optional AI reports are generated
    explanations and must be checked against the original dataset
    documentation and scientific sources.
5.  **Sonification is a mapping choice.** Different profiles, scales,
    and settings can produce different soundscapes from the same image.
6.  **NASA attribution does not imply NASA endorsement.** NASA SVS is
    used as a source of visualization assets; EARTH//SOUND is an
    independent prototype.

For research, policy, or operational decisions, consult the original
dataset documentation and validated measurements rather than relying on
the app's proxy diagnostics or AI-generated commentary.

------------------------------------------------------------------------

## Technology stack

-   **Python** --- application logic and image/audio processing.
-   **Streamlit** --- interactive web interface and local web server.
-   **NumPy** --- numerical feature processing and audio synthesis.
-   **Pillow** --- image loading, conversion, resizing, and drawing.
-   **Requests** --- NASA SVS API and remote asset retrieval.
-   **SciPy** --- WAV file generation.
-   **Matplotlib** --- diagnostic visualizations.
-   **ImageIO / imageio-ffmpeg** --- video reading and frame sampling.
-   **HTML, CSS, JavaScript, Web Audio API** --- embedded browser
    synthesizer and interaction.
-   **Browser SpeechSynthesis API** --- spoken narration.

------------------------------------------------------------------------

## Requirements

-   Python **3.10 or newer** (Python 3.11 is a good choice).
-   `pip`
-   Internet connection for NASA SVS assets and optional AI analysis.
-   A modern browser with JavaScript and Web Audio support.
-   Enough memory and disk space for the videos you choose to process.

The Python packages and version ranges are listed in `requirements.txt`.

------------------------------------------------------------------------

## Run locally

These instructions assume the repository contains:

``` text
EARTH-SOUND/
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

If your Python file has a different name, replace `app.py` in the
commands below with its actual filename.

### macOS

#### 1. Install or verify Python

Open **Terminal** and run:

``` bash
python3 --version
```

If Python is not installed, install a current Python 3 release from
[python.org](https://www.python.org/downloads/) or use your preferred
package manager.

#### 2. Open the project folder

Move into the folder where you cloned or downloaded the project:

``` bash
cd path/to/EARTH-SOUND
```

For example, if it is in Downloads:

``` bash
cd ~/Downloads/EARTH-SOUND
```

#### 3. Create a virtual environment

``` bash
python3 -m venv .venv
```

#### 4. Activate it

``` bash
source .venv/bin/activate
```

Your terminal prompt should now show `(.venv)`.

#### 5. Upgrade pip and install dependencies

``` bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### 6. Start the application

``` bash
streamlit run app.py
```

Streamlit will print a local address, normally:

``` text
http://localhost:8501
```

Open that address in your browser.

#### 7. Stop the server

Return to Terminal and press:

``` text
Control + C
```

#### 8. Next time you run the project

Open Terminal, enter the project folder, activate the environment, and
run Streamlit:

``` bash
cd path/to/EARTH-SOUND
source .venv/bin/activate
streamlit run app.py
```

### Windows

#### 1. Install or verify Python

Install Python 3.10+ from
[python.org](https://www.python.org/downloads/). During installation,
enable **Add Python to PATH** if the installer offers that option.

Open PowerShell and check:

``` powershell
py --version
```

#### 2. Open the project folder

``` powershell
cd path\to\EARTH-SOUND
```

#### 3. Create a virtual environment

``` powershell
py -3 -m venv .venv
```

#### 4. Activate it

``` powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation because of the execution policy, you can
use Command Prompt instead:

``` bat
.venv\Scripts\activate.bat
```

#### 5. Install dependencies

``` powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### 6. Run the application

``` powershell
streamlit run app.py
```

Open the local URL printed in the terminal, normally
`http://localhost:8501`.

#### 7. Stop the server

Press `Ctrl + C` in the terminal.

### Linux

``` bash
python3 --version
cd path/to/EARTH-SOUND
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501` in your browser. Stop the server with
`Ctrl + C`.

------------------------------------------------------------------------

## Using the application

### Step 1 --- Choose a source

In the left sidebar, select one of the source modes:

-   **NASA EIC Gallery**
-   **Before / After Change Comparison**
-   **Upload an Image**
-   **Upload a Video**

### Step 2 --- Configure animation processing

For NASA animations and uploaded videos, adjust:

-   Maximum video download size.
-   Number of frames to sample.
-   Maximum dimension of sampled frames.

Higher frame counts and larger frame dimensions can preserve more visual
detail, but they also increase download, memory, and processing costs.
Start with the defaults if you are unsure.

### Step 3 --- Choose the sonification mapping

Select a **Sonification Mapping Profile** in the main page and use the
sidebar to tune:

-   Harmonic scale.
-   Longitude scan resolution.
-   Scan speed.
-   Global Earth Choir / sub-bass drone.
-   Lightning / bright-burst chimes.
-   WAV export reverb.

### Step 4 --- Enable browser audio

In the browser player beneath the interactive Earth visualization:

1.  Click **Enable Audio / Test Sound** once.
2.  Click **Play Live Browser Synth** or explore the image with the
    pointer.
3.  Use **Stop / Reset** when you want to stop playback.
4.  Try the scale selector, latitude-band toggle, and ear-training cues.
5.  Switch **Narration ON/OFF** to hear or stop the spoken description.

If you hear nothing, see [Troubleshooting](#troubleshooting).

### Step 5 --- Generate a WAV file

Scroll to **High-Precision Stereo WAV Export & Native Player**:

1.  Click **Render Lossless Stereo WAV File**.
2.  Wait for the render to complete.
3.  Use the built-in audio player to listen.
4.  Click **Download Stereo WAV Soundscape** to save the result.

------------------------------------------------------------------------

## Optional AI analyst setup

The AI analyst is optional. The main NASA browsing, image processing,
browser sonification, diagnostics, and WAV export do not require an AI
API key.

### Supported providers

The sidebar currently offers:

-   OpenRouter
-   Google Gemini
-   OpenAI

### Setup

1.  Create an API key with the provider you intend to use.
2.  Run EARTH//SOUND locally.
3.  In the sidebar, choose the provider.
4.  Paste the key into **Enter API Key**.
5.  Select an available model.
6.  Scroll to **AI Visual & Accessibility Analyst**.
7.  Click **Analyze Visualization & Visual Patterns with AI**.

The application says the entered key is held in session memory and is
not written to disk by the app. Treat API keys as secrets anyway: do not
paste them into source code, commit them to GitHub, or share screenshots
containing them. API usage may incur charges according to the provider's
terms.

Model availability, pricing, and provider API formats can change. If a
selected model stops working, check the provider's current documentation
and choose a supported vision model.

------------------------------------------------------------------------

## Video processing and performance

Video processing is one of the most resource-intensive parts of the
application.

The sidebar provides controls for:

-   Maximum video download: 60--200 MB.
-   Number of sampled frames: 4--20.
-   Maximum sampled-frame dimension: 480, 640, 800, 960, or 1280 pixels.

The app samples frames rather than analyzing every frame in the source
video. The embedded browser player is also kept lighter by using at most
six representative frames, while the Python analysis and WAV export can
use the full sampled frame sequence.

### If a NASA animation is too large

-   Try a smaller maximum download size only if you want a stricter
    safety limit; increase it if you have enough bandwidth and memory.
-   If a NASA video exceeds the configured cap, the app may fall back to
    the still preview.
-   Reduce the number of sampled frames.
-   Reduce the maximum frame dimension.
-   Use the still preview or upload a shorter/lower-resolution clip.

A still preview can still be explored and sonified, but it does not
provide the same time-evolving input as a sampled animation.

------------------------------------------------------------------------

## Troubleshooting

### `streamlit: command not found`

The virtual environment may not be active, or Streamlit may not have
installed correctly.

``` bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

On Windows, activate with:

``` powershell
.\.venv\Scripts\Activate.ps1
```

### `ModuleNotFoundError`

Make sure you are in the project folder and have activated the virtual
environment. Then reinstall:

``` bash
python -m pip install -r requirements.txt
```

### Browser player appears, but there is no sound

1.  Click **Enable Audio / Test Sound** inside the browser player.
2.  Check that the browser tab is not muted.
3.  Check your system output device and volume.
4.  Try a current version of Chrome, Edge, Firefox, or Safari.
5.  Interact with the player after the page loads; browsers commonly
    restrict audio before a user gesture.
6.  Check whether an extension or privacy setting is blocking audio.

The embedded browser synthesizer and the Python WAV renderer are
separate. If browser audio is unavailable, try rendering a WAV file
using the Python export section.

### Narration does not speak

-   Switch **Narration ON** using the player control or press V while
    the player is focused/active.
-   Check system volume and browser audio settings.
-   Confirm that your browser and operating system have a speech voice
    installed.
-   Speech synthesis support and available voices vary by browser and
    operating system.

### NASA gallery does not load

-   Check your internet connection.
-   Retry after a short wait; the NASA SVS service or a particular asset
    may be temporarily unavailable.
-   Try another visualization.
-   The app may display an offline demonstration fallback if the NASA
    API cannot be reached. Check the displayed source/provenance
    information to understand which content is being shown.

### NASA animation falls back to a still image

The selected video may be too large, unavailable, or incompatible with
the current processing environment.

-   Reduce frame count and maximum frame dimension.
-   Try another catalogue item.
-   Allow a larger download cap only if your machine and connection can
    handle it.
-   Continue with the still preview if animation sampling is not
    possible.

### Uploaded video fails to process

-   Confirm that the file is MP4, MOV, or WEBM.
-   Check that it is below the configured upload size limit.
-   Try converting it to a standard H.264 MP4.
-   Reduce the video duration or resolution.
-   Install/reinstall the packages in `requirements.txt`, including
    `imageio-ffmpeg`.

### AI analysis fails

-   Confirm that the selected provider matches the API key.
-   Check that the key is active and has access to the selected model.
-   Check provider billing, quotas, and rate limits.
-   Try another supported vision model.
-   Remember that AI analysis requires an internet connection.

### The app is slow or runs out of memory

-   Reduce video frame count.
-   Reduce maximum frame dimensions.
-   Prefer a still image for quick testing.
-   Close other memory-intensive applications.
-   Avoid processing multiple large videos simultaneously.
-   Restart Streamlit after a failed or unusually large processing run.

------------------------------------------------------------------------

## Project structure

A minimal repository layout is:

``` text
EARTH-SOUND/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation
└── .gitignore          # Files excluded from Git
```

The current application is intentionally delivered as a single main
Python file. The browser synthesizer's HTML, CSS, and JavaScript are
embedded in `app.py` and rendered through Streamlit's HTML component.

### Recommended `.gitignore`

Create a `.gitignore` file in the repository root:

``` gitignore
# Python
__pycache__/
*.py[cod]
*$py.class

# Virtual environments
.venv/
venv/
env/

# Streamlit
.streamlit/secrets.toml

# Local environment and secrets
.env
.env.*
!.env.example

# macOS / Windows
.DS_Store
Thumbs.db
Desktop.ini

# Generated audio and temporary media
*.wav
*.mp3
*.mp4
*.mov
*.webm
*.tmp

# Editor / IDE
.vscode/
.idea/
```

Only add media outputs to Git if you intentionally want them versioned
and have permission to redistribute them.

------------------------------------------------------------------------

## Data sources and attribution

The built-in gallery retrieves visualization metadata and media from the
**NASA Scientific Visualization Studio (SVS)** API:

-   NASA SVS: https://svs.gsfc.nasa.gov/
-   NASA SVS API: https://svs.gsfc.nasa.gov/api/

Each catalogue entry in the application includes a direct NASA SVS
source page. Refer to the individual NASA SVS page for the
visualization's creator credits, dataset details, dates, and
usage/credit guidance.

EARTH//SOUND is an independent project and is not affiliated with,
endorsed by, or operated by NASA. NASA names, imagery, and other assets
remain subject to their respective source terms and attribution
requirements. Verify the conditions for each asset before redistributing
it.

------------------------------------------------------------------------

## Privacy and API keys

-   Uploaded images and videos are processed by the running application
    to create the visual analysis and audio output.
-   NASA gallery mode retrieves remote content from NASA SVS.
-   Optional AI analysis sends the selected image and relevant
    prompt/context to the AI provider selected by the user. Do not
    enable this feature with sensitive or confidential imagery.
-   The app's API-key input is held in Streamlit session memory and is
    not written to disk by the application code. Do not commit keys to
    the repository.
-   If you deploy the application to a public server, remember that
    uploaded files and API requests are handled by that server
    environment. Review hosting-provider privacy, retention, and
    resource policies before accepting other users' data.

------------------------------------------------------------------------

## Roadmap ideas

Possible future directions include:

-   More sonification profiles tailored to different Earth systems.
-   Better synchronization between browser playback and exported WAV
    audio.
-   More explicit data provenance and dataset-specific calibration
    support where scientifically justified.
-   Expanded keyboard and screen-reader testing.
-   User-selectable narration speed and voice.
-   More efficient streaming and caching for large NASA animations.
-   Exportable visual/audio session settings.
-   Modularizing the current single-file application into separate data,
    audio, UI, and accessibility modules.

These are possible extensions, not features promised by the current
version.

------------------------------------------------------------------------

## Contributing

Suggestions, bug reports, accessibility feedback, and improvements are
welcome.

When reporting a problem, include:

-   Operating system and version.
-   Python version.
-   Browser and version.
-   The selected source mode and dataset.
-   Whether the issue affects browser audio, narration, video sampling,
    AI analysis, or WAV export.
-   The full error message, with API keys and personal information
    removed.

For code changes, please describe the user-facing behavior being changed
and test the affected workflow locally before opening a pull request.

------------------------------------------------------------------------

## License

No license is declared by this README. Before publishing the repository,
choose a license that matches how you want others to use, modify, and
redistribute your code. Also review the separate attribution and usage
conditions for NASA imagery and any third-party assets.

------------------------------------------------------------------------

**EARTH//SOUND --- Listen to the planet, one pixel at a time.** 🌍🎧
