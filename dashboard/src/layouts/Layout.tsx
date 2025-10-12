import {
  CssBaseline,
  Box,
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Container,
  Divider,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Drawer,
  ListItemIcon,
} from "@mui/material";
import { Menu, Person, People} from "@mui/icons-material";
import { useState } from "react";
import { Outlet, Link } from "react-router";

const navItems = [
  {
    name: "Individual",
    href: "/",
    icon: <Person />
  },
  {
    name: "Matchmaker",
    href: "/matchmaker",
    icon: <People />
  },
];

interface ListItemLinkProps {
  icon?: React.ReactElement<unknown>;
  primary: string;
  to: string;
}

function ListItemLink({ icon, primary, to }: ListItemLinkProps) {
  return (
    <ListItemButton component={Link} to={to} sx={{ textAlign: "center" }}>
      {icon ? <ListItemIcon>{icon}</ListItemIcon> : null}
      <ListItemText primary={primary} />
    </ListItemButton>
  );
}

export function Layout() {
  const [menuOpen, setMenuOpen] = useState(false);

  const handleClick = () => setMenuOpen((prevState) => !prevState);

  const drawer = (
    <Box onClick={handleClick} sx={{ textAlign: "center" }}>
      <Typography variant="h6" sx={{ my: 2 }}>
        Spiral Stats
      </Typography>
      <Divider />
      <List>
        {navItems.map((item) => (
          <ListItem key={item.name} disablePadding>
            <ListItemLink icon={item.icon} primary={item.name} to={item.href} />
          </ListItem>
        ))}
      </List>
    </Box>
  );

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
            onClick={handleClick}
          >
            <Menu />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Spiral Stats
          </Typography>
        </Toolbar>
      </AppBar>
      <nav>
        <Drawer
          variant="temporary"
          open={menuOpen}
          onClose={handleClick}
          ModalProps={{ keepMounted: true }}
        >
          {drawer}
        </Drawer>
      </nav>
      <Container maxWidth="xl">
        <Outlet />
      </Container>
    </>
  );
}
