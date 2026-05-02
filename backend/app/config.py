from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    EXTRACTION_BACKEND: str = "gemini"  # "gemini" or "tesseract"
    UPLOAD_DIR: str = "uploads"
    DATABASE_URL: str = "sqlite:///./docuverify.db"
    
    class Config:
        env_file = ".env"

settings = Settings()
