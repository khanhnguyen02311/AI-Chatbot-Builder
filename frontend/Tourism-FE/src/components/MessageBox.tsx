import { Box, Typography } from '@mui/material';

const MessageBox = ({ content, sender, align }: { content: string, sender: string, align: 'left' | 'right' }) => {
    return (
        <Box sx={{
            display: 'inline-block',
            my: '5',
            ml: align === 'left' ? '0' : '10',
            mr: align === 'right' ? '10' : '0',
            p: '10',
            border: '1',
            borderRadius: '10'
        }}>
            <Typography variant="body2" sx={{ textAlign: align }}>{sender}</Typography>
            <Typography variant="body1" sx={{ textAlign: align }}>{content}</Typography>
        </Box>
    )
}

export default MessageBox;