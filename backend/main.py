from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from agent.lang_agent import run_agent_with_langgraph as run_agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        user_input = data.get("message", "")
        response = run_agent(user_input)
        return {"response": response}
    except Exception as e:
        import traceback
        print("❌ Backend exception:")
        traceback.print_exc()  # 👈 shows full error in terminal
        return {"response": f"❌ Internal error: {str(e)}"}
