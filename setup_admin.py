"""
Setup script to create admin user for Healthcare Planning Assistant
"""

import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from auth_models import AuthManager

def create_admin_user():
    """Create an admin user for the system"""
    auth_manager = AuthManager()
    
    # Check if admin already exists
    for user in auth_manager.users.values():
        if user.username == "admin":
            print("❌ Admin user already exists")
            return
    
    # Create admin user
    admin_user = auth_manager.create_user(
        username="admin",
        email="admin@healthcare.local",
        password="admin123",
        full_name="System Administrator",
        role="admin"
    )
    
    if admin_user:
        print("✅ Admin user created successfully!")
        print("📝 Login credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Role: admin")
        print("\n🔐 You can now login and create other users through the web interface!")
        print("🌐 Start backend: python run_backend.py")
        print("🖥️  Start frontend: python run_secure_frontend.py")
    else:
        print("❌ Failed to create admin user")

if __name__ == "__main__":
    create_admin_user()
