import { useEffect, useState } from "react";
import { Stack, Divider } from "@mui/material";
import {
  SpiralOpenskillClient,
  type RankHistory,
  type PlayerStats,
  type PartnerStats,
  type OpponentStats,
} from "../utils/api";
import { PartnerTable } from "./PartnerTable";
import { useSearchParams } from "react-router";
import { Gauges } from "./Gauges";

const apiClient = new SpiralOpenskillClient({
  baseUrl: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000",
});

const stackSpacing = { xs: 1, sm: 2, md: 4 };

function App() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initial = Number(searchParams.get("player") ?? 0) || 0;
  const [selectedPlayer, setSelectedPlayer] = useState<number>(initial);

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
  const [partnerStats, setPartnerStats] = useState<PartnerStats>({
    playerId: selectedPlayer,
    clubId: 1,
    partners: [],
  });
  const [opponentStats, setOpponentStats] = useState<OpponentStats>({
    playerId: selectedPlayer,
    clubId: 1,
    opponents: [],
  });

  const updatePlayer = (playerId: number) => {
    setSelectedPlayer(playerId);
    setSearchParams(
      (prev) => {
        const next = new URLSearchParams(prev);
        if (playerId) next.set("player", String(playerId));
        else next.delete("player");
        return next;
      },
      { replace: true }
    );
  };

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
      });
      apiClient.getOpponentStats(selectedPlayer).then((data) => {
        setOpponentStats(data);
      });
    }
  }, [selectedPlayer]);

  return (
    <Stack spacing={2}>
      <Gauges
        selectedPlayer={selectedPlayer}
        updatePlayer={updatePlayer}
        playerStats={playerStats}
        rankHistory={rankHistory}
      />
      <Stack
        direction={{ xs: "column", md: "row" }}
        spacing={stackSpacing}
        useFlexGap
        justifyContent="space-around"
        alignItems={{ xs: "stretch", md: "flex-start" }}
        divider={<Divider orientation="vertical" flexItem />}
      >
        <PartnerTable rows={partnerStats.partners} title="Partners" />
        <PartnerTable rows={opponentStats.opponents} title="Opponents" />
      </Stack>
    </Stack>
  );
}

export default App;
