# Domino Game - Web Version Setup Guide

This project consists of a Python Flask backend and a React frontend for the Domino game.

## Prerequisites

- Python 3.7+
- Node.js 14+ and npm
- Git

## Backend Setup (Flask API)

### 1. Install Python dependencies

```bash
cd /Users/daniel/Code/Domino
pip install flask flask-cors
```

### 2. Run the Flask server

```bash
python api.py
```

The API will start on `http://localhost:5000`

## Frontend Setup (React)

### 1. Create React app (if not already done)

```bash
npx create-react-app frontend
cd frontend
```

### 2. Copy component files

The component files have been created in:
- `frontend/src/App.jsx`
- `frontend/src/App.css`
- `frontend/src/components/GameBoard.jsx`
- `frontend/src/components/PlayerHand.jsx`
- `frontend/src/components/GameInfo.jsx`
- `frontend/src/components/StartMenu.jsx`
- `frontend/src/styles/GameBoard.css`
- `frontend/src/styles/PlayerHand.css`
- `frontend/src/styles/GameInfo.css`
- `frontend/src/styles/StartMenu.css`

### 3. Install dependencies

```bash
cd frontend
npm install
```

### 4. Start the React development server

```bash
npm start
```

The app will open at `http://localhost:3000`

## Running the Full Application

### Terminal 1 - Start the Backend

```bash
cd /Users/daniel/Code/Domino
python api.py
```

### Terminal 2 - Start the Frontend

```bash
cd /Users/daniel/Code/Domino/frontend
npm start
```

Then open your browser to `http://localhost:3000`

## Game Features

### Players

- **Player A/C (You)**: Controlled by mouse clicks
- **Player B/D**: AI-controlled with different strategies

### Strategies

- **Win**: Maximizes personal winning chances
- **Help**: Supports teammate's victory
- **Block**: Tries to prevent opponent's winning
- **AI**: Balanced strategy considering both personal and team victory
- **User**: Human-controlled player

### Game Rules

1. Each player starts with 7 tiles
2. Player A starts first
3. Players must play tiles that match the numbers on the table ends
4. If no valid move exists, the turn is skipped
5. Game ends when:
   - A player empties their hand (wins)
   - All players pass (game locked - lowest points wins)

### Valid Moves

- Blue tiles are valid to play
- Gray tiles cannot be played
- Click a tile to play it
- If the tile can go on both ends, you'll be asked to choose left or right

## Troubleshooting

### CORS Errors

If you see CORS errors, make sure the Flask server is running with CORS enabled.

### Port Already in Use

- Flask default: 5000
- React default: 3000

Change ports if needed:
```bash
# Flask
python api.py --port 5001

# React
npm start -- --port 3001
```

### Module Not Found Errors

Make sure all dependencies are installed:
```bash
# For Flask
pip install flask flask-cors

# For React
npm install
```

## Modifying Strategies

To change AI strategies, edit the `startNewGame` function in `api.py`:

```python
players[0].strategy = "Win"      # Change this
players[1].strategy = "Block"    # Or this
players[2].strategy = "Help"     # Or this
players[3].strategy = "Block"    # Or this
```

Available strategies: `"Win"`, `"Help"`, `"Block"`, `"AI"`, `"User"`

## Project Structure

```
Domino/
├── runme.py              # Core game logic
├── api.py                # Flask backend API
├── ui.py                 # Terminal UI (legacy)
├── frontend/             # React frontend
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── components/
│   │   │   ├── GameBoard.jsx
│   │   │   ├── PlayerHand.jsx
│   │   │   ├── GameInfo.jsx
│   │   │   └── StartMenu.jsx
│   │   └── styles/
│   │       ├── GameBoard.css
│   │       ├── PlayerHand.css
│   │       ├── GameInfo.css
│   │       └── StartMenu.css
│   └── package.json
└── README.md
```

## Future Enhancements

- WebSocket for real-time multiplayer
- Player statistics and leaderboard
- Custom strategy creation
- Game replay functionality
- Mobile-responsive improvements
- Dark mode theme
