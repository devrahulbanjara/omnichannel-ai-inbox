from fastapi import FastAPI

app = FastAPI(title="Omnichannel AI Inbox API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
