import { useRef } from 'react';
import ChatHistoryItem from '../ChatHistoryItem/chathistoryitem';
import './chathistorylist.scss'

function ChatHistoryList(){
    const chats = [
        { id: 1, name: 'Chat 1' },
        { id: 2, name: 'Chat 2' },
        { id: 3, name: 'Chat 3' },
        { id: 2, name: 'Chat 2' },
        { id: 3, name: 'Chat 3' },
        { id: 2, name: 'Chat 2' },
        { id: 3, name: 'Chat 3' },
        { id: 2, name: 'Chat 2' },
        { id: 3, name: 'Chat 3' },
        { id: 2, name: 'Chat 2' },
        { id: 3, name: 'Chat 3' }
      ];
    return (
        <ul className='chat-list'>
            {chats.map(chat => 
                <ChatHistoryItem key={chat.id} id={chat.id} name={chat.name} ></ChatHistoryItem>
            )}
        </ul>
    )
}

export default ChatHistoryList;