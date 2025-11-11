import React from 'react';
import '../styles/StartMenu.css';

function StartMenu({ onStartGame }) {
  const positions = [
    {
      index: 0,
      name: 'A',
      teammate: 'C',
      opponents: 'B & D'
    },
    {
      index: 1,
      name: 'B',
      teammate: 'D',
      opponents: 'A & C'
    },
    {
      index: 2,
      name: 'C',
      teammate: 'A',
      opponents: 'B & D'
    },
    {
      index: 3,
      name: 'D',
      teammate: 'B',
      opponents: 'A & C'
    }
  ];

  return (
    <div className="start-menu">
      <div className="menu-container">
        <h1>Domino Game</h1>
        <p className="subtitle">Choose your position</p>

        <div className="options">
          {positions.map((pos) => (
            <button
              key={pos.index}
              className={`menu-button player-${pos.name.toLowerCase()}`}
              onClick={() => onStartGame(pos.index)}
            >
              <h3>Play as Player {pos.name}</h3>
              <p>Your teammate: Player {pos.teammate}</p>
              <p>Opponents: Players {pos.opponents}</p>
            </button>
          ))}
        </div>

        <div className="info-section">
          <h3>How to Play</h3>
          <ul>
            <li>Click on a tile in your hand to play it</li>
            <li>Valid moves are highlighted in blue</li>
            <li>If a tile can play on both ends, choose the side</li>
            <li>Try to empty your hand before your opponents</li>
            <li>Your AI teammates will help you win!</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default StartMenu;
