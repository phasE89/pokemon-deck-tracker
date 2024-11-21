# Pokemon Pocket Deck Tracker

A simple and efficient desktop application for tracking your Pokemon Trading Card Game matches, decks, and statistics.

## Features

Track your Pokemon TCG matches with details including your deck choice, opponent's archetype, match result, and optional notes. The application automatically records timestamps and maintains comprehensive statistics about your performance.

The deck management system allows you to easily add new decks, rename existing ones, or remove those you no longer use. All match data is automatically updated when you make changes to your deck names.

Get detailed statistics about your performance, including win rates for each deck and specific matchup data. View your complete match history and edit past entries if needed.

## Installation

Clone the repository and install the required dependencies:

```
bash
git clone https://github.com/yourusername/pokemon-deck-tracker.git
cd pokemon-deck-tracker
pip install -r requirements.txt
```

Run the application by executing `python pokemon-deck-tracker.py` or double-clicking `run.bat` on Windows.

## Project Structure

```
pokemon-deck-tracker/
├── data/            # Directory for storing match data
├── static/          # Static files (images, icons)
├── pokemon-deck-tracker.py   # Main application file
├── run.bat          # Windows batch file to run the application
├── requirements.txt  # Python dependencies
├── .gitignore       # Git ignore file
└── README.md        # This file
```

## Usage

The main window provides an intuitive interface for recording matches. Simply enter your deck name (or select from existing ones), specify your opponent's archetype, select the match result, and optionally add any notes about the game.

View your statistics by selecting a deck from the dropdown menu and clicking "Show Stats". The application will display your overall win rate and detailed matchup-specific data.

The deck management window allows you to organize your decks, while the match history viewer lets you review and edit past matches.

All data is stored locally in JSON format in the `data` directory, making it easy to back up or transfer your match history.

## Requirements

The application requires Python 3.6 or newer and uses PySimpleGUI for the interface. All necessary dependencies are listed in requirements.txt.

## Support and Contributing

If you encounter any issues or have suggestions for improvements, please open an issue on GitHub. Contributions are welcome through pull requests.

## License

This project is open source and available under the MIT License.

---
Pokemon and Pokemon Trading Card Game are trademarks of Nintendo/Creatures Inc./GAME FREAK inc.