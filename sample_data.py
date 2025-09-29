from database import DatabaseManager
from datetime import datetime, timedelta
import random

def create_sample_data():
    """Create comprehensive sample data for demonstration"""
    db = DatabaseManager()
    
    # Sample users
    sample_users = [
        {"name": "Ahmed Rahman", "email": "ahmed@email.com", "password": "password123", "role": "user", "location": "Dhanmondi", "phone": "01712345678"},
        {"name": "Fatima Khan", "email": "fatima@email.com", "password": "password123", "role": "user", "location": "Gulshan", "phone": "01812345679"},
        {"name": "Mohammad Ali", "email": "ali@email.com", "password": "password123", "role": "user", "location": "Uttara", "phone": "01912345680"},
        {"name": "Rashida Begum", "email": "rashida@email.com", "password": "password123", "role": "user", "location": "Mirpur", "phone": "01612345681"},
        {"name": "Karim Hassan", "email": "karim@email.com", "password": "password123", "role": "user", "location": "Wari", "phone": "01512345682"},
        {"name": "Shahana Akter", "email": "shahana@email.com", "password": "password123", "role": "user", "location": "Banani", "phone": "01412345683"},
        {"name": "Rafiq Ahmed", "email": "rafiq@email.com", "password": "password123", "role": "user", "location": "Mohammadpur", "phone": "01312345684"},
        {"name": "Nasir Uddin", "email": "nasir@email.com", "password": "password123", "role": "user", "location": "Tejgaon", "phone": "01212345685"},
        
        # Admin users
        {"name": "Admin User", "email": "admin@gov.bd", "password": "admin123", "role": "admin", "location": "Secretariat", "phone": "01700000001"},
        {"name": "Traffic Admin", "email": "traffic@gov.bd", "password": "admin123", "role": "admin", "location": "BRTA Office", "phone": "01700000002"},
    ]
    
    # Create users and store IDs
    user_ids = []
    for user_data in sample_users:
        try:
            user_id = db.create_user(**user_data)
            user_ids.append(user_id)
            print(f"Created user: {user_data['name']} (ID: {user_id})")
        except ValueError as e:
            print(f"User {user_data['email']} already exists, skipping...")
            # Get existing user ID
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users WHERE email = ?", (user_data['email'],))
            existing_user = cursor.fetchone()
            if existing_user:
                user_ids.append(existing_user[0])
            conn.close()
    
    # Sample feedback data
    sample_feedback = [
        {
            "title": "Broken Traffic Signal at Dhanmondi 27",
            "description": "The traffic signal at Dhanmondi 27 intersection has been malfunctioning for 3 days. It's causing major traffic jams and accidents. Please fix urgently.",
            "category": "Traffic",
            "severity": "High",
            "location_detail": "Dhanmondi 27 intersection, near Abahani Club"
        },
        {
            "title": "Garbage Collection Not Regular",
            "description": "Garbage has not been collected from our street for over a week. The smell is terrible and it's becoming a health hazard.",
            "category": "Sanitation", 
            "severity": "Medium",
            "location_detail": "Road 15, House 25, Gulshan 1"
        },
        {
            "title": "Street Lights Not Working",
            "description": "Multiple street lights on our road have been out for months. It's very dangerous at night, especially for women and children.",
            "category": "Electricity",
            "severity": "High", 
            "location_detail": "Road 12, Block C, Uttara Sector 7"
        },
    ]
    
    # Submit feedback and create AI responses
    from ai_processing import EnhancedAIProcessor
    ai_processor = EnhancedAIProcessor()  # Will use fallback methods
    
    for i, feedback_data in enumerate(sample_feedback):
        if i < len(user_ids):
            user_id = user_ids[i % 8]  # Rotate through regular users
            
            # Submit feedback
            feedback_id = db.submit_feedback(
                user_id=user_id,
                title=feedback_data["title"],
                description=feedback_data["description"],
                category=feedback_data["category"],
                severity=feedback_data["severity"],
                location_detail=feedback_data["location_detail"]
            )
            
            # Generate AI response
            ai_response = ai_processor.generate_ai_response(
                title=feedback_data["title"],
                description=feedback_data["description"],
                category=feedback_data["category"],
                severity=feedback_data["severity"]
            )
            
            # Generate action plan
            action_plan = ai_processor.generate_action_plan(
                title=feedback_data["title"],
                description=feedback_data["description"],
                category=feedback_data["category"],
                severity=feedback_data["severity"]
            )
            
            # Calculate priority score
            priority_score = ai_processor.calculate_priority_score(
                severity=feedback_data["severity"],
                category=feedback_data["category"],
                description=feedback_data["description"]
            )
            
            # Spam detection
            spam_score, spam_reason = ai_processor.detect_spam(
                title=feedback_data["title"],
                description=feedback_data["description"]
            )
            
            # Update feedback with AI results
            db.update_feedback(
                feedback_id=feedback_id,
                updates={
                    'ai_response': ai_response,
                    'priority_score': priority_score,
                    'spam_confidence': spam_score
                },
                changed_by=user_id
            )
            
            # Add some feedback as resolved
            if i % 4 == 0:  # Mark every 4th feedback as resolved
                db.update_feedback(
                    feedback_id=feedback_id,
                    updates={
                        'status': 'Resolved',
                        'official_response': f"This {feedback_data['category'].lower()} issue has been resolved. Thank you for your patience."
                    },
                    changed_by=user_ids[-1]  # Admin user
                )
            elif i % 3 == 0:  # Mark every 3rd as in progress
                db.update_feedback(
                    feedback_id=feedback_id,
                    updates={
                        'status': 'In Progress',
                        'official_response': f"We are working on this {feedback_data['category'].lower()} issue. Expected completion in 2-3 days."
                    },
                    changed_by=user_ids[-1]  # Admin user
                )
            
            # Create notifications
            db.add_notification(
                user_id=user_id,
                title="Feedback Submitted",
                message=f"Your feedback '{feedback_data['title']}' has been submitted successfully.",
                feedback_id=feedback_id,
                type="success"
            )
            
            # Notify admins for high priority issues
            if feedback_data["severity"] == "High":
                for admin_id in user_ids[-2:]:  # Last 2 users are admins
                    db.add_notification(
                        user_id=admin_id,
                        title="High Priority Issue",
                        message=f"New {feedback_data['category']} issue requires immediate attention: {feedback_data['title']}",
                        feedback_id=feedback_id,
                        type="warning"
                    )
            
            print(f"Created feedback: {feedback_data['title']} (ID: {feedback_id})")
    
    print(f"\n✅ Sample data created successfully!")
    print(f"👥 Users created: {len(user_ids)}")
    print(f"📝 Feedback items created: {len(sample_feedback)}")
    print(f"🔐 Admin credentials: admin@gov.bd / admin123")
    print(f"👤 User credentials: ahmed@email.com / password123")

if __name__ == "__main__":
    create_sample_data()