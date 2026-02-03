# Default settings template
import os


from dotenv import load_dotenv
load_dotenv()

class Settings:
	database_url = os.getenv("DATABASE_URL")
	debug = os.getenv("DEBUG", "false").lower() == "true"

	# Application settings
	app_name = os.getenv("APP_NAME", "Red Team AI")
	version = os.getenv("APP_VERSION", "0.1.0")
	cors_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",")]
	api_prefix = os.getenv("API_PREFIX", "/api/v1")

settings = Settings()
