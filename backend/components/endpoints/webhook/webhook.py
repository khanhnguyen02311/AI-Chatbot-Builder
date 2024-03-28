from fastapi import APIRouter,Request,Response
from configurations.envs import Chat

router = APIRouter(prefix="/webhook")


@router.get("")
async def init_messenger(request: Request):
	# FB sends the verify token as hub.verify_token
    fb_token = request.query_params.get("hub.verify_token")

    # we verify if the token sent matches our verify token
    if fb_token == Chat.FACEBOOK_VERIFY_TOKEN:
    	# respond with hub.challenge parameter from the request.
        return Response(content=request.query_params["hub.challenge"])
    return 'Failed to verify token'


@router.post("")
async def get_messenger(request: Request):
    data = await request.json()
    if data.get("object") == "page":
        print(data)
        sender_id = data['entry'][0]['messaging'][0]['sender']['id']
        received_message = data['entry'][0]['messaging'][0]['message']['text']
        # handleMessage(sender_id, received_message)
        # Further processing of the webhook data can be done here
    return '{"status": "ok"}'