import {
    Box,
    List,
    ListItemButton,
    Typography,
    Divider,
    Card,
    CardActionArea,
    MenuItem,
    FormControl,
    InputLabel,
    Select,
    SelectChangeEvent,
    Container,
    TextField, IconButton
} from "@mui/material";
import { AddCircle, Send } from "@mui/icons-material";
import React from "react";
import MessageBox from "../components/MessageBox";

function TestHistoryItem() {
    return (
        <ListItemButton sx={{ border: 1, width: '100%' }}>
            <Typography variant="body1">A conversation</Typography>
        </ListItemButton>
    )
}

function ChatLayoutPage() {
    const [bot, setBot] = React.useState('');

    const handleChange = (event: SelectChangeEvent) => {
        console.log(event.target.value as string)
        setBot(event.target.value as string);
    };

    return (
        <Box sx={{ height: "100vh", display: 'flex', flexDirection: 'row', alignItems: 'stretch' }}>
            <Box sx={{ bgcolor: "#212329", width: '300px', py: 4, px: 2, border: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <Card variant="outlined" sx={{ bgcolor: "#212329", width: '100%', height: '50px' }}>
                    <CardActionArea sx={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'stretch' }}>
                        <Typography variant="body1" sx={{ ml: 2 }}>New conversation</Typography>
                        <AddCircle sx={{ ml: 'auto', mr: 2 }} />
                    </CardActionArea>
                </Card>

                <Divider sx={{ my: 4, width: '100%' }} />
                <List sx={{ width: '100%' }}>
                    <TestHistoryItem />
                    <TestHistoryItem />
                    <TestHistoryItem />
                    <TestHistoryItem />
                </List>
                <Box sx={{ flexGrow: 1 }} />
                <Card variant="outlined" sx={{ bgcolor: "#212329", width: '100%', height: '50px' }}>
                    <CardActionArea sx={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'stretch' }}>
                        <Typography variant="body1" sx={{ ml: 2 }}>My Account</Typography>
                        <AddCircle sx={{ ml: 'auto', mr: 2 }} />
                    </CardActionArea>
                </Card>
            </Box>
            <Box sx={{ flexGrow: 1, border: 1, display: 'flex', flexDirection: 'column', alignItems: 'stretch' }}>
                <Box sx={{ border: 1, width: '100%', height: '100px', flex: 'none', display: 'flex', alignItems: 'center', justifyContent: 'stretch' }}>
                    <Box sx={{ pl: 4, border: 1, flexGrow: 1, height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'start', justifyContent: 'center' }}>
                        <Typography variant="body1">Conversation Name ABC</Typography>
                        <Typography variant="body2">Wednesday, 16th, 2024</Typography>
                    </Box>
                    <FormControl sx={{ mx: 4, minWidth: "150px" }} size="medium">
                        <InputLabel id="simple-select-label">Choose bot</InputLabel>
                        <Select
                            labelId="=simple-select-label"
                            id="simple-select"
                            value={bot}
                            label="Choose bot"
                            onChange={handleChange}>
                            <MenuItem value={"QuangBinhTravisstant"}>QuangBinhTravisstant</MenuItem>
                            <MenuItem value={"DaLatBot"}>DaLatBot</MenuItem>
                            <Divider />
                            <MenuItem value={""}>Discover more bots ...</MenuItem>
                        </Select>
                    </FormControl>
                </Box>
                <Box sx={{ flexGrow: 1, alignSelf: 'center', px: '15%', py: 4, gap: 2, width: '100%', display: 'flex', flexDirection: 'column', overflowY: 'scroll' }}>
                    <MessageBox content="Hello, how can I help you" sender="QuangBinhTravisstant" align="left" />
                    <MessageBox content="Can you send me some recommended things to do in Son Doong ?" sender="Me" align="right" />
                    <MessageBox content="No, can't help you" sender="QuangBinhTravisstant" align="left" />
                    <MessageBox content="Oh, okay." sender="Me" align="right" />
                    <MessageBox content="Hello, how can I help you" sender="QuangBinhTravisstant" align="left" />
                    <MessageBox content="Can you send me some recommended things to do in Son Doong ?" sender="Me" align="right" />
                    <MessageBox content="No, can't help you" sender="QuangBinhTravisstant" align="left" />
                    <MessageBox content="Oh, okay." sender="Me" align="right" />
                    <MessageBox content="Hello, how can I help you" sender="QuangBinhTravisstant" align="left" />
                    <MessageBox content="Can you send me some recommended things to do in Son Doong ?" sender="Me" align="right" />
                    <MessageBox content="No, can't help you" sender="QuangBinhTravisstant" align="left" />
                    <MessageBox content="Oh, okay." sender="Me" align="right" />
                    <MessageBox content="Hello, how can I help you" sender="QuangBinhTravisstant" align="left" />
                    <MessageBox content="Can you send me some recommended things to do in Son Doong ?" sender="Me" align="right" />
                    <MessageBox content="No, can't help you" sender="QuangBinhTravisstant" align="left" />
                    <MessageBox content="Oh, okay." sender="Me" align="right" />
                    <MessageBox content="Hello, how can I help you" sender="QuangBinhTravisstant" align="left" />
                    <MessageBox content="Can you send me some recommended things to do in Son Doong ?" sender="Me" align="right" />
                    <MessageBox content="No, can't help you" sender="QuangBinhTravisstant" align="left" />
                    <MessageBox content="Oh, okay." sender="Me" align="right" />
                    <MessageBox content="Hello, how can I help you" sender="QuangBinhTravisstant" align="left" />
                    <MessageBox content="Can you send me some recommended things to do in Son Doong ?" sender="Me" align="right" />
                    <MessageBox content="No, can't help you" sender="QuangBinhTravisstant" align="left" />
                    <MessageBox content="Oh, okay." sender="Me" align="right" />
                </Box>
                <Box sx={{ border: 1, p: 4, width: '100%', maxHeight: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <TextField maxRows={8}
                        id="input-area"
                        label="Ask me anything"
                        placeholder="Type your message here"
                        multiline
                        sx={{ width: '75%' }}
                    />
                    <IconButton aria-label="" size="large" sx={{ ml: 2 }}>
                        <Send />
                    </IconButton>
                </Box >
            </Box >
        </Box >
    )
}

export default ChatLayoutPage