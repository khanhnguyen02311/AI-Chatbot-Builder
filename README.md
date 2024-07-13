# AI Chatbot Builder System

## Overview

The application provides the functionality to create & modify your own chatbot based on your specific prompt & dataset. After creation, you can public your Chatbots for the community to use.

You can also try out Chatbots from other users, and manage your conversations accordingly.

The Chatbots can be designed to handle a variety of tasks & scenarios. The system provides interfaces and tools to design it effectively.

## Structure

The system consists of the [backend](./backend/) and [frontend](./frontend/) module.

- Backend module consists of the main API interface, data structure, as well as the [agent system](./backend/agent_system/) to work with external LLMs & datas
- Frontend is currently being an MVP using Streamlit (in [mvp_streamlit](./frontend/mvp_streamlit/) folder)

## Development

### Prequesites

- Python 3.10 or above
- Docker & Docker Compose

***NOTE***: The current project is developed on Linux, so running it on Windows may have some dependency conflicts.

### First-time running

***For backend module:***

- Create a new environment file based on [.env.example](./backend/.env.example), in the same place as the example file location.
  - The env filename must be **.env.[anyname]** (.env.dev / env.staging / env.hello / ...)
  - Create neccessary API keys for third party services **(HuggingFace, OpenAI, OpenWeather, Google Search API)** and add to the environment file.
  - Change secret keys, DB credentials, ... if wanted.
- Create a new Python environment and install backend dependencies. You can use venv, Anaconda, Poetry, whatever you want. The easiest is to use the default venv library:

```sh
# on Linux
cd backend
python -m venv .venv_backend
source .venv_backend/bin/activate
pip install -r requirements.txt
```

- Run [docker-compose-dev.yml](./backend/docker-compose-dev.yml) file to run the backend databases, use the same environment filename in the *--env-file* options

```sh
docker compose -p assistant-builder-dev -f docker-compose-dev.yml --env-file .env.[anyname] up
```

- Run the backend module, the **stage name** must be the same as the env file suffix for it to load the correct variables.

```sh
# inside backend folder, venv_backend activated
python main.py --stage [anyname] --debug True
```

***For frontend module:***

- Create a new Python environment and install frontend dependencies. The steps are similar to the backend module.

```sh
cd frontend/mvp_streamlit
python -m venv .venv_frontend
source .venv_frontend/bin/activate
pip install -r requirements.txt
```

- Run the frontend module

```sh
# inside frontend/mvp_streamlit folder, venv_frontend activated
python -m streamlit run Home.py
```

### Update dependencies

***For backend module:*** using pip-tools
- Add new library name into [requirements.in](./backend/requirements.in)
- Run commands to update new libaries to requirement file and install it

```sh
# inside backend folder, venv_backend activated
pip-compile --strip-extras  # add '--upgrade' options if you want to update all library versions
pip install -r requirements.txt
```

***For frontend module:*** just add new libraries directly to [requirements.txt](./frontend/mvp_streamlit/requirements.txt) and run `pip install -r requirements.txt`

