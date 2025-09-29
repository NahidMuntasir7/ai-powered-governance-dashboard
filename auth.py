import streamlit as st
from typing import Optional, Dict
from database import DatabaseManager

class AuthManager:
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'page' not in st.session_state:
            st.session_state.page = 'login'
    
    def login_form(self) -> bool:
        """Display login form and handle authentication"""
        st.markdown("### 🔐 Login to Civic Feedback Platform")
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns(2)
            with col1:
                login_clicked = st.form_submit_button("🚀 Login", use_container_width=True)
            with col2:
                signup_clicked = st.form_submit_button("📝 Sign Up", use_container_width=True, type="secondary")
            
            if login_clicked:
                if email and password:
                    user = self.db.authenticate_user(email, password)
                    if user:
                        st.session_state.user = user
                        st.session_state.authenticated = True
                        st.success(f"Welcome back, {user['name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password")
                else:
                    st.error("Please fill in all fields")
            
            elif signup_clicked:
                st.session_state.page = 'signup'
                st.rerun()
        
        return st.session_state.authenticated
    
    def signup_form(self) -> bool:
        """Display signup form"""
        st.markdown("### 📝 Create Account")
        
        with st.form("signup_form"):
            name = st.text_input("Full Name", placeholder="Enter your full name")
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Create a password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            
            col1, col2 = st.columns(2)
            with col1:
                location = st.text_input("Location", placeholder="Your area/city")
            with col2:
                phone = st.text_input("Phone (Optional)", placeholder="Your phone number")
            
            # Role selection (hidden admin option)
            role = st.selectbox("Account Type", ["Citizen", "Government Official"])
            actual_role = "admin" if role == "Government Official" else "user"
            
            col1, col2 = st.columns(2)
            with col1:
                signup_clicked = st.form_submit_button("✅ Create Account", use_container_width=True)
            with col2:
                back_clicked = st.form_submit_button("⬅️ Back to Login", use_container_width=True, type="secondary")
            
            if signup_clicked:
                if name and email and password and confirm_password:
                    if password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters long")
                    else:
                        try:
                            user_id = self.db.create_user(
                                name=name,
                                email=email,
                                password=password,
                                role=actual_role,
                                location=location,
                                phone=phone
                            )
                            
                            # Auto-login after signup
                            user = self.db.authenticate_user(email, password)
                            if user:
                                st.session_state.user = user
                                st.session_state.authenticated = True
                                st.success(f"Account created successfully! Welcome, {name}!")
                                
                                # Add welcome notification
                                self.db.add_notification(
                                    user_id=user_id,
                                    title="Welcome!",
                                    message=f"Welcome to the Civic Feedback Platform, {name}! You can now submit feedback and track your issues.",
                                    type="success"
                                )
                                
                                st.rerun()
                        except ValueError as e:
                            st.error(str(e))
                        except Exception as e:
                            st.error("An error occurred while creating your account")
                else:
                    st.error("Please fill in all required fields")
            
            elif back_clicked:
                st.session_state.page = 'login'
                st.rerun()
        
        return False
    
    def logout(self):
        """Logout user"""
        st.session_state.user = None
        st.session_state.authenticated = False
        st.session_state.page = 'login'
        st.success("Logged out successfully!")
        st.rerun()
    
    def require_auth(self, required_role: str = None) -> bool:
        """Check if user is authenticated and has required role"""
        if not st.session_state.authenticated or not st.session_state.user:
            return False
        
        if required_role and st.session_state.user['role'] != required_role:
            st.error(f"Access denied. {required_role.title()} role required.")
            return False
        
        return True
    
    def get_current_user(self) -> Optional[Dict]:
        """Get current authenticated user"""
        if st.session_state.authenticated:
            return st.session_state.user
        return None
    
    def is_admin(self) -> bool:
        """Check if current user is admin"""
        user = self.get_current_user()
        return user and user['role'] == 'admin'
    
    def render_auth_pages(self):
        """Render authentication pages"""
        if st.session_state.page == 'login':
            return self.login_form()
        elif st.session_state.page == 'signup':
            return self.signup_form()
        return False