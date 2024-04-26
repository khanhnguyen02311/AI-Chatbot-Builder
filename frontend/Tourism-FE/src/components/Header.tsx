import { Button, Grid, Link, Typography } from "@mui/material";

function Header() {
    return (
        <Grid container spacing={2} direction="row" justifyContent="center" alignItems="center" >
            <Grid item xs={3}>
                <Typography variant='h4' sx={{ fontWeight: 450 }}>TravelBot</Typography>
            </Grid>
            <Grid container item xs={3} direction="row" justifyContent="space-between" alignItems="center">
                <Grid item sx={{ mr: 2 }}>
                    <Link href="#introduction" variant='h6' color="inherit" underline="hover">Introduction</Link>
                </Grid>
                <Grid item sx={{ mr: 2 }}>
                    <Link href="#pricing" variant='h6' color="inherit" underline="hover">Pricing</Link>
                </Grid>
                <Grid item sx={{ mr: 2 }}>
                    <Link href="#contact" variant='h6' color="inherit" underline="hover">Contact</Link>
                </Grid>
            </Grid>
            <Grid item xs />
            <Grid item xs="auto">
                <Button href="/signin" variant="outlined" color="inherit" size='large'>Sign in</Button>
            </Grid>
            <Grid item xs="auto">
                <Button href="/signup" variant="contained" size='large'>Sign up</Button>
            </Grid>
        </Grid>
    );
};

export default Header;