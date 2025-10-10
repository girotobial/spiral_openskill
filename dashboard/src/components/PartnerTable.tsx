import { type GridColDef, DataGrid } from "@mui/x-data-grid";
import { type OtherPlayerStatsEntry } from "../utils/api";
import { Paper, Typography, Box } from "@mui/material";

export interface PartnerTableProps {
  rows: OtherPlayerStatsEntry[];
  title?: string;
}

export function PartnerTable({ rows, title }: PartnerTableProps) {
  const columns: GridColDef[] = [
    { field: "playerName", headerName: "Player", width: 200 },
    { field: "wins", headerName: "Wins"},
    { field: "matches", headerName: "Matches"},
    { field: "winRate", headerName: "Win Rate"},
  ];

  return (
    <Box>
      <Typography>{title}</Typography>
      <DataGrid
        columns={columns}
        rows={rows}
        getRowId={(row) => row.playerId}
      ></DataGrid>
    </Box>
  );
}
