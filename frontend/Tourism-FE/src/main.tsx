import React from 'react'
import ReactDOM from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import CssBaseline from '@mui/material/CssBaseline';
// import './index.css'
// import 'bootstrap/dist/css/bootstrap.css'
import { ThemeProvider, createTheme } from '@mui/material';
import HomePage from './pages/Home.tsx'
import ChatPage from './pages/Chat.tsx';
import ChatLayoutPage from './pages/ChatLayout.tsx';
import ErrorPage from './pages/Error.tsx'
import SignUpPage from './pages/SignUp.tsx';
import SignInPage from './pages/SignIn.tsx';

const theme = createTheme({
  palette: {
    mode: 'dark',
  },
});

const router = createBrowserRouter([
  {
    path: "/",
    element: <HomePage />,
    errorElement: <ErrorPage />,
  },
  {
    path: "/chat",
    element: <ChatPage />,
    errorElement: <ErrorPage />,
  },
  {
    path: "/chat-layout",
    element: <ChatLayoutPage />,
    errorElement: <ErrorPage />,
  },
  {
    path: "/signup",
    element: <SignUpPage />,
    errorElement: <ErrorPage />,
  },
  {
    path: "/signin",
    element: <SignInPage />,
    errorElement: <ErrorPage />,
  },
]);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <RouterProvider router={router} />
    </ThemeProvider>
  </React.StrictMode>,
)
