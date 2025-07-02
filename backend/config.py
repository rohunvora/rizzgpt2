from pydantic_settings import BaseSettings
from typing import List, Union


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str = ""
    
    # Server
    port: int = 8000
    host: str = "0.0.0.0"
    environment: str = "development"
    
    # CORS
    allowed_origins: Union[str, List[str]] = ["http://localhost:3000", "http://localhost:8080"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        
    @property
    def cors_origins(self) -> List[str]:
        # Parse comma-separated origins if provided as string
        if isinstance(self.allowed_origins, str):
            return [origin.strip() for origin in self.allowed_origins.split(",")]
        return self.allowed_origins


settings = Settings()