import { PlayerDropdown } from "./PlayerDropdown";
import { useEffect, useState } from "react";
import {
  CssBaseline,
  Box,
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Paper,
  Container,
} from "@mui/material";
import { Menu } from "@mui/icons-material";
import { SpiralOpenskillClient, type RankHistory } from "../utils/api";
import { LineChart } from "@mui/x-charts";
import { Slider } from "@mui/material";

const apiClient = new SpiralOpenskillClient({
  baseUrl: "http://localhost:8000",
});

const FIRST_DATE = new Date("2025-01-01");
const LAST_DATE = new Date("2025-12-31");

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
    return { datetime: new Date(entry.datetime), mu: entry.mu };
  });

  const firstDate = graphData.length > 0 ? graphData[0].datetime : FIRST_DATE;
  const lastDate =
    graphData.length > 0 ? graphData[graphData.length - 1].datetime : LAST_DATE;

  const [sliderValue, setSliderValue] = useState<number[]>([
    firstDate.getTime(),
    lastDate.getTime(),
  ]);

  useEffect(() => {
    if (selectedPlayer !== 0) {
      apiClient.getRankHistory(selectedPlayer).then((data) => {
        setRankHistory(data);
      });
    }
  }, [selectedPlayer]);

  const handleSliderChange = (
    event: Event,
    newValue: number | number[],
    activeThumb: number
  ) => {
    if (!Array.isArray(newValue)) {
      return;
    }
    if (newValue[1] - newValue[0] < 86400000) {
      if (activeThumb === 0) {
        const clamped = Math.min(newValue[0], LAST_DATE.getTime() - 86400000);
        setSliderValue([clamped, clamped + 86400000]);
      } else {
        const clamped = Math.max(newValue[1], FIRST_DATE.getTime() + 86400000);
        setSliderValue([clamped - 86400000, clamped]);
      }
    } else {
      setSliderValue(newValue as number[]);
    }
  };

  return (
    <>
      <CssBaseline />
      <Box>
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
      </Box>
      <Container maxWidth="lg">
        <Paper elevation={1} variant="outlined">
          <PlayerDropdown onPlayerSelect={updatePlayer} />
        <Box
          sx={{
            width: '100%',
            height: 400,
          }}
        >
          <LineChart
            series={[{ dataKey: "mu" }, { dataKey: "datetime" }]}
            dataset={graphData}
            xAxis={[
              {
                dataKey: "datetime",
                scaleType: "time",
                label: "Date/Time",
                min: new Date(sliderValue[0]),
                max: new Date(sliderValue[1]),
              },
            ]}
            yAxis={[{ dataKey: "mu", min: 0, label: "Skill" }]}
            grid={{ vertical: true, horizontal: true }}
          />
          <Slider
            value={sliderValue}
            valueLabelDisplay="off"
            min={FIRST_DATE.getTime()}
            max={LAST_DATE.getTime()}
            onChange={handleSliderChange}
          />
        </Box>
        </Paper>
      </Container>
    </>
  );
}

export default App;
