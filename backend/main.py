import uvicorn
from configurations import arguments
from components import serve_api

if __name__ == "__main__":
    arguments.parse_args()
    api_server = serve_api()
    print(f"Starting API server with arguments: {arguments.APP_STAGE} stage, debug information set to {arguments.APP_DEBUG}")
    uvicorn.run(api_server, host="0.0.0.0", port=arguments.APP_API_PORT)
