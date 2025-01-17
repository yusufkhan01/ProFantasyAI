import React, { useState, useEffect } from 'react';

function App() {
  const [players, setPlayers] = useState([]);

  useEffect(() => {
    fetch("/home")
      .then((res) => res.json())
      .then((home) => {
        const formattedPlayers = home.best_team.map((player) => {
          return `${player[0]} (${player[1]}): ${player[2]} (${player[3]})`;
        });
        setPlayers(formattedPlayers);
      })
      .catch((err) => console.error("Error fetching data:", err));
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Best Fantasy Premier League Team</h1>
        {/* Dynamically render player data */}
        {players.length > 0 ? (
          players.map((player, index) => <p key={index}>{player}</p>)
        ) : (
          <p>Loading team data...</p>
        )}
      </header>
    </div>
  );
}

export default App;
