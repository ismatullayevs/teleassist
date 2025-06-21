import uvicorn
from admin import UserAdmin
from api.v1.main import router as api_router_v1
from core.db import engine
from fastapi import FastAPI
from sqladmin import Admin

app = FastAPI()
admin = Admin(app, engine)

admin.add_view(UserAdmin)

app.include_router(api_router_v1, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run(
        app, host="0.0.0.0", port=80, forwarded_allow_ips="*", proxy_headers=True
    )
