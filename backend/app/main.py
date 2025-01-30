from fastapi import FastAPI
from app.routers import users, complaints, auth
from app.enums import Role, Status

app = FastAPI()

app.include_router(users.router)
app.include_router(complaints.router)
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

# Обработчик ошибок
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal Server Error",
            "detail": str(exc),
            "traceback": traceback.format_exc()
        }
    )