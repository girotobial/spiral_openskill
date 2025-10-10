import { type GridColDef, DataGrid } from "@mui/x-data-grid";
import { type OtherPlayerStatsEntry } from "../utils/api";
import { Divider, Typography, Box } from "@mui/material";

export interface PartnerTableProps {
  rows: OtherPlayerStatsEntry[];
  title?: string;
}

export function PartnerTable({ rows, title }: PartnerTableProps) {
  const columns: GridColDef[] = [
    { field: "playerName", headerName: "Player", width: 200, type: "string" },
    {
      field: "wins",
      headerName: "Wins",
      description: "Total matches selected player has won",
      type: "number",
    },
    {
      field: "matches",
      headerName: "Matches",
      description: "Total matches played",
      type: "number",
    },
    {
      field: "winRate",
      headerName: "Win Rate",
      description: "% of matches played that selected player has won",
      type: "number",
      valueFormatter: (value) => `${(value * 100).toFixed(1)}%`,
    },
  ];

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        maxHeight: "800px",
        width: { xs: "100%", md: "50%" },
        minWidth: 0,
      }}
    >
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
