import './sidebar.scss';
import NewChat from '../NewChat/newchat';
import ChatHistoryList from '../ChatHistory/chathistorylist';
import UserInfo from '../UserInfo/userinfo';


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