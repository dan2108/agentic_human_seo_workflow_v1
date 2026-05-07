from pydantic import BaseModel, HttpUrl


class CreateJobRequest(BaseModel):
    site_url: HttpUrl
    business_goal: str
    icp: str
    brand_voice: str


class JobResponse(BaseModel):
    id: str
    site_url: str
    status: str
    created_at: str
