import { useState, useEffect } from "react";
import { FormControl, InputLabel, Select, MenuItem, Box } from "@mui/material";
import { SpiralOpenskillClient } from "../utils/api";
import { type SpiralOpenskillClientOptions, type Player } from "../utils/api";

interface PlayerDropdownProps {
    onPlayerSelect?: (playerId: number) => void;
}

export function PlayerDropdown({ onPlayerSelect }: PlayerDropdownProps) {
  const [selectedPlayer, setSelectedPlayer] = useState<number | string>("");
  const [players, setPlayers] = useState<Array<Player>>([]);

  async function fetchPlayers(): Promise<Array<Player>> {
      const options: SpiralOpenskillClientOptions = {
        baseUrl: "http://localhost:8000",
      };
      const client = new SpiralOpenskillClient(options);
      return client.getPeople();
  }

  const handlePlayerSelect = (playerId: number) => {
    setSelectedPlayer(playerId);
    if (onPlayerSelect) {
      onPlayerSelect(playerId);
    }
}

  useEffect(() => {
    fetchPlayers().then((players) => setPlayers(players));
    return () => {};
  }, []);

  return (
      <FormControl sx={{ minWidth: 250, m: 1}} size="small">
        <InputLabel id="player-select-label">Select Player</InputLabel>
        <Select
          labelId="player-select-label"
          id="player-select"
          value={selectedPlayer}
          label="Select Player"
          onChange={(e) => handlePlayerSelect(e.target.value as number)}
        >
          {players.map((player) => (
            <MenuItem key={player.id} value={player.id}>{player.name}</MenuItem>
          ))}
        </Select>
      </FormControl>
  )
}
