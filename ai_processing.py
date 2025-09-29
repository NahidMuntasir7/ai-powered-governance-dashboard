import google.generativeai as genai
import os
import json
import re
from typing import Dict, List, Optional, Tuple
import streamlit as st
from datetime import datetime

class EnhancedAIProcessor:
    def __init__(self, api_key: str = None):
        """Initialize AI processor with Google Gemini API"""
        self.api_available = False
        self.model = None
        
        if api_key:
            try:
                genai.configure(api_key=api_key)
                # Use the correct model name: gemini-1.5-flash
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                self.api_available = True
            except Exception as e:
                st.warning(f"⚠️ Google API setup failed: {str(e)}. Using fallback methods.")
                self.api_available = False
    
    def categorize_feedback(self, title: str, description: str) -> Tuple[str, float]:
        """Categorize feedback with confidence score"""
        text = f"Title: {title}\nDescription: {description}"
        
        if self.api_available and self.model:
            prompt = f"""
            Analyze the following civic feedback and categorize it into ONE of these categories:
            - Traffic (roads, signals, parking, transportation)
            - Sanitation (waste, garbage, cleaning, hygiene)
            - Safety (crime, security, dangerous areas, violence)
            - Water (water supply, leaks, quality, drainage)
            - Electricity (power outages, lines, transformers)
            - Infrastructure (buildings, bridges, streetlights, maintenance)
            - Other (anything that doesn't fit above categories)
            
            Feedback: "{text}"
            
            Return ONLY a JSON object with:
            {{"category": "CategoryName", "confidence": 0.95}}
            
            The confidence should be between 0.0 and 1.0.
            """
            
            try:
                response = self.model.generate_content(prompt)
                result = self._parse_json_response(response.text)
                
                if result and 'category' in result:
                    category = result['category']
                    confidence = float(result.get('confidence', 0.8))
                    
                    # Validate category
                    valid_categories = ['Traffic', 'Sanitation', 'Safety', 'Water', 'Electricity', 'Infrastructure', 'Other']
                    if category in valid_categories:
                        return category, confidence
            except Exception as e:
                st.warning(f"AI categorization failed: {str(e)}")
        
        # Fallback categorization
        return self._fallback_categorize(text), 0.6
    
    def detect_severity(self, title: str, description: str) -> Tuple[str, float]:
        """Detect severity level with confidence score"""
        text = f"Title: {title}\nDescription: {description}"
        
        if self.api_available and self.model:
            prompt = f"""
            Analyze the following civic feedback and determine the severity level:
            
            - High: Immediate danger, health hazard, major infrastructure failure, emergency situations
            - Medium: Significant inconvenience, moderate problems affecting daily life
            - Low: Minor issues, cosmetic problems, routine maintenance needs
            
            Feedback: "{text}"
            
            Return ONLY a JSON object with:
            {{"severity": "High/Medium/Low", "confidence": 0.95, "reasoning": "brief explanation"}}
            """
            
            try:
                response = self.model.generate_content(prompt)
                result = self._parse_json_response(response.text)
                
                if result and 'severity' in result:
                    severity = result['severity']
                    confidence = float(result.get('confidence', 0.8))
                    
                    if severity in ['High', 'Medium', 'Low']:
                        return severity, confidence
            except Exception as e:
                st.warning(f"AI severity detection failed: {str(e)}")
        
        # Fallback severity detection
        return self._fallback_severity(text), 0.6
    
    def detect_spam(self, title: str, description: str, user_history: int = 0) -> Tuple[float, str]:
        """Detect spam with confidence score and reasoning"""
        text = f"Title: {title}\nDescription: {description}"
        
        if self.api_available and self.model:
            prompt = f"""
            Analyze this civic feedback for spam/fake content. Consider:
            - Relevance to civic issues
            - Coherence and logical content
            - Appropriate language and tone
            - Realistic problem description
            - User has submitted {user_history} feedback items before
            
            Feedback: "{text}"
            
            Return ONLY a JSON object with:
            {{"spam_score": 0.15, "reasoning": "brief explanation", "is_spam": false}}
            
            spam_score: 0.0 (definitely not spam) to 1.0 (definitely spam)
            is_spam: true if spam_score > 0.7
            """
            
            try:
                response = self.model.generate_content(prompt)
                result = self._parse_json_response(response.text)
                
                if result and 'spam_score' in result:
                    spam_score = float(result['spam_score'])
                    reasoning = result.get('reasoning', 'AI analysis completed')
                    return spam_score, reasoning
            except Exception as e:
                st.warning(f"AI spam detection failed: {str(e)}")
        
        # Fallback spam detection
        return self._fallback_spam_detection(text), "Fallback analysis"
    
    def generate_ai_response(self, title: str, description: str, category: str, severity: str) -> str:
        """Generate AI intermediate response"""
        if self.api_available and self.model:
            prompt = f"""
            A citizen has submitted this {severity.lower()} priority {category.lower()} feedback:
            
            Title: {title}
            Description: {description}
            
            Generate a professional, empathetic AI response that:
            1. Acknowledges the issue
            2. Provides immediate guidance or next steps
            3. Sets appropriate expectations
            4. Maintains a helpful, official tone
            5. Is 2-3 sentences maximum
            
            Do not make specific promises about timeline unless it's emergency.
            """
            
            try:
                response = self.model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                st.warning(f"AI response generation failed: {str(e)}")
        
        # Fallback response
        return self._fallback_ai_response(category, severity)
    
    def generate_action_plan(self, title: str, description: str, category: str, severity: str) -> str:
        """Generate action plan for administrators"""
        if self.api_available and self.model:
            prompt = f"""
            Create an action plan for this {severity.lower()} priority {category.lower()} issue:
            
            Title: {title}
            Description: {description}
            
            Provide a structured action plan with:
            1. Immediate actions (within 24 hours)
            2. Required resources and personnel
            3. Timeline estimate
            4. Responsible department
            5. Follow-up steps
            
            Keep it practical and specific. Max 200 words.
            """
            
            try:
                response = self.model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                st.warning(f"AI action plan generation failed: {str(e)}")
        
        # Fallback action plan
        return self._fallback_action_plan(category, severity)
    
    def calculate_priority_score(self, severity: str, category: str, description: str, 
                               user_history: int = 0, location_frequency: int = 0) -> float:
        """Calculate priority score based on multiple factors"""
        base_scores = {
            'High': 0.8,
            'Medium': 0.5,
            'Low': 0.2
        }
        
        category_multipliers = {
            'Safety': 1.2,
            'Water': 1.1,
            'Electricity': 1.1,
            'Traffic': 1.0,
            'Sanitation': 0.9,
            'Infrastructure': 0.8,
            'Other': 0.7
        }
        
        score = base_scores.get(severity, 0.3)
        score *= category_multipliers.get(category, 1.0)
        
        # Keyword urgency boost
        urgent_keywords = ['emergency', 'urgent', 'immediate', 'dangerous', 'broken', 'not working', 'flooding']
        description_lower = description.lower()
        urgency_boost = sum(0.1 for keyword in urgent_keywords if keyword in description_lower)
        score += min(urgency_boost, 0.3)
        
        # Location frequency factor (higher frequency = higher priority)
        location_factor = min(location_frequency * 0.05, 0.2)
        score += location_factor
        
        # User history factor (prevent spam but don't penalize active users too much)
        if user_history > 10:
            score *= 0.95
        
        return min(score, 1.0)
    
    def generate_weekly_summary(self, feedback_data: List[Dict]) -> str:
        """Generate weekly summary report"""
        if not feedback_data:
            return "No feedback data available for this period."
        
        if self.api_available and self.model:
            # Prepare data summary
            total_issues = len(feedback_data)
            categories = {}
            severities = {}
            statuses = {}
            
            for feedback in feedback_data:
                cat = feedback.get('category', 'Unknown')
                sev = feedback.get('severity', 'Unknown')
                stat = feedback.get('status', 'Unknown')
                
                categories[cat] = categories.get(cat, 0) + 1
                severities[sev] = severities.get(sev, 0) + 1
                statuses[stat] = statuses.get(stat, 0) + 1
            
            prompt = f"""
            Generate an executive summary for this week's civic feedback:
            
            Total Issues: {total_issues}
            Categories: {categories}
            Severity Levels: {severities}
            Status Distribution: {statuses}
            
            Provide insights on:
            1. Main areas of concern
            2. Priority trends
            3. Resolution performance
            4. Recommended actions
            
            Keep it professional and actionable. Max 300 words.
            """
            
            try:
                response = self.model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                st.warning(f"AI summary generation failed: {str(e)}")
        
        # Fallback summary
        return self._fallback_weekly_summary(feedback_data)
    
    def generate_insights(self, stats: Dict) -> str:
        """Generate insights from statistics"""
        if self.api_available and self.model:
            prompt = f"""
            Analyze these civic feedback statistics and provide insights:
            
            {json.dumps(stats, indent=2)}
            
            Provide:
            1. Key trends and patterns
            2. Areas needing attention
            3. Performance indicators
            4. Actionable recommendations
            
            Keep it concise and executive-level. Max 250 words.
            """
            
            try:
                response = self.model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                st.warning(f"AI insights generation failed: {str(e)}")
        
        # Fallback insights
        return self._fallback_insights(stats)
    
    # Helper methods
    def _parse_json_response(self, text: str) -> Optional[Dict]:
        """Parse JSON from AI response"""
        try:
            # Extract JSON from text
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
        except:
            pass
        return None
    
    def _fallback_categorize(self, text: str) -> str:
        """Fallback categorization using keywords"""
        text_lower = text.lower()
        
        categories = {
            'Traffic': ['traffic', 'road', 'car', 'bus', 'signal', 'parking', 'highway', 'street', 'vehicle', 'transportation'],
            'Sanitation': ['garbage', 'waste', 'trash', 'clean', 'dirty', 'smell', 'sanitation', 'litter', 'dump'],
            'Safety': ['crime', 'police', 'safety', 'security', 'theft', 'violence', 'dangerous', 'unsafe', 'attack'],
            'Water': ['water', 'pipe', 'supply', 'leak', 'flooding', 'sewage', 'drainage', 'tap', 'well'],
            'Electricity': ['electricity', 'power', 'light', 'outage', 'blackout', 'transformer', 'electrical', 'cable'],
            'Infrastructure': ['building', 'bridge', 'road', 'sidewalk', 'streetlight', 'maintenance', 'repair', 'construction']
        }
        
        scores = {}
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                scores[category] = score
        
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        return 'Other'
    
    def _fallback_severity(self, text: str) -> str:
        """Fallback severity detection"""
        text_lower = text.lower()
        
        high_keywords = ['emergency', 'urgent', 'immediate', 'danger', 'critical', 'broken', 'not working', 'flooding', 'fire']
        medium_keywords = ['problem', 'issue', 'concern', 'repair', 'damaged', 'inconvenience', 'affecting']
        
        high_score = sum(1 for keyword in high_keywords if keyword in text_lower)
        medium_score = sum(1 for keyword in medium_keywords if keyword in text_lower)
        
        if high_score > 0:
            return 'High'
        elif medium_score > 0:
            return 'Medium'
        return 'Low'
    
    def _fallback_spam_detection(self, text: str) -> float:
        """Fallback spam detection"""
        spam_indicators = 0
        text_lower = text.lower()
        
        # Check for spam patterns
        if len(text) < 10:
            spam_indicators += 0.3
        if text.count('!') > 3:
            spam_indicators += 0.2
        if any(spam_word in text_lower for spam_word in ['free', 'money', 'win', 'click', 'buy']):
            spam_indicators += 0.4
        if text.isupper():
            spam_indicators += 0.2
        
        return min(spam_indicators, 1.0)
    
    def _fallback_ai_response(self, category: str, severity: str) -> str:
        """Fallback AI response generation"""
        responses = {
            ('Traffic', 'High'): "Thank you for reporting this urgent traffic issue. This has been flagged for immediate attention by our transportation department. Please avoid the area if possible and use alternate routes for safety.",
            ('Traffic', 'Medium'): "Your traffic concern has been received and will be addressed by our transportation team. We expect to review this within 2-3 business days.",
            ('Traffic', 'Low'): "Thank you for your traffic feedback. This will be included in our routine maintenance planning and review cycle.",
            
            ('Safety', 'High'): "This safety issue has been marked as high priority. If there is immediate danger, please contact emergency services. Our public safety team will investigate promptly.",
            ('Safety', 'Medium'): "Your safety concern is important to us. Our team will review this issue and take appropriate action within 24-48 hours.",
            ('Safety', 'Low'): "Thank you for reporting this safety concern. We will include this in our regular safety assessments and patrol considerations.",
            
            ('Water', 'High'): "This water issue has been escalated to our utilities emergency team. If you have no water access, please contact our emergency hotline immediately.",
            ('Water', 'Medium'): "Your water system concern has been received. Our utilities team will investigate and respond within 1-2 business days.",
            ('Water', 'Low'): "Thank you for the water system feedback. This will be reviewed in our next maintenance cycle.",
            
            ('Sanitation', 'High'): "This sanitation issue requires immediate attention. Our waste management team has been notified and will address this urgently.",
            ('Sanitation', 'Medium'): "Your sanitation concern has been forwarded to our waste management department for prompt action.",
            ('Sanitation', 'Low'): "Thank you for your sanitation feedback. This will be included in our regular collection and maintenance schedule.",
            
            ('Electricity', 'High'): "This electrical issue has been reported to our power utility emergency team. If there are safety concerns, please maintain distance and contact our emergency line.",
            ('Electricity', 'Medium'): "Your electrical system report has been received. Our power utilities team will investigate within 24 hours.",
            ('Electricity', 'Low'): "Thank you for the electrical system feedback. This will be reviewed in our routine maintenance planning.",
        }
        
        response = responses.get((category, severity))
        if response:
            return response
        
        return f"Thank you for your {category.lower()} feedback. This {severity.lower()} priority issue has been received and will be reviewed by the appropriate department."
    
    def _fallback_action_plan(self, category: str, severity: str) -> str:
        """Fallback action plan generation"""
        timelines = {'High': '24 hours', 'Medium': '2-3 days', 'Low': '1-2 weeks'}
        departments = {
            'Traffic': 'Transportation Department',
            'Safety': 'Public Safety Department',
            'Water': 'Water Utilities Department',
            'Sanitation': 'Waste Management Department',
            'Electricity': 'Power Utilities Department',
            'Infrastructure': 'Public Works Department'
        }
        
        timeline = timelines.get(severity, '1 week')
        department = departments.get(category, 'General Services Department')
        
        return f"""
**ACTION PLAN - {severity} Priority {category} Issue**

**Immediate Actions:**
• Assign to {department}
• Conduct field assessment within {timeline}
• Contact citizen for additional details if needed

**Resources Required:**
• Field inspection team
• {category.lower()} repair equipment and materials
• Safety equipment and protocols

**Timeline:** {timeline} for initial response and assessment

**Responsible Department:** {department}

**Follow-up Steps:**
• Provide status update to citizen within 48 hours
• Monitor progress until completion
• Final resolution confirmation and closure
        """
    
    def _fallback_weekly_summary(self, feedback_data: List[Dict]) -> str:
        """Fallback weekly summary"""
        total = len(feedback_data)
        if total == 0:
            return "No feedback received this week."
        
        categories = {}
        severities = {}
        resolved = 0
        
        for feedback in feedback_data:
            cat = feedback.get('category', 'Unknown')
            sev = feedback.get('severity', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
            severities[sev] = severities.get(sev, 0) + 1
            if feedback.get('status') == 'Resolved':
                resolved += 1
        
        top_category = max(categories.items(), key=lambda x: x[1])[0] if categories else 'None'
        resolution_rate = round((resolved / total) * 100, 1)
        
        return f"""
**WEEKLY CIVIC FEEDBACK SUMMARY**

**Overview:**
• Total issues reported: {total}
• Issues resolved: {resolved} ({resolution_rate}% resolution rate)
• Top concern category: {top_category} ({categories.get(top_category, 0)} reports)

**Category Distribution:**
{chr(10).join([f'• {cat}: {count}' for cat, count in categories.items()])}

**Severity Breakdown:**
{chr(10).join([f'• {sev}: {count}' for sev, count in severities.items()])}

**Key Insights:**
• {top_category} represents the primary citizen concern this week
• Resolution rate of {resolution_rate}% {'exceeds' if resolution_rate > 70 else 'needs improvement from'} target performance
• Continued monitoring recommended for {top_category.lower()} issues

**Recommendations:**
• Focus additional resources on {top_category.lower()} department
• Review response protocols for {max(severities.items(), key=lambda x: x[1])[0].lower() if severities else 'all'} priority issues
• Enhance citizen communication for transparency
        """
    
    def _fallback_insights(self, stats: Dict) -> str:
        """Fallback insights generation"""
        total = stats.get('total_feedback', 0)
        resolution_rate = stats.get('resolution_rate', 0)
        categories = stats.get('category_stats', {})
        
        if total == 0:
            return "Insufficient data for meaningful insights."
        
        top_category = max(categories.items(), key=lambda x: x[1])[0] if categories else 'Unknown'
        
        return f"""
**CIVIC FEEDBACK INSIGHTS**

**Performance Overview:**
• Total feedback processed: {total}
• Current resolution rate: {resolution_rate}%
• Primary concern area: {top_category}

**Key Trends:**
• {top_category} issues represent the highest volume of citizen concerns
• Resolution performance {'exceeds standards' if resolution_rate > 75 else 'requires attention'}
• Citizen engagement remains active with consistent feedback submission

**Strategic Recommendations:**
• Prioritize resource allocation to {top_category.lower()} department
• Implement proactive measures to prevent recurring {top_category.lower()} issues
• Enhance response time protocols for high-priority items
• Strengthen citizen communication and transparency initiatives

**Action Items:**
• Review {top_category.lower()} operational procedures
• Establish performance metrics for response time improvement
• Consider preventive maintenance programs
• Develop citizen satisfaction measurement system
        """