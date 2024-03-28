import './userinfo.scss';
import {Avatar} from 'react-chat-elements';
import dot from '../../assets/dot-menu-more-2-svgrepo-com.svg'
interface UserInfoProps{
    name:string
}

function UserInfo({name}:UserInfoProps){
    return(
        <div className='user-info'>
            <div className='user'>
                <Avatar
                    src={dot}
                    alt="avatar"
                    size="default"
                    type="rounded"
                />
                
            </div>
            {name}
        </div>
    )
}


export default UserInfo;