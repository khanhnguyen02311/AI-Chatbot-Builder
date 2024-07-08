import requests
from fastapi import APIRouter, Request, Response
from configurations.envs import Chat
from components.data import POSTGRES_SESSION_FACTORY
from components.services.account_facebook import AccountFacebookService

router = APIRouter()


@router.get("")
async def init_messenger(request: Request):
    # FB sends the verify token as hub.verify_token
    fb_token = request.query_params.get("hub.verify_token")
    # we verify if the token sent matches our verify token
    if fb_token == Chat.FACEBOOK_VERIFY_TOKEN:
        # respond with hub.challenge parameter from the request.
        return Response(content=request.query_params["hub.challenge"])
    return "Failed to verify token"


@router.post("")
async def get_messenger(request: Request):
    data = await request.json()
    if data.get("object") == "page":
        # handleMessage(sender_id, received_message)
        # Further processing of the webhook data can be done here

        message_data = data["entry"][0]["messaging"][0]

        print("NEW MESSAGE: ")
        print(message_data)

        facebook_id = message_data["sender"]["id"]
        page_id = message_data["recipient"]["id"]
        message_content = message_data["message"]["text"]

        with POSTGRES_SESSION_FACTORY() as session:
            facebook_service = AccountFacebookService(session, facebook_id)
            new_response_message = facebook_service.append_new_message(message_content)
            session.commit()

            print("NEW MESSAGE RESPONSE:")
            print(new_response_message)

            resp = requests.post(
                f"https://graph.facebook.com/v20.0/{page_id}/message",
                params={
                    "recipient": {"id": facebook_id},
                    "message": {"text": new_response_message.content},
                    "messaging_type": "RESPONSE",
                    "access_token": Chat.FACEBOOK_PAGE_ACCESS_TOKEN,
                },
            )

            print("FB RESPONSE:")
            print(resp.status_code, resp.content)

        # send message to Facebook

    return '{"status": "ok"}'


# To respond to the message a customer sent to your Page, send a POST request to /PAGE-ID/messages endpoint with the recipient parameter set to the customer's PSID, messaging_type parameter set to RESPONSE, and the message parameter set to your response. Note that this must be sent within 24 hours of your Page receiving the customer's message.


# curl -i -X POST "https://graph.facebook.com/LATEST-API-VERSION/PAGE-ID/messages
#     ?recipient={id:PSID}
#     &message={text:'You did it!'}
#     &messaging_type=RESPONSE
#     &access_token=PAGE-ACCESS-TOKEN"

# Received message structure:
# {
#     "object": "page",
#     "entry": [
#         {
#             "time": 1720368846816,
#             "id": "215134631680055",
#             "messaging": [
#                 {
#                     "sender": {"id": "7396619290372809"},
#                     "recipient": {"id": "215134631680055"},
#                     "timestamp": 1720368845189,
#                     "message": {
#                         "mid": "m_NrBwxfywhAU_oi8CQa8nHCtS-YgxehLk1mhv60AK7DLDZiychjnNHqZGACisUI4GPHGvNbjq-4Q8LWVI6MGiRA",
#                         "text": "xin chào",
#                     },
#                 }
#             ],
#             "hop_context": {"app_id": 2653153441517780, "metadata": ""},
#         }
#     ],
# }
