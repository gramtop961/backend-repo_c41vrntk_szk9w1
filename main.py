import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from database import db, create_document, get_documents
from schemas import Member, Trainer, GymClass, ClassBooking, TrainerBooking, BodyMetric, Recommendation, ExerciseItem

app = FastAPI(title="Fit Castle API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Fit Castle Backend Running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Connected & Working"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            try:
                response["collections"] = db.list_collection_names()[:10]
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# ------------- Public Content Endpoints (Company Profile) -------------
class ContactMessage(BaseModel):
    name: str
    email: str
    message: str

@app.post("/api/contact")
def submit_contact(msg: ContactMessage):
    try:
        _id = create_document("contactmessage", msg)
        return {"ok": True, "id": _id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trainers")
def list_trainers():
    try:
        items = get_documents("trainer")
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/classes")
def list_classes():
    try:
        items = get_documents("gymclass")
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------- Membership -------------
@app.post("/api/members")
def create_member(member: Member):
    try:
        _id = create_document("member", member)
        return {"ok": True, "id": _id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/members")
def list_members():
    try:
        items = get_documents("member")
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------- Bookings -------------
@app.post("/api/bookings/class")
def book_class(payload: ClassBooking):
    try:
        _id = create_document("classbooking", payload)
        return {"ok": True, "id": _id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bookings/trainer")
def book_trainer(payload: TrainerBooking):
    try:
        _id = create_document("trainerbooking", payload)
        return {"ok": True, "id": _id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------- Body Recomposition -------------
@app.post("/api/recomposition/metrics")
def submit_metrics(metrics: BodyMetric):
    try:
        _id = create_document("bodymetric", metrics)
        return {"ok": True, "id": _id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recomposition/recommend")
def recommend_plan(metrics: BodyMetric):
    """Generate a simple rule-based weekly plan recommendation based on inputs."""
    try:
        # Basic logic
        goal = metrics.goal
        activity = metrics.activity_level
        gender = metrics.gender
        age = metrics.age
        height = metrics.height_cm
        weight = metrics.weight_kg
        bf = metrics.body_fat_pct

        plan: List[ExerciseItem] = []

        def add(name, sets, reps, freq):
            plan.append(ExerciseItem(name=name, sets=sets, reps=reps, frequency_per_week=freq))

        if goal == "fat_loss":
            add("Treadmill Intervals", 6, "1 min fast / 2 min easy", 3)
            add("Full-Body Circuit", 4, "12-15 reps", 2)
            add("Core Stability", 3, "12-15 reps", 2)
        elif goal == "muscle_gain":
            add("Barbell Squat", 5, "5-8 reps", 2)
            add("Bench Press", 5, "5-8 reps", 2)
            add("Deadlift", 3, "3-5 reps", 1)
            add("Accessory (Rows, Press, Pull-ups)", 4, "8-12 reps", 2)
        else:  # recomp
            add("Upper/Lower Split Strength", 4, "6-10 reps", 3)
            add("Zone 2 Cardio", 1, "30-40 mins", 2)
            add("Mobility & Core", 3, "10-15 reps", 2)

        # Adjust frequency by activity level
        if activity in ["sedentary", "light"]:
            for i in range(len(plan)):
                plan[i].frequency_per_week = max(1, plan[i].frequency_per_week - 1)
        elif activity in ["athlete"]:
            for i in range(len(plan)):
                plan[i].frequency_per_week = plan[i].frequency_per_week + 1

        summary = "Personalized plan generated based on your goal and activity level."
        if bf and goal == "fat_loss" and bf > 25:
            summary += " Focus on sustainable deficit, prioritize sleep and steps."

        rec = Recommendation(
            body_metric_id=None,
            summary=summary,
            weekly_plan=plan
        )

        # Optionally store metrics & recommendation
        try:
            mid = create_document("bodymetric", metrics)
            create_document("recommendation", {"body_metric_id": mid, "summary": rec.summary, "weekly_plan": [i.model_dump() for i in rec.weekly_plan]})
        except Exception:
            pass

        return rec
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
