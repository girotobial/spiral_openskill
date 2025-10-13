import { Stack, Box, Paper, Typography, Divider } from "@mui/material";
import { PlayerDropdown } from "./PlayerDropdown";
import { useState, useEffect } from "react";
import { type Player, API_CLIENT } from "../utils/api";
import { useSearchParams } from "react-router";
import NormalDistChart from "./NormalDistChart";
import type { Rank } from "../types";

type PlayerId = number | string;
type PlayerSetter = (player: PlayerId) => void;

interface PlayerCardProps {
  label: string;
  player: PlayerId;
  onSelect: PlayerSetter;
  mu?: number;
  sigma?: number;
}

function PlayerCard({ label, player, onSelect, mu, sigma }: PlayerCardProps) {
  const graphMu = mu ?? 25;
  const graphSigma = sigma ?? 25 / 3;

  return (
    <Paper
      elevation={2}
      sx={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-around",
        alignItems: "center",
      }}
    >
      <PlayerDropdown label={label} value={player} onPlayerSelect={onSelect} />
      <Typography component="p">{`Skill: ${graphMu.toFixed(1)}`}</Typography>
      <NormalDistChart
        ranks={[{ mu: graphMu, sigma: graphSigma }]}
        height={150}
        x={{ min: 0 }}
      />
    </Paper>
  );
}

interface TeamProps {
  label: string;
  playerOne: {
    id: PlayerId;
    setter: PlayerSetter;
    rank: Rank;
  };
  playerTwo: {
    id: PlayerId;
    setter: PlayerSetter;
    rank: Rank;
  };
}

function Team({ label, playerOne, playerTwo }: TeamProps) {

  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        flexDirection: "column",
      }}
    >
      <Typography component="h2" variant="h5" sx={{ mb: 2 }}>
        {label}
      </Typography>
      <Stack
        spacing={2}
        direction="row"
        useFlexGap
        sx={{ display: "flex", alignItems: "center", justifyContent: "center" }}
      >
        <PlayerCard
          label="Select Player 1"
          player={playerOne.id}
          onSelect={playerOne.setter}
          mu={playerOne.rank.mu}
          sigma={playerOne.rank.sigma}
        />
        <Typography component="p">&</Typography>
        <PlayerCard
          label="Select Player 2"
          player={playerTwo.id}
          onSelect={playerTwo.setter}
          mu={playerTwo.rank.mu}
          sigma={playerTwo.rank.sigma}
        />
      </Stack>
      <Divider flexItem orientation="horizontal" sx={{ mt: 2 }}></Divider>
    </Box>
  );
}

const combineRanks = (rankOne: Rank, rankTwo: Rank) => {
  return {
    mu: rankOne.mu + rankTwo.mu,
    sigma: Math.sqrt(rankOne.sigma ** 2 + rankTwo.sigma ** 2),
  }
}

function getPlayerRank(player: PlayerId, setter: (rank: Rank) => void): void {
  if (Number.isFinite(player)) {
    API_CLIENT.getRankHistory(player as number).then((data) => {
      const lastRank = data.history.at(-1);
      if (lastRank !== undefined) {
        const rank = {
          mu: lastRank.mu,
          sigma: lastRank.sigma,
        };
        setter(rank);
      }
    });
  }
}

export function Matchmaker() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialPlayerOne = Number(searchParams.get("player_one") ?? "") || "";
  const initialPlayerTwo = Number(searchParams.get("player_two") ?? "") || "";
  const initialPlayerThree =
    Number(searchParams.get("player_three") ?? "") || "";
  const initialPlayerFour = Number(searchParams.get("player_four") ?? "") || "";

  const [playerOne, setPlayerOne] = useState<number | string>(initialPlayerOne);
  const [playerTwo, setPlayerTwo] = useState<number | string>(initialPlayerTwo);
  const [playerThree, setPlayerThree] = useState<number | string>(
    initialPlayerThree
  );
  const [playerFour, setPlayerFour] = useState<number | string>(
    initialPlayerFour
  );

  const [playerOneRank, setPlayerOneRank] = useState({
    mu: 25,
    sigma: 25 / 3,
  });
  const [playerTwoRank, setPlayerTwoRank] = useState({
    mu: 25,
    sigma: 25 / 3,
  });
  const [playerThreeRank, setPlayerThreeRank] = useState({
    mu: 25,
    sigma: 25 / 3,
  });
  const [playerFourRank, setPlayerFourRank] = useState({
    mu: 25,
    sigma: 25 / 3,
  });

  const teamOneRank = combineRanks(playerOneRank, playerTwoRank);
  const teamTwoRank = combineRanks(playerThreeRank, playerFourRank);

  const [players, setPlayers] = useState<Array<Player>>([]);

  useEffect(() => {
    API_CLIENT.getPeople().then((data) => setPlayers(data));
    return () => {};
  }, []);

  useEffect(() => {
    getPlayerRank(playerOne, setPlayerOneRank);
    return () => {};
  }, [playerOne]);

  useEffect(() => {
    getPlayerRank(playerTwo, setPlayerTwoRank);
    return () => {};
  }, [playerTwo]);

  useEffect(() => {
    getPlayerRank(playerThree, setPlayerThreeRank);
    return () => {};
  }, [playerThree]);

  useEffect(() => {
    getPlayerRank(playerFour, setPlayerFourRank);
    return () => {};
  }, [playerFour]);

  return (
    <>
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-around",
          mt: 2,
          flexDirection: "column"
        }}
      >
        <Stack
          direction="row"
          spacing={2}
          useFlexGap
          sx={{ display: "flex", alignItems: "center" }}
        >
          <Team
            label="Team 1"
            playerOne={{
              id: playerOne,
              setter: setPlayerOne,
              rank: playerOneRank,
            }}
            playerTwo={{
              id: playerTwo,
              setter: setPlayerTwo,
              rank: playerTwoRank,
            }}
          />
          <Divider orientation="vertical" flexItem>
            VS
          </Divider>
          <Team
            label="Team 2"
            playerOne={{
              id: playerThree,
              setter: setPlayerThree,
              rank: playerThreeRank,
            }}
            playerTwo={{
              id: playerFour,
              setter: setPlayerFour,
              rank: playerFourRank,
            }}
          />
        </Stack>
        <NormalDistChart ranks={[teamOneRank, teamTwoRank]} height={300} x={{ min: 0 }} />
      </Box>
    </>
  );
}
