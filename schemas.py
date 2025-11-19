"""
Database Schemas for Fit Castle Gym

Each Pydantic model below maps to a MongoDB collection. The collection name is the
lowercase of the class name (e.g., Member -> "member").
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime

# Core entities
class Member(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    phone: str = Field(..., description="WhatsApp/phone number")
    plan: Literal["basic", "pro", "elite"] = Field("basic", description="Membership plan")
    start_date: Optional[datetime] = Field(None, description="Membership start date")
    active: bool = Field(True, description="Is membership active")
    notes: Optional[str] = Field(None, description="Internal notes")

class Trainer(BaseModel):
    name: str
    specialty: str = Field(..., description="Primary specialty, e.g. Strength, HIIT, Yoga")
    bio: Optional[str] = None
    certifications: Optional[List[str]] = None
    photo_url: Optional[str] = None
    rate_per_session: Optional[int] = Field(None, description="IDR per 60-minute session")
    availability: Optional[List[str]] = Field(None, description="ISO datetime strings or slots")

class GymClass(BaseModel):
    title: str
    description: Optional[str] = None
    coach_id: Optional[str] = Field(None, description="Trainer document _id as string")
    day_of_week: Literal["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    start_time: str = Field(..., description="Start time in HH:MM (24h)")
    duration_min: int = Field(..., ge=15, le=180)
    capacity: int = Field(15, ge=1)
    level: Literal["Beginner","Intermediate","Advanced"] = "Beginner"

# Bookings
class ClassBooking(BaseModel):
    member_id: str
    class_id: str
    date: str = Field(..., description="Class date YYYY-MM-DD")
    status: Literal["pending","confirmed","cancelled"] = "pending"

class TrainerBooking(BaseModel):
    member_id: str
    trainer_id: str
    datetime_iso: str = Field(..., description="Session start time in ISO 8601")
    goals: Optional[str] = None
    notes: Optional[str] = None
    status: Literal["pending","confirmed","cancelled"] = "pending"

# Body recomposition inputs and outputs
class BodyMetric(BaseModel):
    gender: Literal["male","female"]
    age: int = Field(..., ge=12, le=90)
    height_cm: float = Field(..., ge=120, le=230)
    weight_kg: float = Field(..., ge=30, le=250)
    waist_cm: Optional[float] = Field(None, ge=40, le=200)
    hip_cm: Optional[float] = Field(None, ge=40, le=200)
    neck_cm: Optional[float] = Field(None, ge=20, le=60)
    body_fat_pct: Optional[float] = Field(None, ge=3, le=60)
    activity_level: Literal["sedentary","light","moderate","active","athlete"] = "moderate"
    goal: Literal["fat_loss","muscle_gain","recomp"] = "recomp"
    member_id: Optional[str] = None

class ExerciseItem(BaseModel):
    name: str
    sets: int
    reps: str
    frequency_per_week: int

class Recommendation(BaseModel):
    body_metric_id: Optional[str] = None
    summary: str
    weekly_plan: List[ExerciseItem]
