import uvicorn
from configurations import envs, arguments
from components import serve_api

api_server = serve_api(debug=arguments.debug, stage=arguments.stage)

if __name__ == "__main__":
    uvicorn.run(api_server, host="0.0.0.0", port=envs.App.API_PORT)
