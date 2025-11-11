import React from 'react';
import '../styles/GameBoard.css';

function GameBoard({ gameState }) {
  const renderTile = (tile) => {
    return (
      <div className="tile board-tile">
        <div className="tile-half">{tile[0]}</div>
        <div className="tile-divider"></div>
        <div className="tile-half">{tile[1]}</div>
      </div>
    );
  };

  return (
    <div className="game-board">
      <h2>Table</h2>
      <div className="table-display">
        {gameState.table.length === 0 ? (
          <p className="empty-table">Waiting for Player A to play the first tile...</p>
        ) : (
          <div className="tiles-sequence">
            {gameState.table.map((tile, index) => (
              <div key={index} className="tile-wrapper">
                {renderTile(tile)}
              </div>
            ))}
          </div>
        )}
      </div>
      
      {gameState.playable_numbers.length > 0 && (
        <div className="playable-info">
          <p>Playable numbers: <strong>{gameState.playable_numbers.join(' or ')}</strong></p>
        </div>
      )}
    </div>
  );
}

export default GameBoard;
