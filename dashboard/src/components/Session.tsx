import { TypeSpecimen } from "@mui/icons-material"
import { Typography, Paper, Stack, Grid } from "@mui/material"
import { PlayerDropdown } from "./PlayerDropdown"

function Court({ num }: { num: number}) {
    return (
        <>
        <Paper sx={{m: 2}}>
            <Typography>{`Court ${num}`}</Typography>
            <Stack direction="row" useFlexGap alignItems="center" justifyContent="center">
                <Stack direction="column" useFlexGap>
                <PlayerDropdown label="Player 1" value={""} onPlayerSelect={() => {}} />
                <PlayerDropdown label="Player 2" value={""} onPlayerSelect={() => {}} />
                </Stack>
                <Stack direction="column" useFlexGap>
                <PlayerDropdown label="Player 3" value={""} onPlayerSelect={() => {}} />
                <PlayerDropdown label="Player 4" value={""} onPlayerSelect={() => {}} />
                </Stack>
            </Stack>
        </Paper>
        </>
    )
}

export function Session() {
    return (
        <>
        <Court num={1} />
        <Court num={2} />
        <Court num={3} />
        <Court num={4} />
        </>
    )
}