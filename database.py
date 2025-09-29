import sqlite3
import datetime
from typing import List, Dict, Optional, Tuple
import hashlib
import secrets

class DatabaseManager:
    def __init__(self, db_name: str = "civic_governance.db"):
        """Initialize database connection and create tables"""
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_name)
    
    def init_database(self):
        """Create all necessary tables with enhanced schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table with authentication
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'admin')),
                location TEXT,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Enhanced feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT CHECK (category IN ('Traffic', 'Sanitation', 'Safety', 'Water', 'Electricity', 'Infrastructure', 'Other')),
                severity TEXT CHECK (severity IN ('High', 'Medium', 'Low')),
                status TEXT DEFAULT 'Pending' CHECK (status IN ('Pending', 'In Progress', 'Resolved', 'Rejected')),
                ai_response TEXT,
                official_response TEXT,
                spam_confidence REAL DEFAULT 0.0,
                priority_score REAL DEFAULT 0.0,
                location_detail TEXT,
                attachments TEXT,  -- JSON string for file paths
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                is_deleted BOOLEAN DEFAULT 0,
                is_public BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Notifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                feedback_id INTEGER,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                type TEXT CHECK (type IN ('info', 'success', 'warning', 'error')) DEFAULT 'info',
                is_read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (feedback_id) REFERENCES feedback (feedback_id)
            )
        ''')
        
        # Reports table for export logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                report_id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER NOT NULL,
                report_type TEXT NOT NULL,
                parameters TEXT,  -- JSON string for report parameters
                file_path TEXT,
                file_name TEXT,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (admin_id) REFERENCES users (user_id)
            )
        ''')
        
        # AI processing logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                feedback_id INTEGER NOT NULL,
                operation TEXT NOT NULL,  -- 'categorization', 'severity', 'spam_detection', etc.
                input_data TEXT,
                output_data TEXT,
                confidence_score REAL,
                processing_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (feedback_id) REFERENCES feedback (feedback_id)
            )
        ''')
        
        # Feedback history for tracking changes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback_history (
                history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                feedback_id INTEGER NOT NULL,
                changed_by INTEGER NOT NULL,
                field_name TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                change_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (feedback_id) REFERENCES feedback (feedback_id),
                FOREIGN KEY (changed_by) REFERENCES users (user_id)
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_status ON feedback(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_category ON feedback(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_severity ON feedback(severity)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_user ON feedback(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(is_read)')
        
        conn.commit()
        conn.close()
    
    # Authentication methods
    def hash_password(self, password: str) -> Tuple[str, str]:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return password_hash.hex(), salt
    
    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verify password against hash"""
        computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return computed_hash.hex() == password_hash
    
    def create_user(self, name: str, email: str, password: str, role: str = 'user', 
                   location: str = None, phone: str = None) -> int:
        """Create a new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT user_id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            raise ValueError("Email already exists")
        
        password_hash, salt = self.hash_password(password)
        
        cursor.execute(
            """INSERT INTO users (name, email, password_hash, salt, role, location, phone) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (name, email, password_hash, salt, role, location, phone)
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT user_id, name, email, password_hash, salt, role, location, phone, is_active 
               FROM users WHERE email = ?""",
            (email,)
        )
        user_data = cursor.fetchone()
        
        if user_data and user_data[8]:  # is_active check
            if self.verify_password(password, user_data[3], user_data[4]):
                # Update last login
                cursor.execute(
                    "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?",
                    (user_data[0],)
                )
                conn.commit()
                conn.close()
                
                return {
                    'user_id': user_data[0],
                    'name': user_data[1],
                    'email': user_data[2],
                    'role': user_data[5],
                    'location': user_data[6],
                    'phone': user_data[7]
                }
        
        conn.close()
        return None
    
    # Feedback management
    def submit_feedback(self, user_id: int, title: str, description: str, 
                       category: str = None, severity: str = None, 
                       location_detail: str = None) -> int:
        """Submit new feedback"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO feedback (user_id, title, description, category, severity, location_detail) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, title, description, category, severity, location_detail)
        )
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return feedback_id
    
    def update_feedback(self, feedback_id: int, updates: Dict, changed_by: int) -> bool:
        """Update feedback with history tracking"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get current values for history
        cursor.execute("SELECT * FROM feedback WHERE feedback_id = ?", (feedback_id,))
        current_data = cursor.fetchone()
        if not current_data:
            conn.close()
            return False
        
        # Build update query
        set_clause = []
        values = []
        for field, value in updates.items():
            if field in ['status', 'official_response', 'ai_response', 'priority_score', 'spam_confidence']:
                set_clause.append(f"{field} = ?")
                values.append(value)
                
                # Log history
                cursor.execute(
                    """INSERT INTO feedback_history (feedback_id, changed_by, field_name, old_value, new_value) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (feedback_id, changed_by, field, str(current_data[6]), str(value))  # Adjust index based on schema
                )
        
        if set_clause:
            set_clause.append("updated_at = CURRENT_TIMESTAMP")
            values.append(feedback_id)
            
            update_query = f"UPDATE feedback SET {', '.join(set_clause)} WHERE feedback_id = ?"
            cursor.execute(update_query, values)
            
            # Mark as resolved if status is resolved
            if updates.get('status') == 'Resolved':
                cursor.execute(
                    "UPDATE feedback SET resolved_at = CURRENT_TIMESTAMP WHERE feedback_id = ?",
                    (feedback_id,)
                )
        
        conn.commit()
        conn.close()
        return True
    
    def get_feedback_by_id(self, feedback_id: int) -> Optional[Dict]:
        """Get feedback by ID with user details"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT f.*, u.name, u.email, u.location as user_location, u.phone
               FROM feedback f
               JOIN users u ON f.user_id = u.user_id
               WHERE f.feedback_id = ? AND f.is_deleted = 0""",
            (feedback_id,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None
    
    def get_user_feedback(self, user_id: int) -> List[Dict]:
        """Get all feedback for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT * FROM feedback 
               WHERE user_id = ? AND is_deleted = 0 
               ORDER BY created_at DESC""",
            (user_id,)
        )
        
        columns = [desc[0] for desc in cursor.description]
        feedback_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return feedback_list
    
    def get_all_feedback(self, status: str = None, category: str = None, 
                        severity: str = None, include_deleted: bool = False) -> List[Dict]:
        """Get all feedback with optional filters"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        where_conditions = []
        params = []
        
        if not include_deleted:
            where_conditions.append("f.is_deleted = 0")
        
        if status:
            where_conditions.append("f.status = ?")
            params.append(status)
            
        if category:
            where_conditions.append("f.category = ?")
            params.append(category)
            
        if severity:
            where_conditions.append("f.severity = ?")
            params.append(severity)
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        query = f"""
        SELECT f.*, u.name, u.email, u.location as user_location, u.phone
        FROM feedback f
        JOIN users u ON f.user_id = u.user_id
        {where_clause}
        ORDER BY f.priority_score DESC, f.created_at DESC
        """
        
        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        feedback_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return feedback_list
    
    def soft_delete_feedback(self, feedback_id: int, user_id: int) -> bool:
        """Soft delete feedback (user can only delete their own)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE feedback SET is_deleted = 1 WHERE feedback_id = ? AND user_id = ?",
            (feedback_id, user_id)
        )
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    # Notifications
    def add_notification(self, user_id: int, title: str, message: str, 
                        feedback_id: int = None, type: str = 'info') -> int:
        """Add notification for user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO notifications (user_id, title, message, feedback_id, type) 
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, title, message, feedback_id, type)
        )
        
        notification_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return notification_id
    
    def get_user_notifications(self, user_id: int, unread_only: bool = False) -> List[Dict]:
        """Get notifications for user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        where_clause = "WHERE user_id = ?"
        params = [user_id]
        
        if unread_only:
            where_clause += " AND is_read = 0"
        
        cursor.execute(
            f"""SELECT * FROM notifications {where_clause} 
                ORDER BY created_at DESC LIMIT 50""",
            params
        )
        
        columns = [desc[0] for desc in cursor.description]
        notifications = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return notifications
    
    def mark_notification_read(self, notification_id: int, user_id: int) -> bool:
        """Mark notification as read"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE notifications SET is_read = 1 WHERE notification_id = ? AND user_id = ?",
            (notification_id, user_id)
        )
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def mark_all_notifications_read(self, user_id: int) -> bool:
        """Mark all notifications as read for user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE notifications SET is_read = 1 WHERE user_id = ?",
            (user_id,)
        )
        
        conn.commit()
        conn.close()
        return True
    
    # Analytics and reporting
    def get_feedback_stats(self, date_range: int = 30) -> Dict:
        """Get comprehensive feedback statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total feedback
        cursor.execute("SELECT COUNT(*) FROM feedback WHERE is_deleted = 0")
        total_feedback = cursor.fetchone()[0]
        
        # Recent feedback
        cursor.execute(
            """SELECT COUNT(*) FROM feedback 
               WHERE datetime(created_at) >= datetime('now', '-{} days') AND is_deleted = 0""".format(date_range)
        )
        recent_feedback = cursor.fetchone()[0]
        
        # Category distribution
        cursor.execute(
            """SELECT category, COUNT(*) FROM feedback 
               WHERE category IS NOT NULL AND is_deleted = 0 
               GROUP BY category"""
        )
        category_stats = dict(cursor.fetchall())
        
        # Severity distribution
        cursor.execute(
            """SELECT severity, COUNT(*) FROM feedback 
               WHERE severity IS NOT NULL AND is_deleted = 0 
               GROUP BY severity"""
        )
        severity_stats = dict(cursor.fetchall())
        
        # Status distribution
        cursor.execute(
            """SELECT status, COUNT(*) FROM feedback 
               WHERE is_deleted = 0 GROUP BY status"""
        )
        status_stats = dict(cursor.fetchall())
        
        # Resolution rate
        resolved_count = status_stats.get('Resolved', 0)
        resolution_rate = (resolved_count / total_feedback * 100) if total_feedback > 0 else 0
        
        # Average resolution time
        cursor.execute(
            """SELECT AVG(JULIANDAY(resolved_at) - JULIANDAY(created_at)) * 24 
               FROM feedback WHERE resolved_at IS NOT NULL"""
        )
        avg_resolution_hours = cursor.fetchone()[0] or 0
        
        # Spam statistics
        cursor.execute(
            """SELECT COUNT(*) FROM feedback 
               WHERE spam_confidence > 0.7 AND is_deleted = 0"""
        )
        potential_spam = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_feedback': total_feedback,
            'recent_feedback': recent_feedback,
            'category_stats': category_stats,
            'severity_stats': severity_stats,
            'status_stats': status_stats,
            'resolution_rate': round(resolution_rate, 1),
            'avg_resolution_hours': round(avg_resolution_hours, 1),
            'potential_spam': potential_spam
        }
    
    def get_trend_data(self, days: int = 30) -> List[Dict]:
        """Get daily feedback trends"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT DATE(created_at) as date, 
                      COUNT(*) as count,
                      COUNT(CASE WHEN status = 'Resolved' THEN 1 END) as resolved
               FROM feedback 
               WHERE datetime(created_at) >= datetime('now', '-{} days') AND is_deleted = 0
               GROUP BY DATE(created_at)
               ORDER BY date""".format(days)
        )
        
        columns = [desc[0] for desc in cursor.description]
        trends = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return trends
    
    def get_public_stats(self) -> Dict:
        """Get public statistics (no sensitive data)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Public feedback only
        cursor.execute(
            """SELECT 
                   COUNT(*) as total,
                   COUNT(CASE WHEN status = 'Resolved' THEN 1 END) as resolved,
                   COUNT(CASE WHEN status = 'In Progress' THEN 1 END) as in_progress,
                   COUNT(CASE WHEN status = 'Pending' THEN 1 END) as pending
               FROM feedback WHERE is_public = 1 AND is_deleted = 0"""
        )
        
        stats = cursor.fetchone()
        
        # Category distribution for public
        cursor.execute(
            """SELECT category, COUNT(*) FROM feedback 
               WHERE is_public = 1 AND is_deleted = 0 AND category IS NOT NULL
               GROUP BY category"""
        )
        category_distribution = dict(cursor.fetchall())
        
        # Weekly resolution trend
        cursor.execute(
            """SELECT 
                   strftime('%Y-%W', created_at) as week,
                   COUNT(*) as submitted,
                   COUNT(CASE WHEN status = 'Resolved' THEN 1 END) as resolved
               FROM feedback 
               WHERE is_public = 1 AND is_deleted = 0 
                     AND datetime(created_at) >= datetime('now', '-12 weeks')
               GROUP BY strftime('%Y-%W', created_at)
               ORDER BY week"""
        )
        
        weekly_trends = [dict(zip(['week', 'submitted', 'resolved'], row)) 
                        for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'total_issues': stats[0],
            'resolved_issues': stats[1],
            'in_progress_issues': stats[2],
            'pending_issues': stats[3],
            'resolution_rate': round((stats[1] / stats[0] * 100) if stats[0] > 0 else 0, 1),
            'category_distribution': category_distribution,
            'weekly_trends': weekly_trends
        }
    
    # Report generation support
    def log_report_generation(self, admin_id: int, report_type: str, 
                             parameters: str, file_path: str, file_name: str) -> int:
        """Log report generation"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO reports (admin_id, report_type, parameters, file_path, file_name) 
               VALUES (?, ?, ?, ?, ?)""",
            (admin_id, report_type, parameters, file_path, file_name)
        )
        
        report_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return report_id
    
    def get_user_count(self) -> int:
        """Get total user count"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_admin_count(self) -> int:
        """Get admin count"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin' AND is_active = 1")
        count = cursor.fetchone()[0]
        conn.close()
        return count