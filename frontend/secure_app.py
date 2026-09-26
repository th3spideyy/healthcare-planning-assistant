"""
Secure Healthcare Planning Assistant with Authentication
Main application with login/signup flow
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import time

# Import authentication pages
from auth_pages import (
    login_page, signup_page, profile_page, 
    logout, check_authentication, api_call
)

# Configuration
API_BASE_URL = "http://localhost:8001"

# Page configuration
st.set_page_config(
    page_title="Healthcare Planning Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E86AB;
        margin: 0.5rem 0;
        color: #000000;
    }
    .task-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
        color: #000000;
    }
    .priority-high { border-left: 4px solid #dc3545; }
    .priority-medium { border-left: 4px solid #ffc107; }
    .priority-low { border-left: 4px solid #28a745; }
    .priority-urgent { border-left: 4px solid #6f42c1; }
    .stTextArea > div > div > textarea {
        color: #000000 !important;
    }
    .stText {
        color: #000000 !important;
    }
    .auth-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
    }
    .user-info {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E86AB;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def show_dashboard():
    """Main dashboard for authenticated users"""
    st.markdown('<h1 class="main-header">🏥 Healthcare Planning Assistant</h1>', unsafe_allow_html=True)
    
    # User info in sidebar
    user = st.session_state.get('user', {})
    st.sidebar.markdown(f"### 👤 {user.get('full_name', 'User')}")
    st.sidebar.markdown(f"**Role:** {user.get('role', 'user').title()}")
    
    # Navigation
    st.sidebar.title("Navigation")
    if st.sidebar.button("📋 Create Plan"):
        st.session_state.current_page = "Create Plan"
        st.rerun()
    
    if st.sidebar.button("📚 View Plans"):
        st.session_state.current_page = "View Plans"
        st.rerun()
    
    if st.sidebar.button("🏥 Resources"):
        st.session_state.current_page = "Resources"
        st.rerun()
    
    if st.sidebar.button("📈 Analytics"):
        st.session_state.current_page = "Analytics"
        st.rerun()
    
    if st.sidebar.button("👤 Profile"):
        st.session_state.current_page = "Profile"
        st.rerun()
    
    if st.sidebar.button("🚪 Logout"):
        logout()
    
    # Main content area
    current_page = st.session_state.get('current_page', 'Create Plan')
    
    if current_page == "Create Plan":
        create_plan_page()
    elif current_page == "View Plans":
        view_plans_page()
    elif current_page == "Resources":
        resources_page()
    elif current_page == "Analytics":
        analytics_page()
    elif current_page == "Profile":
        profile_page()

def create_plan_page():
    """Page for creating new healthcare plans"""
    st.header("📋 Create Healthcare Plan")
    
    # Input form
    with st.form("planning_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            goal = st.selectbox(
                "Healthcare Goal*",
                ["Treatment Options", "Emergency Care", "Routine Checkup", "Surgery Preparation"],
                help="Select the type of healthcare planning needed"
            )
            
            age = st.number_input(
                "Patient Age",
                min_value=0,
                max_value=120,
                value=65,
                help="Patient's age in years"
            )
        
        with col2:
            condition = st.text_input(
                "Condition/Symptoms",
                placeholder="e.g., chest pain, headache, routine checkup",
                help="Describe the patient's condition or symptoms"
            )
            
            constraint = st.selectbox(
                "Constraints",
                ["None", "Urgent", "Limited Mobility", "Requires Anesthesia", "Routine"],
                help="Any specific constraints or requirements"
            )
        
        specialist = st.selectbox(
            "Specialist Preference",
            ["None", "Cardiologist", "Neurologist", "General Practitioner", "Orthopedic"],
            help="Preferred specialist (if any)"
        )
        
        submitted = st.form_submit_button("🚀 Generate Plan", type="primary")
        
        if submitted:
            if not condition:
                st.error("Please describe the patient's condition")
                return
            
            # Prepare request data
            request_data = {
                "goal": goal,
                "patient_info": {
                    "age": age,
                    "condition": condition
                },
                "constraints": [constraint.lower()] if constraint != "None" else [],
                "preferences": {"specialist": specialist.lower()} if specialist != "None" else {}
            }
            
            # Show loading spinner
            with st.spinner("Generating healthcare plan..."):
                plan = api_call("POST", "/api/plan", request_data)
            
            if plan:
                st.session_state.current_plan = plan
                st.success("✅ Plan generated successfully!")
                display_plan(plan)
    
    # Display plan if it exists
    if st.session_state.get('current_plan'):
        display_plan(st.session_state.current_plan)

def display_plan(plan):
    """Display a healthcare plan"""
    st.subheader("📊 Execution Plan")
    
    # Plan summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tasks", len(plan["tasks"]))
    
    with col2:
        st.metric("Duration", f"{plan['total_duration']} min")
    
    with col3:
        high_priority = sum(1 for task in plan["tasks"] if task["priority"] in ["high", "urgent"])
        st.metric("High Priority", high_priority)
    
    with col4:
        created_time = datetime.fromisoformat(plan["created_at"].replace("Z", "+00:00"))
        st.metric("Created", created_time.strftime("%H:%M"))
    
    # Tasks display
    st.subheader("📋 Task Breakdown")
    
    # Group tasks by priority
    priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
    sorted_tasks = sorted(plan["tasks"], key=lambda x: priority_order.get(x["priority"], 4))
    
    for task in sorted_tasks:
        priority_class = f"priority-{task['priority']}"
        
        with st.container():
            st.markdown(f"""
            <div class="task-card {priority_class}">
                <h4>{task['title']}</h4>
                <p><strong>Description:</strong> {task['description']}</p>
                <p><strong>Priority:</strong> {task['priority'].upper()} | 
                   <strong>Duration:</strong> {task['estimated_duration']} min | 
                   <strong>Status:</strong> {task['status'].upper()}</p>
                <p><strong>Resources:</strong> {', '.join(task['required_resources'])}</p>
                {f"<p><strong>Scheduled:</strong> {datetime.fromisoformat(task['scheduled_time'].replace('Z', '+00:00')).strftime('%H:%M')}</p>" if task['scheduled_time'] else ""}
                {f"<p><strong>Dependencies:</strong> {len(task['dependencies'])} task(s)</p>" if task['dependencies'] else ""}
            </div>
            """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📈 Update Progress"):
            st.info("Progress tracking coming soon!")
    
    with col2:
        if st.button("💾 Export Plan"):
            st.json(plan, expanded=True)
            st.success("Plan data displayed above. You can copy and save it.")
    
    with col3:
        if st.button("🔄 Refresh Status"):
            st.rerun()

def view_plans_page():
    """Page for viewing existing plans"""
    st.header("📚 Plan History")
    
    # Get all plans (this would need to be implemented in backend)
    st.info("Plan history feature coming soon! For now, plans are stored in your current session.")
    
    # Show current plan if exists
    if st.session_state.get('current_plan'):
        st.subheader("Current Plan")
        plan = st.session_state.current_plan
        st.json(plan)

def resources_page():
    """Page for viewing resource utilization"""
    st.header("🏥 Resource Utilization")
    
    # Get resources
    resources = api_call("GET", "/api/resources")
    
    if not resources:
        st.error("Failed to load resources")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_resources = len(resources)
        st.metric("Total Resources", total_resources)
    
    with col2:
        available = sum(1 for r in resources if r["available"])
        st.metric("Available", f"{available}/{total_resources}")
    
    with col3:
        avg_utilization = sum(r["utilization_percentage"] for r in resources) / len(resources)
        st.metric("Avg Utilization", f"{avg_utilization:.1f}%")
    
    with col4:
        busy_resources = sum(1 for r in resources if not r["available"])
        st.metric("Busy Resources", busy_resources)
    
    # Resource utilization chart
    st.subheader("📊 Resource Utilization Chart")
    
    df = pd.DataFrame(resources)
    fig = px.bar(
        df,
        x="name",
        y="utilization_percentage",
        color="type",
        title="Resource Utilization by Type",
        labels={"utilization_percentage": "Utilization (%)", "name": "Resource Name"}
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    
    # Resource details table
    st.subheader("📋 Resource Details")
    
    # Add status indicator
    df["status"] = df["available"].apply(lambda x: "🟢 Available" if x else "🔴 Busy")
    
    # Reorder columns
    display_df = df[["name", "type", "status", "capacity", "current_load", "utilization_percentage"]]
    display_df.columns = ["Name", "Type", "Status", "Capacity", "Current Load", "Utilization %"]
    
    st.dataframe(display_df, use_container_width=True)

def analytics_page():
    """Page for analytics and insights"""
    st.header("📈 Analytics Dashboard")
    
    # This would show analytics for the current user
    st.info("Analytics feature coming soon! This will show your planning history and insights.")
    
    # Show current plan stats if available
    if st.session_state.get('current_plan'):
        plan = st.session_state.current_plan
        
        st.subheader("Current Plan Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Tasks", len(plan["tasks"]))
        
        with col2:
            st.metric("Duration", f"{plan['total_duration']} min")
        
        with col3:
            urgent_tasks = sum(1 for task in plan["tasks"] if task["priority"] == "urgent")
            st.metric("Urgent Tasks", urgent_tasks)
        
        with col4:
            created_time = datetime.fromisoformat(plan["created_at"].replace("Z", "+00:00"))
            st.metric("Created", created_time.strftime("%Y-%m-%d"))

def main():
    """Main application with authentication flow"""
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    # Check authentication
    if st.session_state.logged_in:
        if not check_authentication():
            st.session_state.logged_in = False
            st.error("Session expired. Please login again.")
            st.rerun()
            return
        
        show_dashboard()
    else:
        # Show login/signup options
        st.markdown('<h1 class="main-header">🏥 Healthcare Planning Assistant</h1>', unsafe_allow_html=True)
        
        # Navigation tabs
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        
        with tab1:
            login_page()
        
        with tab2:
            signup_page()

if __name__ == "__main__":
    main()
