import dotenv

dotenv.load_dotenv()  # before any other imports


if __name__ == "__main__":
    import historical_sources_search.main  # initializes logging

    historical_sources_search.main.main()
