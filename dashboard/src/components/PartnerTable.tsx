import { type GridColDef, DataGrid } from "@mui/x-data-grid";
import { type OtherPlayerStatsEntry } from "../utils/api";
import { Divider, Typography, Box } from "@mui/material";

export interface PartnerTableProps {
  rows: OtherPlayerStatsEntry[];
  title?: string;
}

export function PartnerTable({ rows, title }: PartnerTableProps) {
  const columns: GridColDef[] = [
    { field: "playerName", headerName: "Player", width: 200 },
    {
      field: "wins",
      headerName: "Wins",
      description: "Total matches won with this player",
    },
    {
      field: "matches",
      headerName: "Matches",
      description: "Total matches played with this player",
    },
    {
      field: "winRate",
      headerName: "Win Rate",
      description: "% of matches played that have been won",
      valueFormatter: (value) => `${(value * 100).toFixed(1)}%`
    },
  ];

  return (
    <Box>
      <Typography>{title}</Typography>
      <Divider
        orientation="horizontal"
        flexItem
        sx={{ marginTop: 1, marginBottom: 2 }}
      />
      <DataGrid
        columns={columns}
        rows={rows}
        getRowId={(row) => row.playerId}
      ></DataGrid>
    </Box>
  );
}
