import streamlit as st
from typing import List, Dict
from database import DatabaseManager
from datetime import datetime

class NotificationManager:
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def create_notification(self, user_id: int, title: str, message: str, 
                           feedback_id: int = None, type: str = 'info'):
        """Create a new notification"""
        return self.db.add_notification(user_id, title, message, feedback_id, type)
    
    def notify_feedback_submitted(self, user_id: int, feedback_id: int, title: str):
        """Notify user when feedback is submitted"""
        self.create_notification(
            user_id=user_id,
            title="Feedback Submitted",
            message=f"Your feedback '{title}' has been submitted and is being processed.",
            feedback_id=feedback_id,
            type="success"
        )
    
    def notify_status_change(self, user_id: int, feedback_id: int, 
                           title: str, old_status: str, new_status: str):
        """Notify user when feedback status changes"""
        status_messages = {
            'In Progress': f"Good news! Work has begun on your issue '{title}'.",
            'Resolved': f"Your issue '{title}' has been resolved. Thank you for your feedback!",
            'Rejected': f"Unfortunately, your feedback '{title}' could not be processed at this time."
        }
        
        message = status_messages.get(new_status, f"Status of your feedback '{title}' has been updated to {new_status}.")
        notification_type = 'success' if new_status == 'Resolved' else 'info'
        
        self.create_notification(
            user_id=user_id,
            title="Status Update",
            message=message,
            feedback_id=feedback_id,
            type=notification_type
        )
    
    def notify_admin_response(self, user_id: int, feedback_id: int, title: str):
        """Notify user when admin responds"""
        self.create_notification(
            user_id=user_id,
            title="Official Response",
            message=f"An official response has been added to your feedback '{title}'. Please check for details.",
            feedback_id=feedback_id,
            type="info"
        )
    
    def notify_admins_new_feedback(self, feedback_id: int, title: str, severity: str, category: str):
        """Notify all admins of new feedback"""
        # Get all admin users
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE role = 'admin' AND is_active = 1")
        admin_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # Create notifications for all admins
        notification_type = 'warning' if severity == 'High' else 'info'
        for admin_id in admin_ids:
            self.create_notification(
                user_id=admin_id,
                title=f"New {severity} Priority Issue",
                message=f"New {category} feedback: '{title}' requires attention.",
                feedback_id=feedback_id,
                type=notification_type
            )
    
    def render_notification_panel(self, user_id: int):
        """Render notification panel for user"""
        notifications = self.db.get_user_notifications(user_id)
        unread_count = len([n for n in notifications if not n['is_read']])
        
        # Notification header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### 🔔 Notifications")
        with col2:
            if unread_count > 0:
                if st.button(f"Mark All Read ({unread_count})", key="mark_all_read"):
                    self.db.mark_all_notifications_read(user_id)
                    st.rerun()
        
        if not notifications:
            st.info("No notifications yet.")
            return
        
        # Display notifications
        for notification in notifications[:10]:  # Show latest 10
            with st.container():
                # Notification styling based on type and read status
                type_colors = {
                    'success': 'green',
                    'warning': 'yellow', 
                    'error': 'red',
                    'info': 'blue'
                }
                
                color = type_colors.get(notification['type'], 'blue')
                read_style = "" if notification['is_read'] else "font-weight: bold;"
                
                st.markdown(f"""
                <div class="info-box {color}" style="{read_style}">
                    <strong>{notification['title']}</strong><br>
                    {notification['message']}<br>
                    <small>{self._format_datetime(notification['created_at'])}</small>
                </div>
                """, unsafe_allow_html=True)
                
                # Mark as read button for unread notifications
                if not notification['is_read']:
                    if st.button("✓ Mark Read", key=f"read_{notification['notification_id']}"):
                        self.db.mark_notification_read(notification['notification_id'], user_id)
                        st.rerun()
    
    def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications"""
        notifications = self.db.get_user_notifications(user_id, unread_only=True)
        return len(notifications)
    
    def _format_datetime(self, dt_string: str) -> str:
        """Format datetime string for display"""
        try:
            dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
            now = datetime.now()
            diff = now - dt
            
            if diff.days > 0:
                return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} hour{'s' if hours > 1 else ''} ago"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            else:
                return "Just now"
        except:
            return dt_string