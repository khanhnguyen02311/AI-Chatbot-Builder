import './chathistoryitem.scss'
import dot from '../../assets/dot-menu-more-2-svgrepo-com.svg'

interface ChatHistoryItemProps{
    id:number;
    name:string;
}

function ChatHistoryItem({id, name}: ChatHistoryItemProps){

    return (
        <li className='chat-item' >
            {name}
            <img src={dot}></img>
        </li>
    )
}

export default ChatHistoryItem;