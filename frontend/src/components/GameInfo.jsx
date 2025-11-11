import React from 'react';
import '../styles/GameInfo.css';

function GameInfo({ gameState }) {
  return (
    <div className="game-info">
      <div className="info-section">
        <h3>Current Turn</h3>
        <p className="current-player">Player {gameState.current_player}</p>
        <p className="turn-info">Turn #{gameState.turn_count}</p>
      </div>

      <div className="info-section">
        <h3>Player Status</h3>
        <div className="players-status">
          {gameState.players.map((player) => (
            <div
              key={player.name}
              className={`player-status ${player.is_current ? 'current' : ''}`}
            >
              <strong>{player.name}</strong>
              <p>Team: {player.team}</p>
              <p>Tiles: {player.tile_count}</p>
              <p className="strategy">{player.strategy}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="info-section">
        <h3>Game Status</h3>
        <p>Passes: {gameState.passes}</p>
        {gameState.playable_numbers.length > 0 && (
          <p>Playable: {gameState.playable_numbers.join(', ')}</p>
        )}
        
        {gameState.game_history && gameState.game_history.length > 0 && (
          <div className="game-history">
            <h4>Last Moves</h4>
            <div className="history-list">
              {gameState.game_history.map((move, idx) => (
                <div key={idx} className="history-item">
                  <span className="player-badge">{move.player}</span>
                  <span className="action">
                    {move.action === 'played' 
                      ? `played [${move.tile[0]},${move.tile[1]}]` 
                      : 'passed'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default GameInfo;
