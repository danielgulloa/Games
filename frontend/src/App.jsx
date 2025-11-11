import React, { useState } from 'react';
import './App.css';
import GameBoard from './components/GameBoard';
import PlayerHand from './components/PlayerHand';
import GameInfo from './components/GameInfo';
import StartMenu from './components/StartMenu';

function App() {
  const [gameState, setGameState] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [gameStarted, setGameStarted] = useState(false);
  const [selectedTile, setSelectedTile] = useState(null);
  const [ambiguousTileInfo, setAmbiguousTileInfo] = useState(null);
  const [validMoves, setValidMoves] = useState([]);
  const [playerPosition, setPlayerPosition] = useState(null);

  const API_URL = '/api';

  // Fetch game state
  const fetchGameState = async () => {
    try {
      const response = await fetch(`${API_URL}/game/state`);
      if (!response.ok) throw new Error('Failed to fetch game state');
      const data = await response.json();
      setGameState(data);
      setError(null);
      await fetchValidMoves();
    } catch (err) {
      setError(err.message);
    }
  };

  // Fetch valid moves
  const fetchValidMoves = async () => {
    try {
      const response = await fetch(`${API_URL}/game/get-valid-moves`);
      if (!response.ok) throw new Error('Failed to fetch valid moves');
      const data = await response.json();
      setValidMoves(data.valid_moves);
      return data;
    } catch (err) {
      setError(err.message);
    }
  };

  // Start a new game
  const startNewGame = async (playerPosition) => {
    setLoading(true);
    setError(null);
    try {
      console.log(`Starting game as player position ${playerPosition}`);
      const response = await fetch(`${API_URL}/game/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ player_position: playerPosition })
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Server error: ${response.status} - ${errorText}`);
      }
      
      const data = await response.json();
      console.log('Game started:', data);
      setGameState(data);
      setPlayerPosition(playerPosition);
      setGameStarted(true);
      setSelectedTile(null);
      await fetchValidMoves();
    } catch (err) {
      console.error('Error starting game:', err);
      setError(`Failed to start game: ${err.message}. Make sure the Flask server is running on http://localhost:5001`);
    } finally {
      setLoading(false);
    }
  };

  // Play a tile
  const playTile = async (tileIndex, side = null) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/game/play`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tile_index: tileIndex, side })
      });
      if (!response.ok) throw new Error('Failed to play tile');
      const data = await response.json();
      setGameState(data.game_state);
      setError(null);
      setSelectedTile(null);
      setAmbiguousTileInfo(null);
      
      // Auto-refresh if not the player's turn
      if (data.game_state.current_player !== 'A' && data.game_state.current_player !== 'C') {
        setTimeout(() => {
          fetchGameState();
        }, 1000);
      } else {
        await fetchValidMoves();
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Skip turn when no valid moves
  const skipTurn = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/game/skip`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      if (!response.ok) throw new Error('Failed to skip turn');
      const data = await response.json();
      setGameState(data.game_state);
      setError(null);
      setSelectedTile(null);
      
      // Refresh valid moves for the next player
      await fetchValidMoves();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Handle tile selection
  const handleTileSelect = async (index) => {
    if (!validMoves.includes(index)) return;

    setSelectedTile(index);

    // Check if this tile is ambiguous (can play on both sides)
    const validMovesData = await fetchValidMoves();
    if (validMovesData && validMovesData.ambiguous_tiles.includes(index)) {
      setAmbiguousTileInfo(index);
    } else {
      setAmbiguousTileInfo(null);
      await playTile(index);
    }
  };

  // Handle side selection for ambiguous tiles
  const handleSideSelect = async (side) => {
    if (selectedTile !== null) {
      await playTile(selectedTile, side);
    }
  };

  // Reset game
  const handleResetGame = async () => {
    await fetch(`${API_URL}/game/reset`, { method: 'POST' });
    setGameStarted(false);
    setGameState(null);
    setPlayerPosition(null);
    setSelectedTile(null);
    setAmbiguousTileInfo(null);
    setError(null);
  };

  if (!gameStarted) {
    return <StartMenu onStartGame={startNewGame} />;
  }

  if (error) {
    return (
      <div className="error-container">
        <h2>Error</h2>
        <p className="error-message">{error}</p>
        <button onClick={() => setError(null)}>Dismiss</button>
        <p className="error-hint">
          If you see "Failed to connect", make sure the Flask backend is running:
          <br />
          <code>cd /Users/daniel/Code/Domino && python api.py</code>
        </p>
      </div>
    );
  }

  if (!gameState) {
    return <div className="loading">Loading game...</div>;
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Domino Game</h1>
        <button onClick={handleResetGame} className="reset-btn">New Game</button>
      </header>

      <div className="game-container">
        <GameInfo gameState={gameState} />
        
        <div className="game-board-section">
          <GameBoard gameState={gameState} />
        </div>

        <div className="player-section">
          <h3>Your Hand</h3>
          <PlayerHand
            tiles={gameState.players[playerPosition].tiles}
            validMoves={validMoves}
            selectedTile={selectedTile}
            onTileSelect={handleTileSelect}
            disabled={loading || gameState.game_over}
          />
        </div>

        {ambiguousTileInfo !== null && (
          <div className="side-selection">
            <p>Where do you want to play this tile?</p>
            <button onClick={() => handleSideSelect('L')} className="side-btn">Left</button>
            <button onClick={() => handleSideSelect('R')} className="side-btn">Right</button>
          </div>
        )}

        {validMoves.length === 0 && !gameState.game_over && (
          <div className="no-moves">
            <p>No valid moves available!</p>
            <button onClick={skipTurn} disabled={loading} className="skip-btn">
              {loading ? 'Skipping...' : 'Skip Turn'}
            </button>
          </div>
        )}

        {gameState.game_over && (
          <div className="game-over">
            <h2>Game Over!</h2>
            {gameState.game_locked ? (
              <>
                <div className="team-scores">
                  <div className="team-score">
                    <strong>Team AC:</strong> {gameState.team_ac_points} points
                  </div>
                  <div className="team-score">
                    <strong>Team BD:</strong> {gameState.team_bd_points} points
                  </div>
                </div>
                <p className={`win-message ${gameState.winner === 'A' ? 'team-ac-win' : 'team-bd-win'}`}>
                  {gameState.winner === 'A' 
                    ? 'Team AC wins!' 
                    : 'Team BD wins!'}
                  {playerPosition !== null && (
                    <>
                      {' '}
                      {(playerPosition === 0 || playerPosition === 2) === (gameState.winner === 'A')
                        ? '🎉 You win!' 
                        : '😢 You lose!'}
                    </>
                  )}
                </p>
              </>
            ) : (
              <p className="win-message">
                {gameState.winner === gameState.players[playerPosition]?.name
                  ? '🎉 You win!'
                  : `Player ${gameState.winner} wins!`}
              </p>
            )}
            <button onClick={handleResetGame} className="play-again-btn">Play Again</button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
