import React from 'react';
import '../styles/PlayerHand.css';

function PlayerHand({ tiles, validMoves, selectedTile, onTileSelect, disabled }) {
  const renderTile = (tile, index) => {
    const isValid = validMoves.includes(index);
    const isSelected = selectedTile === index;

    return (
      <button
        key={index}
        className={`tile player-tile ${isValid ? 'valid' : 'invalid'} ${isSelected ? 'selected' : ''}`}
        onClick={() => isValid && onTileSelect(index)}
        disabled={disabled || !isValid}
        title={isValid ? 'Click to play' : 'Cannot play this tile'}
      >
        <div className="tile-half">{tile[0]}</div>
        <div className="tile-divider"></div>
        <div className="tile-half">{tile[1]}</div>
      </button>
    );
  };

  return (
    <div className="player-hand">
      <div className="tiles-container">
        {tiles.map((tile, index) => renderTile(tile, index))}
      </div>
      <p className="tile-count">Total tiles: {tiles.length}</p>
    </div>
  );
}

export default PlayerHand;
