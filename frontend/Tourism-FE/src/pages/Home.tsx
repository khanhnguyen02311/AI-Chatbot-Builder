import { Container, Typography, Grid, Button, Link } from '@mui/material';
import Header from '../components/Header';
import Footer from '../components/Footer';

function HomePage() {
    return (
        <>
            <Container maxWidth="xl" sx={{ mt: 5 }}>
                <Header />
                <Grid container spacing={2} direction="row" justifyContent="center" alignItems="center" sx={{ mt: 5 }} >
                    <Grid item xs={8}>
                        <Typography variant='h1'>Hello!</Typography>
                        <Typography variant='h3'>Welcome to our chatbot app. We are here to assist you.</Typography>
                    </Grid>
                    <Grid item xs />
                </Grid>
            </Container>
        </>

    )
}

export default HomePage