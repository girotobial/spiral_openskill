import { CssBaseline, AppBar, Toolbar, IconButton, Typography, Container } from "@mui/material"
import { Outlet } from "react-router"

export function Layout() {
 return (
    <>
      <CssBaseline />
      <AppBar position="static">
        <Toolbar>
          <IconButton
            size="large"
            edge="start"
            color="inherit"
            aria-label="menu"
            sx={{ mr: 2 }}
          >
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Spiral Stats
          </Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="xl">
        <Outlet />
      </Container>
    </>
)
}