import {
  Stack,
  Paper,
  Box,
  Card,
  CardContent,
  Typography,
} from "@mui/material";
import { PlayerDropdown } from "./PlayerDropdown";
import SkillChart from "./SkillChart";
import { Gauge } from "@mui/x-charts";
import type { PlayerStats, RankHistory } from "../utils/api";

export interface GaugesProps {
  selectedPlayer: number | string;
  updatePlayer: (playerId: number) => void;
  playerStats: PlayerStats;
  rankHistory: RankHistory;
}

const stackSpacing = { xs: 1, sm: 2, md: 4 };

export function Gauges({
  selectedPlayer,
  updatePlayer,
  playerStats,
  rankHistory,
}: GaugesProps) {
  const winRate = (playerStats.wins / playerStats.totalMatches) * 100;
  const graphData = rankHistory.history.map((entry) => {
    return {
      datetime: new Date(entry.datetime),
      mu: entry.mu,
      lowerBound:
        entry.mu - 3 * entry.sigma > 0 ? entry.mu - 3 * entry.sigma : 0,
      upperBound: entry.mu + 3 * entry.sigma,
    };
  });

  return (
      <Paper
        elevation={1}
        variant="outlined"
        sx={{ padding: 1, marginTop: 2, marginBottom: 2 }}
      >
        <Stack direction="row" useFlexGap spacing={stackSpacing}>
          <Stack direction="column" useFlexGap spacing={stackSpacing}>
            <Stack direction="column" useFlexGap spacing={stackSpacing}>
              <PlayerDropdown
                value={selectedPlayer}
                onPlayerSelect={updatePlayer}
              />
              <Stack
                direction={{ xs: "column", md: "row" }}
                spacing={stackSpacing}
                useFlexGap
                justifyContent="center"
                alignItems="center"
              >
                <Paper elevation={2} sx={{ height: "100%" }}>
                  <Card sx={{ height: "100%" }}>
                    <CardContent sx={{ height: "100%" }}>
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
                      sx={{
                        "& .MuiGauge-valueArc": {
                          fill:
                            playerStats.averagePointsDifference < 0
                              ? "#d32f2f"
                              : "#2e7d32",
                        },
                        "& .MuiGauge-referenceArc": {
                          fill: "#e0e0e0",
                        },
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
  );
}
