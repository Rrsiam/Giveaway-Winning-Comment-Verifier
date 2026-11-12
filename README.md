# Giveaway Comment Checker

A web app that checks whether a giveaway winner's comment really exists on a YouTube video or Short. Paste the video link, the comment text and, optionally, the winner's username. The app scans every comment and reply and tells you whether the comment is real, with a direct link to it on YouTube as proof.

## Features

- **No API key or account needed.** It reads comments directly, so there is no Google Cloud setup and no card required.
- **Five comment languages.** English, Bengali, Banglish, Hindi and Hinglish. A Banglish comment matches its Bengali-script version, and a Hinglish comment matches its Devanagari version, even when the spelling varies.
- **Full comments scan.** Checks all top-level comments and replies, and stops early once a verified match is found.
- **Clear results.** Verified, Likely match, Comment found but posted by a different user, or Not found.
- **Three page languages.** English, বাংলা and हिन्दी. Results and error messages switch instantly.
- **Light and dark themes.** A toggle switches between them and remembers your choice.

> **Note:** The app uses the unofficial `youtube-comment-downloader` library instead of the official YouTube API. This is against YouTube's terms of service and can stop working when YouTube changes its pages. Use it for personal checking and testing.

## Live Demo

**Live link:** https://your-demo-link-here *(replace with your deployed link)*

**Run locally:** http://localhost:5000 after following the steps below.

## How to Run

**Requirements:** Python 3.9 or newer and an internet connection.

**1. Get the project**

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git
cd YOUR-REPO
```

You can also download the project as a ZIP, unzip it and open a terminal inside the folder that contains `app.py`.

**2. Create a virtual environment and install dependencies**

Windows:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Mac / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3. Start the app**

```bash
python app.py
```

**4. Open the website**

Go to http://localhost:5000 in your browser.

**How to use it:** paste a YouTube video or Shorts link, add the winner's username if you have it, paste the comment exactly as it appears on YouTube, and click **Check comment**. Large videos can take a few minutes to scan.

Next time, you only need to activate the environment (`venv\Scripts\activate` on Windows, `source venv/bin/activate` on Mac/Linux) and run `python app.py`.

## Project Structure

```
giveaway-verifier-nokey/
├── app.py               Flask server, comment scanning and the /api/verify endpoint
├── matcher.py           Link parsing and English/Bengali/Hindi matching logic
├── templates/
│   └── index.html       Page UI, themes and the three-language text
├── requirements.txt     Python dependencies
├── .gitignore           Keeps cache files and venv out of Git
└── README.md            Project documentation
```
