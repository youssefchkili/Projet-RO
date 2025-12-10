from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import technicians, tasks, routes

app = FastAPI(
    title="Maintenance Routing API",
    description="API for optimizing maintenance technician routes",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(technicians.router, prefix="/api/technicians", tags=["Technicians"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(routes.router, prefix="/api/routes", tags=["Routes"])

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Server is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
