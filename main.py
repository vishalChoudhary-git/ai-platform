import uvicorn

from app.main import create_app
from app.core.config import app_settings

app = create_app()

# if __name__ == "__main__":
#     uvicorn.run(
#         "main:app",
#         host=app_settings.host,
#         port=app_settings.port,
#         reload=False,
#     )