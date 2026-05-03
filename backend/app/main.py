from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import upload, verify, results
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="DocuVerify API", version="1.0.0")

# Configure allowed origins from environment. Use comma-separated list or "*" for all.
allowed_origins = os.getenv("FASTAPI_ALLOWED_ORIGINS", "http://localhost:5173", "*")
if allowed_origins.strip() == "*":
    origins = ["*"]
else:
    origins = [o.strip() for o in allowed_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(verify.router)
app.include_router(results.router)

@app.get("/")
def read_root():
    return {"message": "DocuVerify API is running"}

@app.get("/categories")
def get_categories():
    return {
        "IDENTIFICATION": ["PVC_AADHAAR", "PAN", "STUDENT_ID", "BIRTH_CERTIFICATE", "RATION_CARD", "LAST_PASSPORT", "EPIC", "DRIVING_LICENCE", "BANK_PASSBOOK", "SC_ST_OBC_CERT", "ARMS_LICENCE", "PENSION_DOC", "SERVICE_ID"],
        "ADDRESS": ["ADDRESS_AADHAAR", "RENT_AGREEMENT", "PARENT_PASSPORT", "ELECTRICITY_BILL", "TELEPHONE_BILL", "WATER_BILL", "GAS_CONNECTION_PROOF", "INCOME_TAX_ORDER", "EMPLOYER_LETTER", "SPOUSE_PASSPORT", "PHOTO_BANK_PASSBOOK"],
        "NON_ECR": ["DEGREE_CERTIFICATE", "TENTH_MARKSHEET", "TWELFTH_MARKSHEET", "GRADUATION_CERTIFICATE"]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", os.getenv("FASTAPI_PORT", 8000)))
    uvicorn.run(app, host="0.0.0.0", port=port)