import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Optional
import streamlit as st

class ReportGenerator:
    def __init__(self, db):
        self.db = db
        self.reports_dir = "reports"
        self._ensure_reports_dir()
    
    def _ensure_reports_dir(self):
        """Ensure reports directory exists"""
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)
    
    def generate_csv_report(self, report_type: str, date_range: int = 30, 
                           filters: Dict = None) -> str:
        """Generate CSV report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{report_type}_{timestamp}.csv"
        filepath = os.path.join(self.reports_dir, filename)
        
        if report_type == "feedback_summary":
            data = self._get_feedback_data(date_range, filters)
            df = pd.DataFrame(data)
            
            # Clean and format data for CSV
            if not df.empty:
                df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
                if 'resolved_at' in df.columns:
                    df['resolved_at'] = pd.to_datetime(df['resolved_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
                
                # Remove sensitive data for export
                export_columns = [
                    'feedback_id', 'title', 'category', 'severity', 'status',
                    'location_detail', 'created_at', 'resolved_at', 'priority_score'
                ]
                df = df[[col for col in export_columns if col in df.columns]]
            
        elif report_type == "analytics_summary":
            stats = self.db.get_feedback_stats(date_range)
            df = pd.DataFrame([stats])
            
        elif report_type == "trend_analysis":
            trends = self.db.get_trend_data(date_range)
            df = pd.DataFrame(trends)
        
        else:
            raise ValueError(f"Unknown report type: {report_type}")
        
        # Save to CSV
        df.to_csv(filepath, index=False)
        return filepath
    
    def generate_detailed_report(self, admin_id: int, report_type: str, 
                               parameters: Dict) -> Dict:
        """Generate detailed report with charts and analysis"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_data = {
            'generated_at': datetime.now().isoformat(),
            'report_type': report_type,
            'parameters': parameters,
            'data': {}
        }
        
        date_range = parameters.get('date_range', 30)
        
        if report_type == "comprehensive_analysis":
            # Get all data
            feedback_data = self._get_feedback_data(date_range, parameters.get('filters'))
            stats = self.db.get_feedback_stats(date_range)
            trends = self.db.get_trend_data(date_range)
            
            report_data['data'] = {
                'summary_stats': stats,
                'trend_data': trends,
                'feedback_count': len(feedback_data),
                'analysis': self._generate_analysis(stats, trends)
            }
            
        # Log report generation
        self.db.log_report_generation(
            admin_id=admin_id,
            report_type=report_type,
            parameters=json.dumps(parameters),
            file_path="",
            file_name=f"{report_type}_{timestamp}.json"
        )
        
        return report_data
    
    def _get_feedback_data(self, date_range: int, filters: Dict = None) -> List[Dict]:
        """Get feedback data for reports"""
        return self.db.get_all_feedback()
    
    def _generate_analysis(self, stats: Dict, trends: List[Dict]) -> str:
        """Generate textual analysis"""
        total = stats.get('total_feedback', 0)
        resolution_rate = stats.get('resolution_rate', 0)
        categories = stats.get('category_stats', {})
        
        analysis = f"""
        **EXECUTIVE SUMMARY**
        
        Total Issues Processed: {total}
        Resolution Rate: {resolution_rate}%
        
        **KEY INSIGHTS:**
        """
        
        if categories:
            top_category = max(categories.items(), key=lambda x: x[1])[0]
            analysis += f"\n• Primary concern area: {top_category} ({categories[top_category]} reports)"
        
        analysis += f"\n• Resolution performance: {'Excellent' if resolution_rate > 80 else 'Good' if resolution_rate > 60 else 'Needs Improvement'}"
        
        return analysis
    
    def render_report_interface(self, user_id: int):
        """Render report generation interface for admins"""
        st.markdown("### 📊 Generate Reports")
        
        col1, col2 = st.columns(2)
        
        with col1:
            report_type = st.selectbox(
                "Report Type",
                ["Feedback Summary", "Analytics Summary", "Trend Analysis", "Comprehensive Analysis"]
            )
            
            date_range = st.selectbox(
                "Date Range",
                [7, 14, 30, 60, 90],
                index=2,
                format_func=lambda x: f"Last {x} days"
            )
        
        with col2:
            format_type = st.selectbox("Format", ["CSV", "JSON"])
            
            # Filter options
            with st.expander("🔍 Filters"):
                category_filter = st.selectbox("Category", ["All"] + ["Traffic", "Sanitation", "Safety", "Water", "Electricity", "Infrastructure"])
                severity_filter = st.selectbox("Severity", ["All", "High", "Medium", "Low"])
                status_filter = st.selectbox("Status", ["All", "Pending", "In Progress", "Resolved"])
        
        if st.button("📋 Generate Report", use_container_width=True):
            with st.spinner("Generating report..."):
                filters = {}
                if category_filter != "All":
                    filters['category'] = category_filter
                if severity_filter != "All":
                    filters['severity'] = severity_filter
                if status_filter != "All":
                    filters['status'] = status_filter
                
                try:
                    if format_type == "CSV":
                        report_type_key = report_type.lower().replace(" ", "_")
                        filepath = self.generate_csv_report(report_type_key, date_range, filters)
                        
                        # Provide download
                        with open(filepath, 'rb') as file:
                            st.download_button(
                                label="📥 Download CSV Report",
                                data=file.read(),
                                file_name=os.path.basename(filepath),
                                mime="text/csv"
                            )
                    
                    else:  # JSON format
                        report_data = self.generate_detailed_report(
                            admin_id=user_id,
                            report_type=report_type.lower().replace(" ", "_"),
                            parameters={'date_range': date_range, 'filters': filters}
                        )
                        
                        # Display report data
                        st.json(report_data)
                        
                        # Provide download
                        json_str = json.dumps(report_data, indent=2)
                        st.download_button(
                            label="📥 Download JSON Report",
                            data=json_str,
                            file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                    
                    st.success("Report generated successfully!")
                    
                except Exception as e:
                    st.error(f"Error generating report: {str(e)}")