import { useState, useEffect } from "react";
import { FormControl, InputLabel, Select, MenuItem } from "@mui/material";
import { SpiralOpenskillClient } from "../utils/api";
import { type SpiralOpenskillClientOptions, type Player } from "../utils/api";

interface PlayerDropdownProps {
  label?: string;
  value: number | string;
  onPlayerSelect: (playerId: number) => void;
}

export function PlayerDropdown({
  label,
  value,
  onPlayerSelect,
}: PlayerDropdownProps) {
  const [players, setPlayers] = useState<Array<Player>>(
     []
  );

  async function fetchPlayers(): Promise<Array<Player>> {
    const options: SpiralOpenskillClientOptions = {
      baseUrl: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000",
    };
    const client = new SpiralOpenskillClient(options);
    return client.getPeople();
  }

  const handlePlayerSelect = (playerId: number) => {
    onPlayerSelect(playerId);
  };

  useEffect(() => {
    fetchPlayers().then((players) => setPlayers(players));
    return () => {};
  }, []);

  return (
    <FormControl sx={{ width: 250, m: 1 }} size="small">
      <InputLabel id="player-select-label">
        {label ? label : "Select Player"}
      </InputLabel>
      <Select
        labelId="player-select-label"
        id="player-select"
        value={value}
        label="Select Player"
        onChange={(e) => handlePlayerSelect(e.target.value as number)}
      >
        {players.map((player) => (
          <MenuItem key={player.id} value={player.id}>
            {player.name}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}
