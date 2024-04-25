import './newchat.scss';
import chatlogo from '../../assets/openai-svgrepo-com.svg';
import newchatlogo from '../../assets/chat-new-svgrepo-com.svg'

function NewChat(){
    return(
        <div className='newchat'>
            <button>
                <img src={chatlogo}/>
                <text>New chat</text>
                <img src={newchatlogo}/>
            </button>
        </div>
    )
}

export default NewChat;