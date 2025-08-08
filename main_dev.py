import dotenv

dotenv.load_dotenv()  # before any other imports


if __name__ == "__main__":
    import uvicorn

    from historical_sources_search.env import Env
    from historical_sources_search.logging.config import LOGGING_CONFIG_DICT

    env = Env.get()
    uvicorn.run(
        "historical_sources_search.api:api",
        host="localhost",
        port=env.api_port,
        reload=True,
        reload_dirs="src",
        log_config=LOGGING_CONFIG_DICT,
    )
