from components.data.models import postgres as PostgresModels
from components.data.schemas import chat_message as ChatMessageSchemas
from components.repositories.bot import BotRepository
from components.repositories.chat_account import ChatAccountRepository
from components.repositories.chat_session import ChatSessionRepository
from components.services.chat import ChatService
from agent_system.agents.account import AccountAgent


class AccountFacebookService:
    def __init__(self, session, facebook_id: int):
        self.current_account = None
        self.current_chat_session = None

        self.session = session
        self.bot_repository = BotRepository(session)
        self.chat_account_repository = ChatAccountRepository(session)
        self.chat_session_repository = ChatSessionRepository(session)
        self.chat_service = ChatService(session)

        existed_account = self.chat_account_repository.get_by_account_type(facebook_id, "facebook")
        if existed_account is not None:
            existed_session = self.chat_session_repository.get_all_by_chat_account(existed_account.id)[0]
            self.current_account = existed_account
            self.current_chat_session = existed_session

        new_account = PostgresModels.ChatAccount(account_type="facebook", id_external_account=facebook_id)
        self.chat_account_repository.create(new_account)
        admin_bot_id = self.bot_repository.get_all_by_account(1)[0].id
        facebook_session = PostgresModels.ChatSession(
            name="Facebook Session", id_chat_account=new_account.id, id_bot=admin_bot_id
        )
        self.chat_session_repository.create(facebook_session)
        self.current_account = new_account
        self.current_chat_session = facebook_session

    def append_new_message(self, content: str):
        new_message_data = ChatMessageSchemas.ChatMessagePOST(
            content=content, id_chat_session=self.current_chat_session.id, type="user-text"
        )

        bot = self.bot_repository.get(self.current_chat_session.id_bot)
        session_message_history = self.chat_service.get_session_messages(
            self.current_chat_session.id, self.current_account, return_type="langchain", with_validation=False
        )
        agent_response = AccountAgent(bot_data=bot, message_history=session_message_history).generate_response(
            new_message_data.content
        )
        _ = self.chat_service.create_new_chat_message(new_message_data, self.current_account, with_validation=False)
        new_response_message = self.chat_service.create_new_chat_message(
            ChatMessageSchemas.ChatMessagePOST(
                content=agent_response, type="bot", id_chat_session=self.current_chat_session.id
            ),
            self.current_account,
            with_validation=False,
        )
        return new_response_message
        # send API response
