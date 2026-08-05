# Cradlewise Integration for Home Assistant

A custom integration for Home Assistant to monitor Cradlewise Smart Crib status and sleep metrics via the official Cradlewise Data API v1 (Beta).

## Features
- Real-time status monitoring (sleeping, awake, stirring, crying, away)
- Live state tracking for baby presence in crib, bounce mode, and music mode
- Daily sleep metrics (Total Night Sleep, Total Day Sleep, Longest Sleep Stretch)
- Built-in rate limiting protection adhering to Cradlewise API constraints

## Installation

### Via HACS (Custom Repository)
1. Open **HACS** in Home Assistant.
2. Click the 3 dots in the top right corner and select **Custom repositories**.
3. Add `https://github.com/jakeshuemake/ha-cradlewise-integration` as an **Integration**.
4. Search for "Cradlewise" in HACS and click **Download**.
5. Restart Home Assistant.

## Setup
1. Go to **Settings** -> **Devices & Services**.
2. Click **Add Integration** and search for **Cradlewise**.
3. Enter your Cradlewise Data API Bearer Token (generated from the Cradlewise Web Dashboard).
