import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get configuration from environment variables
PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")
ENV = os.getenv("ENV", "development")

if __name__ == "__main__":
    print(f"Starting server on {HOST}:{PORT} in {ENV} mode")
    uvicorn.run("app.main:app", 
                host=HOST, 
                port=PORT, 
                reload=(ENV == "development"))
