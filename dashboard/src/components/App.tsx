import { PlayerDropdown } from "./PlayerDropdown";
import { useEffect, useState } from "react";
import {
  CssBaseline,
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Paper,
  Container,
} from "@mui/material";
import { Menu } from "@mui/icons-material";
import { SpiralOpenskillClient, type RankHistory } from "../utils/api";
import SkillChart from "./SkillChart";

const apiClient = new SpiralOpenskillClient({
  baseUrl: "http://localhost:8000",
});


function App() {
  const [selectedPlayer, setSelectedPlayer] = useState<number>(0);
  const [rankHistory, setRankHistory] = useState<RankHistory>({
    player_id: selectedPlayer,
    history: [],
  });

  const updatePlayer = (playerId: number) => {
    setSelectedPlayer(playerId);
  };

  const graphData = rankHistory.history.map((entry) => {
    return {
      datetime: new Date(entry.datetime),
      mu: entry.mu,
      lowerBound: entry.mu - 3 * entry.sigma,
      upperBound: entry.mu + 3 * entry.sigma,
    };
  });



  useEffect(() => {
    if (selectedPlayer !== 0) {
      apiClient.getRankHistory(selectedPlayer).then((data) => {
        setRankHistory(data);
      });
    }
  }, [selectedPlayer]);


  return (
    <>
      <CssBaseline />
      <AppBar position="static">
        <Toolbar>
          <IconButton
            size="large"
            edge="start"
            color="inherit"
            aria-label="menu"
            sx={{ mr: 2 }}
          >
            <Menu />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Spiral Stats
          </Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="xl">
        <Paper elevation={1} variant="outlined">
          <Paper elevation={2}>
            <PlayerDropdown onPlayerSelect={updatePlayer} />
          </Paper>
          <SkillChart data={graphData} />
        </Paper>
      </Container>
    </>
  );
}

export default App;
