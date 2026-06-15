# Price Comparison Tool

AI-powered grocery price comparison tool. Upload supplier PDF price lists, get a comparison table with trend indicators, and export to Excel with profit margin and selling price calculations.

## Requirements

- [Node.js](https://nodejs.org) v18 or later (download the LTS version)

## Setup (first time only)

1. Unzip this folder somewhere on your computer
2. Open a terminal / command prompt inside the folder
3. Run:

```bash
npm install
```

This installs all dependencies (takes about a minute).

## Running the tool

```bash
npm run dev
```

The tool will start and show something like:

```
  VITE v5.x.x  ready in 300ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.1.10:5173/   ← share this with coworkers
```

- Open the **Local** link on your own computer
- Share the **Network** link with coworkers on the same WiFi/office network — they just open it in their browser, no installation needed

## Usage

1. Click **Settings** at the bottom → paste your Google AI Studio API key
2. Set your profit margin % (default: 30%)
3. Drag & drop your supplier PDF price lists into the upload area
4. Click **Analyse** — the AI reads all PDFs and builds the comparison table
5. Click **Download Excel** to export the full report

## Getting a free API key

1. Go to https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click **Create API key**
4. Copy and paste it into the Settings panel

The free tier allows 1,500 requests/day — more than enough for daily use.

## Stopping the tool

Press `Ctrl + C` in the terminal.
