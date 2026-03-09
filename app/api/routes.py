from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.chains.summary_chain import generate_streaming_response

router = APIRouter()


class ExplainCommitFileChangeReqs(BaseModel):
    systemPrompt: str
    userPrompt: str


@router.post("/explain-commit-file-change")
async def explain_commit_file_change(req: ExplainCommitFileChangeReqs):
    """
    Explain commit file changes using LLM with streaming response.
    """

    async def stream_generator():
        async for chunk in generate_streaming_response(
            system_prompt=req.systemPrompt, user_prompt=req.userPrompt
        ):
            yield chunk

    return StreamingResponse(stream_generator(), media_type="text/event-stream")


@router.get("/")
def read_root():
    return {"message": "Welcome to AI Backend API"}
