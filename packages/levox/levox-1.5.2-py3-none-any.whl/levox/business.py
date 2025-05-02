"""
Business module for enterprise features like report automation, dashboards and team collaboration.
"""
import os
import json
import csv
import datetime
import base64
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

from levox.scanner import GDPRIssue

class Report:
    """Base class for GDPR compliance reports."""
    def __init__(self, issues: List[GDPRIssue], project_name: str = ""):
        self.issues = issues
        self.project_name = project_name or "Unnamed Project"
        self.timestamp = datetime.datetime.now()
        
    def generate_summary(self) -> Dict[str, Any]:
        """Generate a summary of issues."""
        if not self.issues:
            return {
                "project_name": self.project_name,
                "scan_date": self.timestamp.isoformat(),
                "total_issues": 0,
                "high_severity": 0,
                "medium_severity": 0,
                "low_severity": 0,
                "issue_types": {},
                "compliance_score": 100,
                "risk_level": "Low"
            }
            
        # Count issues by severity
        high = sum(1 for issue in self.issues if issue.severity == "high")
        medium = sum(1 for issue in self.issues if issue.severity == "medium")
        low = sum(1 for issue in self.issues if issue.severity == "low")
        
        # Count issues by type
        issue_types = defaultdict(int)
        for issue in self.issues:
            issue_types[issue.issue_type] += 1
            
        # Calculate compliance score (0-100)
        # High severity issues have more impact on the score
        total_weight = len(self.issues)
        weighted_issues = (high * 1.0) + (medium * 0.5) + (low * 0.2)
        compliance_score = max(0, 100 - (weighted_issues * 100 / max(1, total_weight)))
        
        # Determine risk level
        risk_level = "Critical"
        if compliance_score >= 90:
            risk_level = "Low"
        elif compliance_score >= 75:
            risk_level = "Medium"
        elif compliance_score >= 50:
            risk_level = "High"
            
        return {
            "project_name": self.project_name,
            "scan_date": self.timestamp.isoformat(),
            "total_issues": len(self.issues),
            "high_severity": high,
            "medium_severity": medium,
            "low_severity": low,
            "issue_types": dict(issue_types),
            "compliance_score": round(compliance_score, 1),
            "risk_level": risk_level
        }
    
    def export_json(self, output_file: str) -> bool:
        """Export the report as JSON."""
        try:
            summary = self.generate_summary()
            
            # Create full report
            report = {
                "summary": summary,
                "issues": [issue.to_dict() for issue in self.issues]
            }
            
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error exporting JSON report: {e}")
            return False


class EnterpriseReport(Report):
    """Extended report with enterprise features."""
    def __init__(self, issues: List[GDPRIssue], project_name: str = "", 
                 metadata: Dict[str, Any] = None):
        super().__init__(issues, project_name)
        self.metadata = metadata or {}
        
    def export_csv(self, output_file: str) -> bool:
        """Export the report as CSV."""
        try:
            with open(output_file, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow([
                    "Issue Type", "Severity", "File Path", "Line Number", 
                    "Content", "Remediation"
                ])
                
                # Write issues
                for issue in self.issues:
                    writer.writerow([
                        issue.issue_type,
                        issue.severity,
                        issue.file_path,
                        issue.line_number,
                        issue.line_content,
                        issue.remediation or "N/A"
                    ])
                    
            return True
        except Exception as e:
            print(f"Error exporting CSV report: {e}")
            return False
    
    def export_html(self, output_file: str) -> bool:
        """Export the report as HTML."""
        try:
            summary = self.generate_summary()
            
            # Create charts for the report
            severity_chart = self._create_severity_chart()
            issues_chart = self._create_issues_chart()
            
            # Generate HTML content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>GDPR Compliance Report - {self.project_name}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1, h2 {{ color: #333; }}
                    .summary {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; }}
                    .score {{ font-size: 24px; font-weight: bold; }}
                    .risk-Low {{ color: green; }}
                    .risk-Medium {{ color: orange; }}
                    .risk-High {{ color: red; }}
                    .risk-Critical {{ color: darkred; }}
                    table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    tr:nth-child(even) {{ background-color: #f9f9f9; }}
                    .charts {{ display: flex; justify-content: space-between; margin: 20px 0; }}
                    .chart {{ width: 48%; }}
                </style>
            </head>
            <body>
                <h1>GDPR Compliance Report - {self.project_name}</h1>
                <p>Generated on: {self.timestamp.strftime("%Y-%m-%d %H:%M:%S")}</p>
                
                <div class="summary">
                    <h2>Summary</h2>
                    <p>Compliance Score: <span class="score risk-{summary['risk_level']}">{summary['compliance_score']}%</span></p>
                    <p>Risk Level: <span class="risk-{summary['risk_level']}">{summary['risk_level']}</span></p>
                    <p>Total Issues: {summary['total_issues']}</p>
                    <p>High Severity: {summary['high_severity']}</p>
                    <p>Medium Severity: {summary['medium_severity']}</p>
                    <p>Low Severity: {summary['low_severity']}</p>
                </div>
                
                <div class="charts">
                    <div class="chart">
                        <h2>Issues by Severity</h2>
                        <img src="data:image/png;base64,{severity_chart}" alt="Severity Chart" width="100%">
                    </div>
                    <div class="chart">
                        <h2>Issues by Type</h2>
                        <img src="data:image/png;base64,{issues_chart}" alt="Issues Chart" width="100%">
                    </div>
                </div>
                
                <h2>Detailed Issues</h2>
                <table>
                    <tr>
                        <th>Issue Type</th>
                        <th>Severity</th>
                        <th>File Path</th>
                        <th>Line</th>
                        <th>Content</th>
                        <th>Remediation</th>
                    </tr>
            """
            
            for issue in self.issues:
                # Determine row color based on severity
                row_class = ""
                if issue.severity == "high":
                    row_class = ' class="risk-High"'
                elif issue.severity == "medium":
                    row_class = ' class="risk-Medium"'
                
                html_content += f"""
                    <tr{row_class}>
                        <td>{issue.issue_type}</td>
                        <td>{issue.severity}</td>
                        <td>{issue.file_path}</td>
                        <td>{issue.line_number}</td>
                        <td><code>{issue.line_content}</code></td>
                        <td>{issue.remediation or "N/A"}</td>
                    </tr>
                """
                
            html_content += """
                </table>
                
                <h2>Recommendations</h2>
                <ul>
                    <li>Address high severity issues immediately</li>
                    <li>Create a remediation plan for medium severity issues</li>
                    <li>Schedule regular compliance scans</li>
                    <li>Review your GDPR documentation and processes</li>
                </ul>
                
                <footer>
                    <p>Generated by Levox GDPR Compliance Tool</p>
                </footer>
            </body>
            </html>
            """
            
            with open(output_file, 'w') as f:
                f.write(html_content)
                
            return True
        except Exception as e:
            print(f"Error exporting HTML report: {e}")
            return False
    
    def _create_severity_chart(self) -> str:
        """Create a chart showing issues by severity."""
        try:
            plt.figure(figsize=(6, 4))
            
            # Count issues by severity
            severities = ['high', 'medium', 'low']
            counts = [
                sum(1 for issue in self.issues if issue.severity == 'high'),
                sum(1 for issue in self.issues if issue.severity == 'medium'),
                sum(1 for issue in self.issues if issue.severity == 'low')
            ]
            
            # Colors for each severity
            colors = ['#ff4444', '#ffbb33', '#00C851']
            
            # Create pie chart
            plt.pie(counts, labels=severities, colors=colors, autopct='%1.1f%%', startangle=90)
            plt.axis('equal')
            plt.title('Issues by Severity')
            
            # Convert chart to base64 for embedding in HTML
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
        except Exception as e:
            print(f"Error creating severity chart: {e}")
            return ""
    
    def _create_issues_chart(self) -> str:
        """Create a chart showing issues by type."""
        try:
            plt.figure(figsize=(6, 4))
            
            # Count issues by type
            issue_counts = defaultdict(int)
            for issue in self.issues:
                issue_counts[issue.issue_type] += 1
                
            # Sort by count (descending)
            sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
            
            # For readability, only show top 5 types
            if len(sorted_issues) > 5:
                other_count = sum(count for _, count in sorted_issues[5:])
                sorted_issues = sorted_issues[:5]
                sorted_issues.append(('Other', other_count))
                
            # Extract labels and values
            labels = [label for label, _ in sorted_issues]
            values = [value for _, value in sorted_issues]
            
            # Create bar chart
            plt.bar(range(len(labels)), values, color='#3498db')
            plt.xticks(range(len(labels)), labels, rotation=45, ha='right')
            plt.title('Issues by Type')
            plt.tight_layout()
            
            # Convert chart to base64 for embedding in HTML
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            plt.close()
            
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
        except Exception as e:
            print(f"Error creating issues chart: {e}")
            return ""
    
    def export_pdf(self, output_file: str) -> bool:
        """Export the report as PDF."""
        try:
            # For this implementation, we'll first create an HTML file and then convert it to PDF
            # In a real implementation, you might use a library like reportlab or weasyprint
            
            # Create a temporary HTML file
            html_file = output_file.replace('.pdf', '_temp.html')
            self.export_html(html_file)
            
            # In a real implementation, you would convert HTML to PDF here
            # For this demo, we'll just return a message
            print(f"PDF export would convert {html_file} to {output_file}")
            print("For a complete implementation, use a library like weasyprint or reportlab")
            
            return True
        except Exception as e:
            print(f"Error exporting PDF report: {e}")
            return False


class ComplianceDashboard:
    """Enterprise dashboard for tracking compliance over time."""
    def __init__(self, data_dir: str = None):
        """Initialize the dashboard with a data directory."""
        self.data_dir = data_dir or os.path.expanduser("~/.levox/dashboard")
        
        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def add_scan_result(self, issues: List[GDPRIssue], project_name: str, 
                        metadata: Dict[str, Any] = None) -> str:
        """Add a scan result to the dashboard history."""
        try:
            # Create report object
            report = EnterpriseReport(issues, project_name, metadata)
            summary = report.generate_summary()
            
            # Generate a unique ID for this scan
            scan_id = f"{project_name.lower().replace(' ', '_')}_{int(datetime.datetime.now().timestamp())}"
            
            # Save the summary to the dashboard history
            data_file = os.path.join(self.data_dir, f"{scan_id}.json")
            
            with open(data_file, 'w') as f:
                json.dump({
                    "scan_id": scan_id,
                    "summary": summary,
                    "metadata": metadata or {},
                    "timestamp": datetime.datetime.now().isoformat()
                }, f, indent=2)
                
            return scan_id
        except Exception as e:
            print(f"Error adding scan result: {e}")
            return ""
    
    def get_history(self, project_name: str = None, days: int = 30) -> List[Dict[str, Any]]:
        """Get scan history for a project or all projects."""
        try:
            history = []
            
            # Calculate the cutoff date
            cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
            
            # Read all saved scan results
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.data_dir, filename)
                    
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        
                    # Only include if it matches the project name filter (if provided)
                    if project_name and data["summary"]["project_name"] != project_name:
                        continue
                        
                    # Only include if it's within the time range
                    scan_time = datetime.datetime.fromisoformat(data["timestamp"])
                    if scan_time < cutoff:
                        continue
                        
                    history.append(data)
                    
            # Sort by timestamp (newest first)
            history.sort(key=lambda x: x["timestamp"], reverse=True)
            
            return history
        except Exception as e:
            print(f"Error getting history: {e}")
            return []
    
    def generate_trend_chart(self, project_name: str, days: int = 90) -> Optional[str]:
        """Generate a chart showing compliance trends over time."""
        try:
            # Get history data
            history = self.get_history(project_name, days)
            
            if not history:
                return None
                
            # Extract dates and scores
            dates = [datetime.datetime.fromisoformat(item["timestamp"]) for item in history]
            scores = [item["summary"]["compliance_score"] for item in history]
            high_counts = [item["summary"]["high_severity"] for item in history]
            
            # Need to reverse the order to show oldest to newest
            dates.reverse()
            scores.reverse()
            high_counts.reverse()
            
            # Create the figure with two Y axes
            fig, ax1 = plt.subplots(figsize=(10, 6))
            
            # Plot compliance score
            ax1.set_xlabel('Date')
            ax1.set_ylabel('Compliance Score (%)', color='blue')
            ax1.plot(dates, scores, 'b-', marker='o')
            ax1.tick_params(axis='y', labelcolor='blue')
            ax1.set_ylim(0, 100)
            
            # Create second Y axis for high severity issues
            ax2 = ax1.twinx()
            ax2.set_ylabel('High Severity Issues', color='red')
            ax2.plot(dates, high_counts, 'r-', marker='x')
            ax2.tick_params(axis='y', labelcolor='red')
            
            # Set title and format
            plt.title(f'Compliance Trend for {project_name}')
            fig.tight_layout()
            
            # Format x-axis dates
            plt.xticks(rotation=45)
            
            # Save the chart to a file
            output_file = os.path.join(self.data_dir, f"{project_name.lower().replace(' ', '_')}_trend.png")
            plt.savefig(output_file)
            plt.close()
            
            return output_file
        except Exception as e:
            print(f"Error generating trend chart: {e}")
            return None
    
    def get_compliance_stats(self, project_name: str = None) -> Dict[str, Any]:
        """Get compliance statistics across projects or for a specific project."""
        try:
            # Get all history
            all_history = self.get_history(project_name, days=365)
            
            if not all_history:
                return {
                    "projects": 0,
                    "total_scans": 0,
                    "average_score": 0,
                    "trend": "stable",
                    "most_common_issues": []
                }
                
            # Get unique projects
            projects = set(item["summary"]["project_name"] for item in all_history)
            
            # Calculate average compliance score
            avg_score = sum(item["summary"]["compliance_score"] for item in all_history) / len(all_history)
            
            # Determine trend (improving, declining, or stable)
            if len(all_history) >= 2:
                # Compare most recent with previous
                newest = all_history[0]["summary"]["compliance_score"]
                prev = all_history[1]["summary"]["compliance_score"]
                
                if newest > prev + 5:  # 5% improvement threshold
                    trend = "improving"
                elif newest < prev - 5:  # 5% decline threshold
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "stable"
                
            # Get most common issue types
            issue_counts = defaultdict(int)
            for item in all_history:
                for issue_type, count in item["summary"]["issue_types"].items():
                    issue_counts[issue_type] += count
                    
            # Sort and get top 5
            most_common = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                "projects": len(projects),
                "total_scans": len(all_history),
                "average_score": round(avg_score, 1),
                "trend": trend,
                "most_common_issues": most_common
            }
        except Exception as e:
            print(f"Error getting compliance stats: {e}")
            return {}


class TeamManager:
    """Enterprise team collaboration features."""
    def __init__(self, data_dir: str = None):
        """Initialize the team manager."""
        self.data_dir = data_dir or os.path.expanduser("~/.levox/teams")
        
        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        # Team data file
        self.teams_file = os.path.join(self.data_dir, "teams.json")
        
        # Load or initialize teams data
        self.teams = self._load_teams()
    
    def _load_teams(self) -> Dict[str, Any]:
        """Load teams data from file or create default."""
        if os.path.exists(self.teams_file):
            try:
                with open(self.teams_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {"teams": {}, "members": {}, "assignments": {}}
        else:
            return {"teams": {}, "members": {}, "assignments": {}}
    
    def _save_teams(self) -> bool:
        """Save teams data to file."""
        try:
            with open(self.teams_file, 'w') as f:
                json.dump(self.teams, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving teams data: {e}")
            return False
    
    def create_team(self, team_name: str, description: str = "") -> bool:
        """Create a new team."""
        if team_name in self.teams["teams"]:
            print(f"Team {team_name} already exists")
            return False
            
        self.teams["teams"][team_name] = {
            "name": team_name,
            "description": description,
            "created_at": datetime.datetime.now().isoformat()
        }
        
        return self._save_teams()
    
    def add_member(self, email: str, name: str, role: str = "viewer") -> bool:
        """Add a new team member."""
        if email in self.teams["members"]:
            print(f"Member {email} already exists")
            return False
            
        self.teams["members"][email] = {
            "email": email,
            "name": name,
            "role": role,
            "created_at": datetime.datetime.now().isoformat()
        }
        
        return self._save_teams()
    
    def assign_to_team(self, email: str, team_name: str, role: str = None) -> bool:
        """Assign a member to a team."""
        if email not in self.teams["members"]:
            print(f"Member {email} does not exist")
            return False
            
        if team_name not in self.teams["teams"]:
            print(f"Team {team_name} does not exist")
            return False
            
        if "assignments" not in self.teams:
            self.teams["assignments"] = {}
            
        if team_name not in self.teams["assignments"]:
            self.teams["assignments"][team_name] = []
            
        # Check if already assigned
        for assignment in self.teams["assignments"][team_name]:
            if assignment["email"] == email:
                # Update role if provided
                if role:
                    assignment["role"] = role
                return self._save_teams()
                
        # Add new assignment
        self.teams["assignments"][team_name].append({
            "email": email,
            "role": role or self.teams["members"][email]["role"],
            "assigned_at": datetime.datetime.now().isoformat()
        })
        
        return self._save_teams()
    
    def assign_issue(self, issue_id: str, email: str, due_date: str = None) -> bool:
        """Assign an issue to a team member."""
        if email not in self.teams["members"]:
            print(f"Member {email} does not exist")
            return False
            
        if "issue_assignments" not in self.teams:
            self.teams["issue_assignments"] = {}
            
        self.teams["issue_assignments"][issue_id] = {
            "email": email,
            "assigned_at": datetime.datetime.now().isoformat(),
            "due_date": due_date,
            "status": "open"
        }
        
        return self._save_teams()
    
    def update_issue_status(self, issue_id: str, status: str) -> bool:
        """Update the status of an assigned issue."""
        if "issue_assignments" not in self.teams or issue_id not in self.teams["issue_assignments"]:
            print(f"Issue {issue_id} not found or not assigned")
            return False
            
        self.teams["issue_assignments"][issue_id]["status"] = status
        self.teams["issue_assignments"][issue_id]["updated_at"] = datetime.datetime.now().isoformat()
        
        return self._save_teams()
    
    def get_team_members(self, team_name: str) -> List[Dict[str, Any]]:
        """Get all members of a team."""
        if team_name not in self.teams["teams"] or team_name not in self.teams.get("assignments", {}):
            return []
            
        members = []
        for assignment in self.teams["assignments"][team_name]:
            email = assignment["email"]
            if email in self.teams["members"]:
                member = self.teams["members"][email].copy()
                member["team_role"] = assignment["role"]
                members.append(member)
                
        return members
    
    def get_member_assignments(self, email: str) -> List[Dict[str, Any]]:
        """Get all issues assigned to a team member."""
        if email not in self.teams["members"] or "issue_assignments" not in self.teams:
            return []
            
        assignments = []
        for issue_id, assignment in self.teams["issue_assignments"].items():
            if assignment["email"] == email:
                issue_assignment = assignment.copy()
                issue_assignment["issue_id"] = issue_id
                assignments.append(issue_assignment)
                
        return assignments 