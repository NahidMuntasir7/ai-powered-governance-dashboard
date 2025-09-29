import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import os

# Import all modules
from database import DatabaseManager
from ai_processing import EnhancedAIProcessor
from auth import AuthManager
from notifications import NotificationManager
from reports import ReportGenerator
from public_dashboard import PublicDashboard

# Configure Streamlit page
st.set_page_config(
    page_title="🏛️ Civic Feedback & Governance Platform",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize components
@st.cache_resource
def init_components():
    """Initialize all components"""
    db = DatabaseManager()
    
    # Try to get API key from multiple sources
    api_key = None
    try:
        api_key = st.secrets.get("GOOGLE_API_KEY")
    except:
        pass
    
    if not api_key:
        api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        try:
            with open('.env', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith('GOOGLE_API_KEY='):
                        api_key = line.split('=', 1)[1].strip()
                        break
        except:
            pass
    
    ai_processor = EnhancedAIProcessor(api_key)
    auth_manager = AuthManager(db)
    notification_manager = NotificationManager(db)
    report_generator = ReportGenerator(db)
    public_dashboard = PublicDashboard(db)
    
    return db, ai_processor, auth_manager, notification_manager, report_generator, public_dashboard

# Initialize all components
db, ai_processor, auth_manager, notification_manager, report_generator, public_dashboard = init_components()

# HIGH CONTRAST CSS - BLACK CARDS WITH WHITE TEXT + BUTTON FIX
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    .main-header {
        font-family: 'Poppins', sans-serif;
        font-size: 3rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .subtitle {
        text-align: center;
        color: #64748b;
        font-size: 1.2rem;
        font-weight: 400;
        margin-bottom: 2rem;
        font-family: 'Poppins', sans-serif;
    }
    
    /* HIGH CONTRAST BLACK METRIC CARDS WITH WHITE TEXT */
    .metric-card {
        background: #000000;
        color: #ffffff;
        padding: 2rem;
        border-radius: 16px;
        border: 2px solid #ffffff;
        box-shadow: 0 8px 32px rgba(255,255,255,0.1);
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(255,255,255,0.2);
        border-color: #3b82f6;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    }
    
    .metric-card h3 {
        color: #ffffff;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        font-family: 'Poppins', sans-serif;
    }
    
    .metric-card .number {
        color: #ffffff;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
        font-family: 'Poppins', sans-serif;
    }
    
    .metric-card .subtitle {
        color: #cccccc;
        font-size: 0.85rem;
        font-weight: 400;
        margin: 0;
    }
    
    /* Specific Card Accent Colors for Numbers */
    .total-feedback .number { color: #60a5fa; }
    .total-feedback::before { background: linear-gradient(90deg, #3b82f6, #1d4ed8); }
    
    .recent-feedback .number { color: #22d3ee; }
    .recent-feedback::before { background: linear-gradient(90deg, #06b6d4, #0891b2); }
    
    .high-priority .number { color: #f87171; }
    .high-priority::before { background: linear-gradient(90deg, #ef4444, #dc2626); }
    
    .resolution-rate .number { color: #4ade80; }
    .resolution-rate::before { background: linear-gradient(90deg, #10b981, #059669); }
    
    /* Feedback Cards - Black with White Text */
    .feedback-card {
        background: #000000;
        color: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #ffffff;
        box-shadow: 0 4px 20px rgba(255,255,255,0.1);
        margin-bottom: 1rem;
        border-left: 5px solid #3b82f6;
        transition: transform 0.2s ease;
    }
    
    .feedback-card:hover {
        transform: translateX(5px);
        box-shadow: 0 6px 25px rgba(255,255,255,0.15);
        border-color: #60a5fa;
    }
    
    .feedback-card.urgency-high {
        border-left-color: #ef4444;
    }
    
    .feedback-card.urgency-medium {
        border-left-color: #f59e0b;
    }
    
    .feedback-card.urgency-low {
        border-left-color: #10b981;
    }
    
    .feedback-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 0.5rem;
        font-family: 'Poppins', sans-serif;
    }
    
    .feedback-meta {
        color: #cccccc;
        font-size: 0.9rem;
        margin-bottom: 0.8rem;
    }
    
    .feedback-text {
        color: #e5e5e5;
        line-height: 1.6;
        margin-bottom: 0.8rem;
    }
    
    .feedback-date {
        color: #999999;
        font-size: 0.8rem;
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        color: white;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-pending { background: linear-gradient(135deg, #f59e0b, #d97706); }
    .status-inprogress { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }
    .status-resolved { background: linear-gradient(135deg, #10b981, #059669); }
    .status-rejected { background: linear-gradient(135deg, #ef4444, #dc2626); }
    
    /* Chart Container - Black with White Border */
    .chart-container {
        background: #000000;
        color: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #ffffff;
        box-shadow: 0 4px 20px rgba(255,255,255,0.1);
        margin-bottom: 1.5rem;
    }
    
    .chart-title {
        color: #ffffff;
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 1rem;
        font-family: 'Poppins', sans-serif;
    }
    
    /* Info Boxes - Black with Colored Borders */
    .info-box {
        background: #000000;
        color: #ffffff;
        padding: 1.5rem;
        border-radius: 8px;
        border: 2px solid;
        margin-bottom: 1rem;
    }
    
    .info-box.blue { border-color: #3b82f6; }
    .info-box.green { border-color: #10b981; }
    .info-box.yellow { border-color: #f59e0b; }
    .info-box.red { border-color: #ef4444; }
    
    /* FIXED BUTTON STYLING - NO HOVER STATE PERSISTENCE */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8) !important;
        color: white !important;
        border: 2px solid #ffffff !important;
        border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-family: 'Poppins', sans-serif !important;
        transition: all 0.3s ease !important;
        position: relative !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8, #1e40af) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3) !important;
    }
    
    /* RESET BUTTON STATE AFTER CLICK */
    .stButton > button:active,
    .stButton > button:focus {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8) !important;
        transform: none !important;
        box-shadow: none !important;
        outline: none !important;
    }
    
    /* Ensure buttons return to normal state */
    .stButton > button:not(:hover):not(:active):not(:focus) {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8) !important;
        transform: none !important;
        box-shadow: none !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #64748b;
        padding: 2rem;
        margin-top: 2rem;
        border-top: 1px solid #ffffff;
        font-family: 'Poppins', sans-serif;
    }
    
    .footer-title {
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 0.5rem;
    }
    
    .footer-subtitle {
        font-size: 0.9rem;
        color: #cccccc;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
auth_manager.initialize_session_state()

# Initialize navigation state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'dashboard'
if 'nav_clicked' not in st.session_state:
    st.session_state.nav_clicked = False

def main():
    """Main application logic"""
    
    # Handle sidebar navigation with proper state management
    with st.sidebar:
        if st.session_state.authenticated:
            # User is logged in - show appropriate navigation
            user = auth_manager.get_current_user()
            
            # Profile navigation with key to prevent state issues
            profile_clicked = st.button(
                f"👤 My Profile ({user['name']})", 
                use_container_width=True,
                key="profile_nav_btn",
                help="Return to your dashboard"
            )
            
            if profile_clicked:
                st.session_state.current_page = 'dashboard'
                st.session_state.page = 'dashboard'
                st.session_state.nav_clicked = True
                st.rerun()
        else:
            # User is not logged in - show login option
            login_clicked = st.button(
                "🔐 Login/Signup", 
                use_container_width=True,
                key="login_nav_btn",
                help="Access your account"
            )
            
            if login_clicked:
                st.session_state.current_page = 'login'
                st.session_state.page = 'login'
                st.session_state.nav_clicked = True
                st.rerun()
        
        # Public dashboard button (always available) with unique key
        public_clicked = st.button(
            "🌐 Public Dashboard", 
            use_container_width=True,
            key="public_nav_btn",
            help="View public transparency dashboard"
        )
        
        if public_clicked:
            st.session_state.current_page = 'public'
            st.session_state.page = 'public'
            st.session_state.nav_clicked = True
            st.rerun()
    
    # Reset navigation click state after handling
    if st.session_state.get('nav_clicked', False):
        st.session_state.nav_clicked = False
    
    # Handle public dashboard
    if st.session_state.get('page') == 'public' or st.session_state.get('current_page') == 'public':
        public_dashboard.render_public_dashboard()
        return
    
    # Authentication flow
    if not st.session_state.authenticated:
        st.markdown("<h1 class='main-header'>🏛️ Civic Feedback & Governance Platform</h1>", unsafe_allow_html=True)
        st.markdown("<p class='subtitle'>AI-Powered Citizen Engagement • Built for HackTheAI 2024</p>", unsafe_allow_html=True)
        
        # Demo credentials info
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 🎯 Demo Credentials")
            st.markdown("""
            <div style="
            background-color: #000; 
            color: #fff; 
            border: 1px solid #fff; 
            border-radius: 10px; 
            padding: 20px; 
            max-width: 400px; 
            font-family: Arial, sans-serif;
            ">
            <p style="margin-bottom: 15px;">
            <strong>👤 Citizen Account:</strong><br>
            Email: <a href="mailto:ahmed@email.com" style="color: #fff; text-decoration: underline;">ahmed@email.com</a><br>
            Password: <code style="background-color: #222; padding: 2px 4px; border-radius: 3px;">password123</code>
            </p>
            <p>
            <strong>👨‍💼 Admin Account:</strong><br>
            Email: <a href="mailto:admin@gov.bd" style="color: #fff; text-decoration: underline;">admin@gov.bd</a><br>
            Password: <code style="background-color: #222; padding: 2px 4px; border-radius: 3px;">admin123</code>
            </p>
            </div>
            """, unsafe_allow_html=True)
        
        auth_manager.render_auth_pages()
        return
    
    # Main application for authenticated users
    user = auth_manager.get_current_user()
    
    # Header
    st.markdown("<h1 class='main-header'>🏛️ Civic Feedback & Governance Platform</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='subtitle'>Welcome back, {user['name']} • {user['role'].title()} Dashboard</p>", unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"### 👋 Hello, {user['name']}")
        st.markdown(f"**Role:** {user['role'].title()}")
        st.markdown(f"**Location:** {user.get('location', 'Not specified')}")
        
        st.markdown("---")
        
        # Notifications count
        unread_count = notification_manager.get_unread_count(user['user_id'])
        
        if user['role'] == 'admin':
            # Admin navigation
            page = st.selectbox(
                "📍 Navigation",
                [
                    "📊 Admin Dashboard",
                    "📋 Current Stack", 
                    "✅ Resolved Issues",
                    "📈 Analytics & Insights",
                    "🚨 Spam & Moderation",
                    "📊 Generate Reports",
                    f"🔔 Notifications ({unread_count})"
                ],
                key="admin_nav_select"
            )
        else:
            # User navigation
            page = st.selectbox(
                "📍 Navigation",
                [
                    "📊 My Dashboard",
                    "📝 Submit Feedback",
                    "📋 My Feedback",
                    f"🔔 Notifications ({unread_count})"
                ],
                key="user_nav_select"
            )
        
        st.markdown("---")
        
        # Logout button with unique key
        logout_clicked = st.button(
            "🚪 Logout", 
            use_container_width=True,
            key="logout_btn",
            help="Sign out of your account"
        )
        
        if logout_clicked:
            st.session_state.current_page = 'login'
            st.session_state.nav_clicked = True
            auth_manager.logout()
    
    # Route to appropriate page
    if user['role'] == 'admin':
        render_admin_pages(page, user, notification_manager, report_generator)
    else:
        render_user_pages(page, user, notification_manager)

def render_user_pages(page: str, user: dict, notification_manager):
    """Render user-specific pages"""
    
    if page == "📊 My Dashboard":
        render_user_dashboard(user)
    
    elif page == "📝 Submit Feedback":
        render_submit_feedback(user, notification_manager)
    
    elif page == "📋 My Feedback":
        render_my_feedback(user)
    
    elif "🔔 Notifications" in page:
        st.markdown("### 🔔 My Notifications")
        notification_manager.render_notification_panel(user['user_id'])

def render_admin_pages(page: str, user: dict, notification_manager, report_generator):
    """Render admin-specific pages"""
    
    if page == "📊 Admin Dashboard":
        render_admin_dashboard(user)
    
    elif page == "📋 Current Stack":
        render_current_stack(user, notification_manager)
    
    elif page == "✅ Resolved Issues":
        render_resolved_issues()
    
    elif page == "📈 Analytics & Insights":
        render_analytics_insights()
    
    elif page == "🚨 Spam & Moderation":
        render_spam_moderation(user)
    
    elif page == "📊 Generate Reports":
        report_generator.render_report_interface(user['user_id'])
    
    elif "🔔 Notifications" in page:
        st.markdown("### 🔔 Admin Notifications")
        notification_manager.render_notification_panel(user['user_id'])

def render_user_dashboard(user: dict):
    """Render user dashboard"""
    st.markdown("### 📊 My Civic Engagement Dashboard")
    
    # Get user's feedback
    user_feedback = db.get_user_feedback(user['user_id'])
    
    # User statistics
    col1, col2, col3, col4 = st.columns(4)
    
    total_submitted = len(user_feedback)
    resolved_count = len([f for f in user_feedback if f['status'] == 'Resolved'])
    pending_count = len([f for f in user_feedback if f['status'] == 'Pending'])
    in_progress_count = len([f for f in user_feedback if f['status'] == 'In Progress'])
    
    with col1:
        st.markdown(f"""
        <div class="metric-card total-feedback">
            <h3>📝 Submitted</h3>
            <div class="number">{total_submitted}</div>
            <div class="subtitle">Total feedback</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card resolution-rate">
            <h3>✅ Resolved</h3>
            <div class="number">{resolved_count}</div>
            <div class="subtitle">Issues fixed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card recent-feedback">
            <h3>⏳ In Progress</h3>
            <div class="number">{in_progress_count}</div>
            <div class="subtitle">Being worked on</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card high-priority">
            <h3>⏸️ Pending</h3>
            <div class="number">{pending_count}</div>
            <div class="subtitle">Awaiting response</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent feedback
    if user_feedback:
        st.markdown("### 📋 Your Recent Feedback")
        
        for feedback in user_feedback[:5]:
            status_class = f"status-{feedback['status'].lower().replace(' ', '')}"
            severity_class = f"urgency-{feedback['severity'].lower()}" if feedback['severity'] else ""
            
            st.markdown(f"""
            <div class="feedback-card {severity_class}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <div class="feedback-header">{feedback['title']}</div>
                    <span class="status-badge {status_class}">{feedback['status']}</span>
                </div>
                <div class="feedback-meta">
                    📂 {feedback.get('category', 'Uncategorized')} • 🎯 {feedback.get('severity', 'Unknown')} Priority
                </div>
                <div class="feedback-text">
                    {feedback['description'][:150]}...
                </div>
                {f'<div class="info-box green"><strong>AI Response:</strong><br>{feedback["ai_response"]}</div>' if feedback.get('ai_response') else ''}
                {f'<div class="info-box blue"><strong>Official Response:</strong><br>{feedback["official_response"]}</div>' if feedback.get('official_response') else ''}
                {f'📅 {feedback["created_at"][:10]}' if feedback.get("created_at") else ''}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No feedback submitted yet. Start by submitting your first feedback!")

def render_submit_feedback(user: dict, notification_manager):
    """Render feedback submission form"""
    st.markdown("### 📝 Submit New Civic Feedback")
    st.markdown("Help improve your community by reporting issues and concerns.")
    
    with st.form("feedback_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Issue Title *", placeholder="Brief description of the issue")
            category = st.selectbox("Category (Optional)", 
                                  ["Auto-detect"] + ["Traffic", "Sanitation", "Safety", "Water", "Electricity", "Infrastructure", "Other"])
        
        with col2:
            severity = st.selectbox("Severity (Optional)", 
                                  ["Auto-detect", "High", "Medium", "Low"])
            location_detail = st.text_input("Specific Location", placeholder="Detailed location of the issue")
        
        description = st.text_area(
            "Detailed Description *",
            placeholder="Please provide a detailed description of the issue, including when it started, how it affects you, and any other relevant information...",
            height=150
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("🚀 Submit Feedback", use_container_width=True)
        
        if submitted:
            if title and description:
                with st.spinner("🤖 Processing your feedback with AI..."):
                    # Determine category and severity
                    if category == "Auto-detect":
                        detected_category, cat_confidence = ai_processor.categorize_feedback(title, description)
                        final_category = detected_category
                    else:
                        final_category = category
                    
                    if severity == "Auto-detect":
                        detected_severity, sev_confidence = ai_processor.detect_severity(title, description)
                        final_severity = detected_severity
                    else:
                        final_severity = severity
                    
                    # Submit feedback
                    feedback_id = db.submit_feedback(
                        user_id=user['user_id'],
                        title=title,
                        description=description,
                        category=final_category,
                        severity=final_severity,
                        location_detail=location_detail
                    )
                    
                    # AI Processing
                    ai_response = ai_processor.generate_ai_response(title, description, final_category, final_severity)
                    action_plan = ai_processor.generate_action_plan(title, description, final_category, final_severity)
                    priority_score = ai_processor.calculate_priority_score(final_severity, final_category, description)
                    spam_score, spam_reason = ai_processor.detect_spam(title, description)
                    
                    # Update feedback with AI results
                    db.update_feedback(
                        feedback_id=feedback_id,
                        updates={
                            'ai_response': ai_response,
                            'priority_score': priority_score,
                            'spam_confidence': spam_score
                        },
                        changed_by=user['user_id']
                    )
                    
                    # Create notifications
                    notification_manager.notify_feedback_submitted(user['user_id'], feedback_id, title)
                    notification_manager.notify_admins_new_feedback(feedback_id, title, final_severity, final_category)
                
                st.success("✅ Your feedback has been submitted successfully!")
                
                # Show AI analysis results
                st.markdown("### 🤖 AI Analysis Results")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>📂 Category</h3>
                        <div class="number" style="font-size: 1.5rem; color: #60a5fa;">{final_category}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    urgency_colors = {"High": "#f87171", "Medium": "#fbbf24", "Low": "#4ade80"}
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>🎯 Severity</h3>
                        <div class="number" style="font-size: 1.5rem; color: {urgency_colors.get(final_severity, '#ffffff')};">
                            {final_severity}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # AI Response
                with st.expander("💡 AI Response for You", expanded=True):
                    st.markdown(f"""
                    <div class="info-box blue">
                        {ai_response}
                    </div>
                    """, unsafe_allow_html=True)
                
                st.balloons()
            else:
                st.error("❌ Please fill in all required fields.")

def render_my_feedback(user: dict):
    """Render user's feedback list"""
    st.markdown("### 📋 My Feedback History")
    
    user_feedback = db.get_user_feedback(user['user_id'])
    
    if not user_feedback:
        st.info("No feedback submitted yet.")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All", "Pending", "In Progress", "Resolved", "Rejected"])
    with col2:
        category_filter = st.selectbox("Filter by Category", ["All"] + ["Traffic", "Sanitation", "Safety", "Water", "Electricity", "Infrastructure", "Other"])
    with col3:
        sort_by = st.selectbox("Sort by", ["Newest First", "Oldest First", "Priority"])
    
    # Apply filters
    filtered_feedback = user_feedback
    if status_filter != "All":
        filtered_feedback = [f for f in filtered_feedback if f['status'] == status_filter]
    if category_filter != "All":
        filtered_feedback = [f for f in filtered_feedback if f.get('category') == category_filter]
    
    # Sort
    if sort_by == "Newest First":
        filtered_feedback.sort(key=lambda x: x['created_at'], reverse=True)
    elif sort_by == "Oldest First":
        filtered_feedback.sort(key=lambda x: x['created_at'])
    else:  # Priority
        filtered_feedback.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
    
    st.info(f"📊 Showing {len(filtered_feedback)} feedback items")
    
    # Display feedback
    for feedback in filtered_feedback:
        with st.expander(f"🎯 {feedback['title']} • {feedback['status']} • {feedback['created_at'][:10]}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("**📝 Description:**")
                st.markdown(f"""
                <div class="info-box blue">
                    {feedback['description']}
                </div>
                """, unsafe_allow_html=True)
                
                if feedback.get('ai_response'):
                    st.markdown("**🤖 AI Response:**")
                    st.markdown(f"""
                    <div class="info-box green">
                        {feedback['ai_response']}
                    </div>
                    """, unsafe_allow_html=True)
                
                if feedback.get('official_response'):
                    st.markdown("**📧 Official Response:**")
                    st.markdown(f"""
                    <div class="info-box yellow">
                        {feedback['official_response']}
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("**📊 Details:**")
                st.markdown(f"""
                <div class="metric-card" style="text-align: left; font-size: 0.9rem;">
                    <strong>📂 Category:</strong> {feedback.get('category', 'N/A')}<br>
                    <strong>🎯 Severity:</strong> {feedback.get('severity', 'N/A')}<br>
                    <strong>📈 Status:</strong> {feedback['status']}<br>
                    <strong>🏆 Priority:</strong> {feedback.get('priority_score', 0):.2f}<br>
                    <strong>📍 Location:</strong> {feedback.get('location_detail', 'N/A')}<br>
                    <strong>📅 Created:</strong> {feedback['created_at'][:10]}
                </div>
                """, unsafe_allow_html=True)
                
                # Delete button with unique key
                if feedback['status'] == 'Pending':
                    if st.button(f"🗑️ Delete", key=f"delete_{feedback['feedback_id']}_{user['user_id']}"):
                        if db.soft_delete_feedback(feedback['feedback_id'], user['user_id']):
                            st.success("Feedback deleted successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to delete feedback.")

def render_admin_dashboard(user: dict):
    """Render admin dashboard"""
    st.markdown("### 📊 Administrative Dashboard")
    st.markdown("Overview of civic feedback and government response metrics")
    
    # Get comprehensive statistics
    stats = db.get_feedback_stats()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card total-feedback">
            <h3>📋 Total Issues</h3>
            <div class="number">{stats['total_feedback']}</div>
            <div class="subtitle">All feedback received</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        high_priority = stats['severity_stats'].get('High', 0)
        st.markdown(f"""
        <div class="metric-card high-priority">
            <h3>🚨 High Priority</h3>
            <div class="number">{high_priority}</div>
            <div class="subtitle">Urgent attention needed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card resolution-rate">
            <h3>✅ Resolution Rate</h3>
            <div class="number">{stats['resolution_rate']}%</div>
            <div class="subtitle">Issues resolved</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card recent-feedback">
            <h3>⚠️ Potential Spam</h3>
            <div class="number">{stats['potential_spam']}</div>
            <div class="subtitle">Needs review</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">📊 Issues by Category</h3>', unsafe_allow_html=True)
        
        if stats['category_stats']:
            fig_category = px.pie(
                values=list(stats['category_stats'].values()),
                names=list(stats['category_stats'].keys()),
                color_discrete_sequence=['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'],
                hole=0.4
            )
            fig_category.update_traces(
                textposition='inside',
                textinfo='percent+label',
                textfont_size=12,
                textfont_color='white'
            )
            fig_category.update_layout(
                font=dict(size=12, color='#ffffff'),
                showlegend=True,
                legend=dict(font=dict(color='#ffffff')),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_category, use_container_width=True)
        else:
            st.info("No category data available.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">📈 Severity Distribution</h3>', unsafe_allow_html=True)
        
        if stats['severity_stats']:
            severity_colors = {'High': '#ef4444', 'Medium': '#f59e0b', 'Low': '#10b981'}
            severity_data = stats['severity_stats']
            
            fig_severity = go.Figure(data=[
                go.Bar(
                    x=list(severity_data.keys()),
                    y=list(severity_data.values()),
                    marker_color=[severity_colors.get(k, '#64748b') for k in severity_data.keys()],
                    text=list(severity_data.values()),
                    textposition='auto',
                    textfont=dict(color='white', size=14),
                    marker=dict(line=dict(color='rgba(255,255,255,0.8)', width=1))
                )
            ])
            fig_severity.update_layout(
                xaxis_title="Severity Level",
                yaxis_title="Number of Issues",
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#ffffff'),
                xaxis=dict(tickfont=dict(color='#ffffff')),
                yaxis=dict(tickfont=dict(color='#ffffff')),
                margin=dict(t=20, b=40, l=40, r=20)
            )
            st.plotly_chart(fig_severity, use_container_width=True)
        else:
            st.info("No severity data available.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # AI Insights
    st.markdown("### 🤖 AI-Generated Insights")
    with st.spinner("Generating AI insights..."):
        insights = ai_processor.generate_insights(stats)
    
    st.markdown(f"""
    <div class="info-box blue">
        {insights}
    </div>
    """, unsafe_allow_html=True)

def render_current_stack(user: dict, notification_manager):
    """Render current stack for admins"""
    st.markdown("### 📋 Current Issues Stack")
    st.markdown("Prioritized list of pending and in-progress issues")
    
    # Get pending and in-progress feedback
    all_feedback = db.get_all_feedback()
    current_stack = [f for f in all_feedback if f['status'] in ['Pending', 'In Progress']]
    
    # Sort by priority score and severity
    current_stack.sort(key=lambda x: (
        {'High': 3, 'Medium': 2, 'Low': 1}.get(x.get('severity', 'Low'), 1),
        x.get('priority_score', 0)
    ), reverse=True)
    
    if not current_stack:
        st.info("No pending issues in the current stack.")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        severity_filter = st.selectbox("Filter by Severity", ["All", "High", "Medium", "Low"])
    with col2:
        category_filter = st.selectbox("Filter by Category", ["All"] + ["Traffic", "Sanitation", "Safety", "Water", "Electricity", "Infrastructure", "Other"])
    with col3:
        status_filter = st.selectbox("Filter by Status", ["All", "Pending", "In Progress"])
    
    # Apply filters
    filtered_stack = current_stack
    if severity_filter != "All":
        filtered_stack = [f for f in filtered_stack if f.get('severity') == severity_filter]
    if category_filter != "All":
        filtered_stack = [f for f in filtered_stack if f.get('category') == category_filter]
    if status_filter != "All":
        filtered_stack = [f for f in filtered_stack if f['status'] == status_filter]
    
    st.info(f"📊 Showing {len(filtered_stack)} issues in current stack")
    
    # Display issues
    for feedback in filtered_stack:
        severity_class = f"urgency-{feedback.get('severity', 'low').lower()}"
        status_class = f"status-{feedback['status'].lower().replace(' ', '')}"
        
        with st.expander(f"🎯 Priority {feedback.get('priority_score', 0):.2f} • {feedback.get('severity', 'Unknown')} • {feedback['title']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("**📝 Issue Description:**")
                st.markdown(f"""
                <div class="info-box blue">
                    {feedback['description']}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("**🤖 AI-Generated Action Plan:**")
                action_plan = ai_processor.generate_action_plan(
                    feedback['title'], 
                    feedback['description'], 
                    feedback.get('category', 'Other'), 
                    feedback.get('severity', 'Medium')
                )
                st.markdown(f"""
                <div class="info-box yellow">
                    {action_plan}
                </div>
                """, unsafe_allow_html=True)
                
                if feedback.get('spam_confidence', 0) > 0.3:
                    st.markdown("**⚠️ Spam Detection Alert:**")
                    st.markdown(f"""
                    <div class="info-box red">
                        Spam confidence: {feedback.get('spam_confidence', 0):.2f}<br>
                        Please review this submission carefully.
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("**📊 Issue Details:**")
                st.markdown(f"""
                <div class="metric-card" style="text-align: left; font-size: 0.9rem;">
                    <strong>👤 Citizen:</strong> {feedback['name']}<br>
                    <strong>📧 Email:</strong> {feedback.get('email', 'N/A')}<br>
                    <strong>📍 Location:</strong> {feedback.get('location_detail', 'N/A')}<br>
                    <strong>📂 Category:</strong> {feedback.get('category', 'N/A')}<br>
                    <strong>🎯 Severity:</strong> {feedback.get('severity', 'N/A')}<br>
                    <strong>📈 Status:</strong> {feedback['status']}<br>
                    <strong>🏆 Priority:</strong> {feedback.get('priority_score', 0):.2f}<br>
                    <strong>📅 Created:</strong> {feedback['created_at'][:10]}
                </div>
                """, unsafe_allow_html=True)
                
                # Response form
                st.markdown("**📧 Send Official Response:**")
                response_text = st.text_area(
                    "Response Message",
                    placeholder="Enter your official response to the citizen...",
                    key=f"response_{feedback['feedback_id']}",
                    height=100
                )
                
                # Status update
                new_status = st.selectbox(
                    "Update Status",
                    ["Pending", "In Progress", "Resolved", "Rejected"],
                    index=["Pending", "In Progress", "Resolved", "Rejected"].index(feedback['status']),
                    key=f"status_{feedback['feedback_id']}"
                )
                
                if st.button(f"💾 Update Issue", key=f"update_{feedback['feedback_id']}"):
                    updates = {}
                    
                    if response_text:
                        updates['official_response'] = response_text
                    
                    if new_status != feedback['status']:
                        updates['status'] = new_status
                    
                    if updates:
                        success = db.update_feedback(
                            feedback['feedback_id'],
                            updates,
                            user['user_id']
                        )
                        
                        if success:
                            # Send notification to citizen
                            if response_text:
                                notification_manager.notify_admin_response(
                                    feedback['user_id'],
                                    feedback['feedback_id'],
                                    feedback['title']
                                )
                            
                            if new_status != feedback['status']:
                                notification_manager.notify_status_change(
                                    feedback['user_id'],
                                    feedback['feedback_id'],
                                    feedback['title'],
                                    feedback['status'],
                                    new_status
                                )
                            
                            st.success("Issue updated successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to update issue.")

def render_resolved_issues():
    """Render resolved issues"""
    st.markdown("### ✅ Resolved Issues")
    st.markdown("Archive of successfully completed civic issues")
    
    # Get resolved feedback
    resolved_feedback = db.get_all_feedback(status='Resolved')
    
    if not resolved_feedback:
        st.info("No resolved issues yet.")
        return
    
    # Statistics
    col1, col2, col3 = st.columns(3)
    
    total_resolved = len(resolved_feedback)
    categories = {}
    for feedback in resolved_feedback:
        cat = feedback.get('category', 'Unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    with col1:
        st.markdown(f"""
        <div class="metric-card resolution-rate">
            <h3>✅ Total Resolved</h3>
            <div class="number">{total_resolved}</div>
            <div class="subtitle">Issues completed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        top_category = max(categories.items(), key=lambda x: x[1])[0] if categories else 'None'
        st.markdown(f"""
        <div class="metric-card">
            <h3>🏆 Top Category</h3>
            <div class="number" style="font-size: 1.2rem; color: #60a5fa;">{top_category}</div>
            <div class="subtitle">Most resolved</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Calculate average resolution time (mock calculation)
        avg_resolution_days = 2.3
        st.markdown(f"""
        <div class="metric-card recent-feedback">
            <h3>⏱️ Avg Resolution</h3>
            <div class="number" style="font-size: 1.5rem;">{avg_resolution_days}</div>
            <div class="subtitle">Days to resolve</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        category_filter = st.selectbox("Filter by Category", ["All"] + list(categories.keys()))
    with col2:
        date_filter = st.selectbox("Date Range", ["All Time", "Last 7 days", "Last 30 days", "Last 90 days"])
    
    # Apply filters
    filtered_resolved = resolved_feedback
    if category_filter != "All":
        filtered_resolved = [f for f in filtered_resolved if f.get('category') == category_filter]
    
    st.info(f"📊 Showing {len(filtered_resolved)} resolved issues")
    
    # Display resolved issues
    for feedback in filtered_resolved[:20]:  # Show latest 20
        with st.expander(f"✅ {feedback['title']} • Resolved on {feedback.get('resolved_at', feedback['updated_at'])[:10]}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("**📝 Original Issue:**")
                st.markdown(f"""
                <div class="info-box blue">
                    {feedback['description']}
                </div>
                """, unsafe_allow_html=True)
                
                if feedback.get('official_response'):
                    st.markdown("**📧 Resolution Details:**")
                    st.markdown(f"""
                    <div class="info-box green">
                        {feedback['official_response']}
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("**📊 Resolution Summary:**")
                st.markdown(f"""
                <div class="metric-card" style="text-align: left; font-size: 0.9rem;">
                    <strong>👤 Citizen:</strong> {feedback['name']}<br>
                    <strong>📂 Category:</strong> {feedback.get('category', 'N/A')}<br>
                    <strong>🎯 Severity:</strong> {feedback.get('severity', 'N/A')}<br>
                    <strong>📍 Location:</strong> {feedback.get('location_detail', 'N/A')}<br>
                    <strong>📅 Submitted:</strong> {feedback['created_at'][:10]}<br>
                    <strong>✅ Resolved:</strong> {feedback.get('resolved_at', feedback['updated_at'])[:10]}
                </div>
                """, unsafe_allow_html=True)

def render_analytics_insights():
    """Render analytics and insights"""
    st.markdown("### 📈 Analytics & AI Insights")
    st.markdown("Comprehensive analysis of civic feedback trends and patterns")
    
    # Get comprehensive statistics
    stats = db.get_feedback_stats()
    trends = db.get_trend_data(30)
    
    # Key performance indicators
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card total-feedback">
            <h3>📊 Total Feedback</h3>
            <div class="number">{stats['total_feedback']}</div>
            <div class="subtitle">All time</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card resolution-rate">
            <h3>✅ Resolution Rate</h3>
            <div class="number">{stats['resolution_rate']}%</div>
            <div class="subtitle">Issues resolved</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card recent-feedback">
            <h3>⏱️ Avg Response</h3>
            <div class="number">{stats['avg_resolution_hours']:.1f}h</div>
            <div class="subtitle">Resolution time</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        citizen_satisfaction = 4.2
        st.markdown(f"""
        <div class="metric-card">
            <h3>😊 Satisfaction</h3>
            <div class="number" style="color: #4ade80;">{citizen_satisfaction}/5</div>
            <div class="subtitle">Citizen rating</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">📈 Daily Feedback Trends</h3>', unsafe_allow_html=True)
        
        if trends:
            dates = [trend['date'] for trend in trends]
            counts = [trend['count'] for trend in trends]
            resolved_counts = [trend['resolved'] for trend in trends]
            
            fig_trends = go.Figure()
            fig_trends.add_trace(go.Scatter(
                x=dates, y=counts, name='Submitted',
                line=dict(color='#3b82f6', width=3),
                mode='lines+markers'
            ))
            fig_trends.add_trace(go.Scatter(
                x=dates, y=resolved_counts, name='Resolved',
                line=dict(color='#10b981', width=3),
                mode='lines+markers'
            ))
            
            fig_trends.update_layout(
                xaxis_title="Date",
                yaxis_title="Number of Issues",
                font=dict(color='#ffffff'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(font=dict(color='#ffffff'))
            )
            st.plotly_chart(fig_trends, use_container_width=True)
        else:
            st.info("No trend data available.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">🎯 Category Performance</h3>', unsafe_allow_html=True)
        
        if stats['category_stats']:
            categories = list(stats['category_stats'].keys())
            values = list(stats['category_stats'].values())
            
            fig_performance = go.Figure(data=[
                go.Bar(
                    x=categories,
                    y=values,
                    marker_color='#3b82f6',
                    text=values,
                    textposition='auto',
                    textfont=dict(color='white', size=12)
                )
            ])
            
            fig_performance.update_layout(
                xaxis_title="Category",
                yaxis_title="Number of Issues",
                font=dict(color='#ffffff'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(tickfont=dict(color='#ffffff')),
                yaxis=dict(tickfont=dict(color='#ffffff')),
                margin=dict(t=20, b=40, l=40, r=20)
            )
            st.plotly_chart(fig_performance, use_container_width=True)
        else:
            st.info("No category data available.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # AI-Generated Weekly Summary
    st.markdown("### 🤖 AI-Generated Weekly Summary")
    
    with st.spinner("Generating AI summary..."):
        all_feedback = db.get_all_feedback()
        recent_feedback = [f for f in all_feedback if 
                          (datetime.now() - datetime.fromisoformat(f['created_at'])).days <= 7]
        summary = ai_processor.generate_weekly_summary(recent_feedback)
    
    st.markdown(f"""
    <div class="info-box blue">
        {summary}
    </div>
    """, unsafe_allow_html=True)
    
    # Government Performance Metrics
    st.markdown("### 🏛️ Government Performance Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-box green">
            <strong>Response Rate</strong><br>
            96% of issues receive response within 24h<br>
            <small>Target: ≥ 90%</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-box blue">
            <strong>Department Efficiency</strong><br>
            Traffic: 2.1 days avg<br>
            Sanitation: 1.8 days avg<br>
            Infrastructure: 3.2 days avg
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-box yellow">
            <strong>Citizen Engagement</strong><br>
            15% increase in feedback submissions<br>
            <small>Compared to last month</small>
        </div>
        """, unsafe_allow_html=True)



def render_spam_moderation(user: dict):
    """Render spam and moderation interface"""
    st.markdown("### 🚨 Spam & Content Moderation")
    st.markdown("AI-powered spam detection and content review")
    
    # Get potentially spam feedback
    all_feedback = db.get_all_feedback()
    spam_candidates = [f for f in all_feedback if f.get('spam_confidence', 0) > 0.3]
    spam_candidates.sort(key=lambda x: x.get('spam_confidence', 0), reverse=True)
    
    if not spam_candidates:
        st.success("🎉 No potential spam detected! All feedback appears legitimate.")
        return
    
    # Spam statistics
    col1, col2, col3 = st.columns(3)
    
    high_spam = len([f for f in spam_candidates if f.get('spam_confidence', 0) > 0.7])
    medium_spam = len([f for f in spam_candidates if 0.5 <= f.get('spam_confidence', 0) <= 0.7])
    low_spam = len([f for f in spam_candidates if 0.3 <= f.get('spam_confidence', 0) < 0.5])
    
    with col1:
        st.markdown(f"""
        <div class="metric-card high-priority">
            <h3>🚨 High Risk</h3>
            <div class="number">{high_spam}</div>
            <div class="subtitle">Confidence > 70%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>⚠️ Medium Risk</h3>
            <div class="number" style="color: #fbbf24;">{medium_spam}</div>
            <div class="subtitle">Confidence 50-70%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card recent-feedback">
            <h3>ℹ️ Low Risk</h3>
            <div class="number">{low_spam}</div>
            <div class="subtitle">Confidence 30-50%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.info(f"📊 Reviewing {len(spam_candidates)} potentially problematic submissions")
    
    # Review interface
    for feedback in spam_candidates:
        spam_score = feedback.get('spam_confidence', 0)
        risk_level = "High" if spam_score > 0.7 else "Medium" if spam_score > 0.5 else "Low"
        risk_color = "red" if risk_level == "High" else "yellow" if risk_level == "Medium" else "blue"
        
        with st.expander(f"🚨 {risk_level} Risk ({spam_score:.1%}) • {feedback['title']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("**📝 Submitted Content:**")
                st.markdown(f"""
                <div class="info-box {risk_color}">
                    <strong>Title:</strong> {feedback['title']}<br>
                    <strong>Description:</strong> {feedback['description']}
                </div>
                """, unsafe_allow_html=True)
                
                # AI spam analysis
                st.markdown("**🤖 AI Analysis:**")
                spam_reason = "Content appears to have characteristics of spam or inappropriate content based on language patterns, coherence, and relevance to civic issues."
                st.markdown(f"""
                <div class="info-box blue">
                    <strong>Spam Confidence:</strong> {spam_score:.1%}<br>
                    <strong>Analysis:</strong> {spam_reason}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("**📊 Submission Details:**")
                st.markdown(f"""
                <div class="metric-card" style="text-align: left; font-size: 0.9rem;">
                    <strong>👤 User:</strong> {feedback['name']}<br>
                    <strong>📧 Email:</strong> {feedback.get('email', 'N/A')}<br>
                    <strong>📍 Location:</strong> {feedback.get('location_detail', 'N/A')}<br>
                    <strong>📅 Submitted:</strong> {feedback['created_at'][:10]}<br>
                    <strong>🎯 Category:</strong> {feedback.get('category', 'N/A')}<br>
                    <strong>📈 Status:</strong> {feedback['status']}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("**⚖️ Moderation Action:**")
                
                col1_action, col2_action = st.columns(2)
                with col1_action:
                    if st.button(f"✅ Approve", key=f"approve_{feedback['feedback_id']}"):
                        # Update spam confidence to 0
                        db.update_feedback(
                            feedback['feedback_id'],
                            {'spam_confidence': 0.0},
                            user['user_id']
                        )
                        st.success("Feedback approved!")
                        st.rerun()
                     
                
                with col2_action:
                    if st.button(f"❌ Reject", key=f"reject_{feedback['feedback_id']}"):
                        # Update status to rejected
                        db.update_feedback(
                            feedback['feedback_id'],
                            {'status': 'Rejected', 'official_response': 'Content flagged as inappropriate or spam.'},
                            user['user_id']
                        )
                        db.update_feedback(
                            feedback['feedback_id'],
                            {'spam_confidence': 0.0},
                            user['user_id']
                        )
                        st.success("Feedback rejected!")
                        st.rerun()

if __name__ == "__main__":
    main()

# Footer
st.markdown("---")
st.markdown("""
<div class="footer">
    <div class="footer-title">🏛️ Civic Feedback & Governance Platform</div>
    <div class="footer-subtitle">
        AI-Powered Citizen Engagement • Built for HackTheAI 2024 • 
        Transforming government-citizen communication through intelligent technology
    </div>
</div>
""", unsafe_allow_html=True)