"""
FastAPI Backend for Healthcare Planning Assistant
RESTful API endpoints for healthcare task planning
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import asyncio
import json

import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
api_dir = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if api_dir not in sys.path:
    sys.path.insert(0, api_dir)

from src.planner_agent import HealthcarePlannerAgent
from src.models import TaskStatus
from src.auth_models import User
from auth import auth_manager, get_current_user

# Initialize FastAPI app
app = FastAPI(
    title="Healthcare Planning Assistant API",
    description="RESTful API for healthcare task planning and scheduling",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth routes
from auth import app as auth_app
app.include_router(auth_app, prefix="/api/auth")

# Global agent instance
agent = HealthcarePlannerAgent()

# Pydantic models for API
class PatientInfo(BaseModel):
    age: Optional[int] = None
    condition: Optional[str] = None
    history: Optional[str] = None

class PlanningRequest(BaseModel):
    goal: str = Field(..., description="Healthcare goal (e.g., 'Treatment Options')")
    patient_info: Optional[PatientInfo] = None
    constraints: Optional[List[str]] = []
    preferences: Optional[Dict[str, Any]] = {}

class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    priority: str
    status: str
    estimated_duration: int
    required_resources: List[str]
    dependencies: List[str]
    scheduled_time: Optional[str] = None

class ExecutionPlanResponse(BaseModel):
    goal: str
    total_duration: int
    tasks: List[TaskResponse]
    created_at: str

class ProgressResponse(BaseModel):
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    progress_percentage: float
    remaining_tasks: int

class ResourceInfo(BaseModel):
    name: str
    type: str
    capacity: int
    current_load: int
    utilization_percentage: float
    available: bool

# In-memory storage for plans (in production, use database)
plans_storage: Dict[str, Any] = {}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Healthcare Planning Assistant API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/plan", response_model=ExecutionPlanResponse)
async def create_plan(request: PlanningRequest, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user)):
    """
    Create a healthcare execution plan
    
    Args:
        request: Planning request with goal, patient info, constraints, and preferences
    
    Returns:
        Execution plan with tasks and schedule
    """
    try:
        # Convert request to agent format
        patient_info = {}
        if request.patient_info:
            patient_info = {
                "age": request.patient_info.age,
                "condition": request.patient_info.condition,
                "history": request.patient_info.history
            }
        
        # Generate plan using agent
        plan = agent.process_request(
            goal=request.goal,
            patient_info=patient_info,
            constraints=request.constraints or [],
            preferences=request.preferences or {}
        )
        
        # Convert to response format
        plan_id = str(uuid.uuid4())
        tasks_response = []
        
        for task in plan.tasks:
            scheduled_time = None
            if task.id in plan.schedule:
                scheduled_time = plan.schedule[task.id].isoformat()
            
            tasks_response.append(TaskResponse(
                id=task.id,
                title=task.title,
                description=task.description,
                priority=task.priority.value,
                status=task.status.value,
                estimated_duration=task.estimated_duration,
                required_resources=task.required_resources,
                dependencies=task.dependencies,
                scheduled_time=scheduled_time
            ))
        
        response = ExecutionPlanResponse(
            goal=plan.goal,
            total_duration=plan.total_duration,
            tasks=tasks_response,
            created_at=datetime.now().isoformat()
        )
        
        # Store plan
        plans_storage[plan_id] = {
            "plan": plan,
            "response": response,
            "created_at": datetime.now()
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create plan: {str(e)}")

@app.get("/api/plan/{plan_id}/progress", response_model=ProgressResponse)
async def get_plan_progress(plan_id: str):
    """Get progress information for a specific plan"""
    try:
        if plan_id not in plans_storage:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        progress = agent.get_task_progress()
        return ProgressResponse(**progress)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get progress: {str(e)}")

@app.put("/api/plan/{plan_id}/task/{task_id}/status")
async def update_task_status(plan_id: str, task_id: str, status: str):
    """Update the status of a specific task"""
    try:
        if plan_id not in plans_storage:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        # Validate status
        try:
            task_status = TaskStatus(status.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
        
        # Update task status
        success = agent.update_task_status(task_id, task_status)
        
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {"message": f"Task status updated to {status}"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update task status: {str(e)}")

@app.get("/api/resources", response_model=List[ResourceInfo])
async def get_resources():
    """Get current resource utilization information"""
    try:
        utilization = agent.get_resource_utilization()
        resources = []
        
        for resource_id, info in utilization.items():
            resources.append(ResourceInfo(
                name=info["name"],
                type=info["type"],
                capacity=info["capacity"],
                current_load=info["current_load"],
                utilization_percentage=info["utilization_percentage"],
                available=info["available"]
            ))
        
        return resources
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get resources: {str(e)}")

@app.get("/api/plans")
async def list_plans():
    """List all created plans"""
    try:
        plans = []
        for plan_id, plan_data in plans_storage.items():
            plans.append({
                "id": plan_id,
                "goal": plan_data["response"].goal,
                "task_count": len(plan_data["response"].tasks),
                "total_duration": plan_data["response"].total_duration,
                "created_at": plan_data["created_at"].isoformat()
            })
        
        return {"plans": plans}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list plans: {str(e)}")

@app.get("/api/plan/{plan_id}/export")
async def export_plan(plan_id: str):
    """Export a plan to JSON format"""
    try:
        if plan_id not in plans_storage:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        plan = plans_storage[plan_id]["plan"]
        filename = f"healthcare_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert plan to exportable format
        export_data = {
            "goal": plan.goal,
            "total_duration": plan.total_duration,
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority.value,
                    "status": task.status.value,
                    "estimated_duration": task.estimated_duration,
                    "required_resources": task.required_resources,
                    "dependencies": task.dependencies,
                    "scheduled_time": plan.schedule.get(task.id, "").isoformat() if task.id in plan.schedule else None
                }
                for task in plan.tasks
            ],
            "exported_at": datetime.now().isoformat()
        }
        
        return {
            "filename": filename,
            "data": export_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export plan: {str(e)}")

@app.delete("/api/plan/{plan_id}")
async def delete_plan(plan_id: str):
    """Delete a specific plan"""
    try:
        if plan_id not in plans_storage:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        del plans_storage[plan_id]
        return {"message": "Plan deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete plan: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
