import { Grid, Typography } from "@mui/material";
import { useRouteError } from "react-router-dom";

export default function ErrorPage() {
  const error = useRouteError();
  console.error(error);

  return (
    <Grid
      container
      spacing={2}
      direction="column"
      alignItems="center"
      justifyContent="center"
      sx={{ minHeight: '100vh' }}>
      <Grid item>
        <Typography variant="h1">Oops!</Typography>
      </Grid>
      <Grid item>
        <Typography variant="h5">Sorry, an unexpected error has occurred.</Typography>
      </Grid>
      <Grid item>
        <Typography variant="h6">
          <i>{error.statusText || error.message}</i>
        </Typography>
      </Grid>
    </Grid>
  );
}