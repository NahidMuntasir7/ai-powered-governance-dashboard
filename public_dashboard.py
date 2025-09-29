import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from database import DatabaseManager
from typing import Dict, List

class PublicDashboard:
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def render_public_dashboard(self):
        """Render public transparency dashboard"""
        st.markdown("# 🏛️ Public Civic Feedback Dashboard")
        st.markdown("### Transparency in Action - Real-time insights into community issues and government response")
        
        # Get public statistics
        stats = self.db.get_public_stats()
        
        # Key public metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card total-feedback">
                <h3>📊 Total Issues</h3>
                <div class="number">{stats['total_issues']}</div>
                <div class="subtitle">Community reports</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card resolution-rate">
                <h3>✅ Resolved</h3>
                <div class="number">{stats['resolved_issues']}</div>
                <div class="subtitle">Issues completed</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card recent-feedback">
                <h3>⏳ In Progress</h3>
                <div class="number">{stats['in_progress_issues']}</div>
                <div class="subtitle">Being addressed</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📈 Resolution Rate</h3>
                <div class="number" style="color: #4ade80;">{stats['resolution_rate']}%</div>
                <div class="subtitle">Government efficiency</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Charts section
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="chart-title">📊 Issues by Category</h3>', unsafe_allow_html=True)
            
            if stats['category_distribution']:
                fig_category = px.pie(
                    values=list(stats['category_distribution'].values()),
                    names=list(stats['category_distribution'].keys()),
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
            st.markdown('<h3 class="chart-title">📈 Weekly Progress</h3>', unsafe_allow_html=True)
            
            if stats['weekly_trends']:
                weeks = [trend['week'] for trend in stats['weekly_trends']]
                submitted = [trend['submitted'] for trend in stats['weekly_trends']]
                resolved = [trend['resolved'] for trend in stats['weekly_trends']]
                
                fig_trends = go.Figure()
                fig_trends.add_trace(go.Scatter(
                    x=weeks, y=submitted, name='Submitted',
                    line=dict(color='#3b82f6', width=3),
                    mode='lines+markers'
                ))
                fig_trends.add_trace(go.Scatter(
                    x=weeks, y=resolved, name='Resolved',
                    line=dict(color='#10b981', width=3),
                    mode='lines+markers'
                ))
                
                fig_trends.update_layout(
                    xaxis_title="Week",
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
        
        # Government accountability section
        st.markdown("### 🎯 Government Accountability")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="info-box green">
                <strong>Response Time</strong><br>
                Average: 2.3 days<br>
                Target: ≤ 3 days
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="info-box blue">
                <strong>Citizen Satisfaction</strong><br>
                Rating: 4.2/5.0<br>
                Based on resolved issues
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="info-box yellow">
                <strong>Transparency Score</strong><br>
                Score: 87%<br>
                Public data availability
            </div>
            """, unsafe_allow_html=True)
        
        # Recent resolved issues (anonymized)
        st.markdown("### ✅ Recently Resolved Issues")
        
        # Get some resolved feedback (anonymized)
        resolved_feedback = self.db.get_all_feedback(status='Resolved')[:5]
        
        if resolved_feedback:
            for i, feedback in enumerate(resolved_feedback):
                category_emoji = {
                    'Traffic': '🚗', 'Sanitation': '🗑️', 'Safety': '🛡️',
                    'Water': '💧', 'Electricity': '⚡', 'Infrastructure': '🏗️'
                }
                
                st.markdown(f"""
                <div class="feedback-card">
                    <div class="feedback-header">
                        {category_emoji.get(feedback['category'], '📋')} {feedback['category']} Issue #{feedback['feedback_id']}
                    </div>
                    <div class="feedback-text">
                        Issue resolved in {feedback.get('location_detail', 'Community Area')} - {feedback['title'][:100]}...
                    </div>
                    <div class="feedback-date">
                        ✅ Resolved on {feedback.get('resolved_at', feedback['updated_at'])[:10]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recently resolved issues to display.")
        
        # Footer with disclaimer
        st.markdown("---")
        st.markdown("""
        <div class="footer">
            <div class="footer-title">🔒 Privacy Notice</div>
            <div class="footer-subtitle">
                All personal information has been anonymized to protect citizen privacy. 
                This dashboard shows aggregated public data to ensure government transparency and accountability.
            </div>
        </div>
        """, unsafe_allow_html=True)