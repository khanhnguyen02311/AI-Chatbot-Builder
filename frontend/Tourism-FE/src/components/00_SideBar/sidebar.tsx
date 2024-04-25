import './sidebar.scss';
import NewChat from '../00_NewChat/newchat';
import ChatHistoryList from '../00_ChatHistory/chathistorylist';
import UserInfo from '../00_UserInfo/userinfo';


function SideBar() {
    return (
        <div className='sidebar'>
            <NewChat/>
            <ChatHistoryList/>
            <UserInfo name='Hai Ngoc'/>
        </div>
    )

}
export default SideBar