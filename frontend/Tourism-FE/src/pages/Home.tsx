import { Container, Typography, Grid, Button } from '@mui/material';
import { Link } from 'react-router-dom'
import HomeAppBar from '../components/AppBar';
import Footer from '../components/Footer';

function HomePage() {
    return (
        <Container maxWidth="xl" sx={{ mt: 5 }}>
            <Grid container spacing={2} direction="row" justifyContent="center" alignItems="center" >
                <Grid item xs={3} >
                    <Typography variant='h4' sx={{ fontWeight: 450 }}>TravelBot</Typography>
                </Grid>
                <Grid container item xs={3} direction="row" justifyContent="space-between" alignItems="center">
                    <Grid item>
                        <Typography variant='h6'>Introduction</Typography>
                    </Grid>
                    <Grid item>
                        <Typography variant='h6'>Pricing</Typography>
                    </Grid>
                    <Grid item>
                        <Typography variant='h6'>Contact</Typography>
                    </Grid>
                </Grid>
                <Grid item xs />
                <Grid item xs="auto">
                    <Button component={Link} to="/login" variant="outlined" color="inherit" size='large'>Login</Button>
                </Grid>
                <Grid item xs="auto">
                    <Button component={Link} to="/signup" variant="contained" size='large'>Sign up</Button>
                </Grid>
            </Grid>

            <Grid container spacing={2} direction="row" justifyContent="center" alignItems="center" sx={{ mt: 5 }} >
                <Grid item xs={8}>
                    <Typography variant='h1'>Hello!</Typography>
                    <Typography variant='h3'>Welcome to our chatbot app. We are here to assist you.</Typography>
                </Grid>
                <Grid item xs />
            </Grid>
        </Container >
    )
}

export default HomePage