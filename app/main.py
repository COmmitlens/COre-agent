from fastapi import FastAPI
from dotenv import load_dotenv
from app.api.routes import router
import sys

import uvicorn

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="AI Backend")

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}


def _parse_port(default_port: int = 9000) -> int:
    args = sys.argv[1:]

    if not args:
        return default_port

    if len(args) >= 2 and args[0].lower() == "port":
        return int(args[1])

    if len(args) >= 2 and args[0] in {"--port", "-p"}:
        return int(args[1])

    if len(args) == 1:
        return int(args[0])

    raise ValueError("Invalid arguments. Use: python main.py port 9000")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=_parse_port())
