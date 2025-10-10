import { type GridColDef, DataGrid } from "@mui/x-data-grid";
import { type OtherPlayerStatsEntry } from "../utils/api";

export interface PartnerTableProps {
  rows: OtherPlayerStatsEntry[];
  title?: string;
}

export function PartnerTable({ rows }: PartnerTableProps) {
  const columns: GridColDef[] = [
    { field: "playerName", headerName: "Player", width: 200 },
    { field: "wins", headerName: "Wins", width: 200 },
    { field: "matches", headerName: "Matches", width: 200 },
    { field: "winRate", headerName: "Win Rate", width: 200 },
  ];

  return (
    <>
      <DataGrid
        columns={columns}
        rows={rows}
        getRowId={(row) => row.playerId}
      ></DataGrid>
    </>
  );
}
