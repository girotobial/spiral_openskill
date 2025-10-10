import { PlayerDropdown } from "./PlayerDropdown";
import { useEffect, useState } from "react";
import {
  CssBaseline,
  Box,
  AppBar,
  Toolbar,
  Typography,
  Paper,
  Container,
  Stack,
  Card,
  CardContent,
} from "@mui/material";
import {
  SpiralOpenskillClient,
  type RankHistory,
  type PlayerStats,
  type OtherPlayerStats,
} from "../utils/api";
import SkillChart from "./SkillChart";
import { Gauge } from "@mui/x-charts";
import { PartnerTable } from "./PartnerTable";

const apiClient = new SpiralOpenskillClient({
  baseUrl: "http://localhost:8000",
});

function App() {
  const [selectedPlayer, setSelectedPlayer] = useState<number>(0);
  const [rankHistory, setRankHistory] = useState<RankHistory>({
    player_id: selectedPlayer,
    history: [],
  });
  const [playerStats, setPlayerStats] = useState<PlayerStats>({
    player_id: selectedPlayer,
    averagePointsDifference: 0,
    totalMatches: 1,
    wins: 0,
  });
  const [partnerStats, setPartnerStats] = useState<OtherPlayerStats>({
    playerId: selectedPlayer,
    clubId: 1,
    partners: []
  })

  const updatePlayer = (playerId: number) => {
    setSelectedPlayer(playerId);
  };

  const graphData = rankHistory.history.map((entry) => {
    return {
      datetime: new Date(entry.datetime),
      mu: entry.mu,
      lowerBound:
        entry.mu - 3 * entry.sigma > 0 ? entry.mu - 3 * entry.sigma : 0,
      upperBound: entry.mu + 3 * entry.sigma,
    };
  });

  useEffect(() => {
    if (selectedPlayer !== 0) {
      apiClient.getRankHistory(selectedPlayer).then((data) => {
        setRankHistory(data);
      });
      apiClient.getPlayerStats(selectedPlayer).then((data) => {
        setPlayerStats(data);
      });
      apiClient.getPartnerStats(selectedPlayer).then((data) => {
        setPartnerStats(data);
      })
    }
  }, [selectedPlayer]);

  const winRate = (playerStats.wins / playerStats.totalMatches) * 100;

  return (
    <>
      <CssBaseline />
      <AppBar position="static">
        <Toolbar>
          {/* <IconButton
            size="large"
            edge="start"
            color="inherit"
            aria-label="menu"
            sx={{ mr: 2 }}
          >
            <Menu />
          </IconButton> */}
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Spiral Stats
          </Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="xl">
        <Paper elevation={1} variant="outlined" sx={{ padding: 1, marginTop: 2, marginBottom: 2}}>
          <Stack direction="row" useFlexGap spacing={{ xs: 1, sm: 2, md: 4 }}>
            <Stack direction="column" useFlexGap spacing={{ xs: 1, sm: 2, md: 4 }}>
              <Stack direction="column" useFlexGap spacing={{ xs: 1, sm: 2, md:4 }}>
                <PlayerDropdown onPlayerSelect={updatePlayer} />
                <Stack
                  direction="row"
                  spacing={{ xs: 1, sm: 2, md: 4}}
                  useFlexGap
                  justifyContent="center"
                  alignItems="center"
                >
                  <Paper elevation={2} sx={{height: "100%"}}>
                    <Card sx={{height: "100%"}}>
                      <CardContent sx={{height: "100%"}}>
                        <Stack>
                          <Typography component="p">Total Matches</Typography>
                          <Stack direction="column">
                            <Typography variant="h4" component="p">
                              {playerStats.totalMatches}
                            </Typography>
                          </Stack>
                        </Stack>
                      </CardContent>
                    </Card>
                  </Paper>
                  <Paper elevation={2}>
                    <Typography component="p">Win Rate</Typography>
                    <Box>
                      <Gauge
                        value={winRate}
                        startAngle={-110}
                        endAngle={110}
                        text={({ value }) => `${value?.toFixed(0)}%`}
                        cornerRadius="50%"
                        color="green"
                      ></Gauge>
                    </Box>
                  </Paper>
                  <Paper elevation={2}>
                    <Typography component="p">Average Points Margin</Typography>
                    <Box>
                      <Gauge
                        value={playerStats.averagePointsDifference}
                        startAngle={-110}
                        endAngle={110}
                        valueMin={-30}
                        valueMax={30}
                        text={({ value }) => `${value?.toFixed(2)}`}
                        cornerRadius="50%"
                        sx= {{
                          '& .MuiGauge-valueArc': {
                            fill: playerStats.averagePointsDifference < 0 ? '#d32f2f' :'#2e7d32'
                          },
                          "& .MuiGauge-referenceArc": {
                            fill: "#e0e0e0"
                          }
                        }}
                      ></Gauge>
                    </Box>
                  </Paper>
                </Stack>
                <Paper elevation={2}>
                  <SkillChart data={graphData} sx={{ height: "450px" }} />
                </Paper>
              </Stack>
            </Stack>
            <Stack direction="column"></Stack>
          </Stack>
        </Paper>
        <Stack direction = "row" spacing={2}>
          <PartnerTable rows={partnerStats.partners} />
        </Stack>
      </Container>
    </>
  );
}

export default App;
