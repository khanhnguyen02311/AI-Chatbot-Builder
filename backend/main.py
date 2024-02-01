import uvicorn
from arguments import args
from components import serve_api
from configurations import App

api_server = serve_api(debug=args.debug, stage=args.stage)

if __name__ == "__main__":
    uvicorn.run(api_server, host="0.0.0.0", port=App.API_PORT)
