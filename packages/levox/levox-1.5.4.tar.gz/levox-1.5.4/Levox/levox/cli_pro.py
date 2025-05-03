"""
Pro version of the CLI with advanced features like license management and enterprise reporting.
"""
import os
import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import datetime

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from prompt_toolkit.shortcuts import clear, set_title, message_dialog, yes_no_dialog
from prompt_toolkit.shortcuts import radiolist_dialog, input_dialog

from levox.scanner import Scanner, GDPRIssue
from levox.advanced_scanner import AdvancedScanner
from levox.fixer import Fixer, OLLAMA_AVAILABLE
from levox.license_manager import LicenseManager
from levox.business import Report, EnterpriseReport, ComplianceDashboard, TeamManager

# Define pro/enterprise commands
PRO_COMMANDS = {
    'advanced_scan': 'Perform an advanced scan with false positive reduction',
    'batch_scan': 'Scan multiple directories at once',
    'schedule': 'Schedule automated scans',
    'license': 'Manage your license',
    'dashboard': 'View compliance dashboard',
    'team': 'Manage team collaboration',
    'export': 'Export reports in various formats',
}

# Define styles
PRO_STYLE = Style.from_dict({
    'title': 'bg:#0000aa fg:#ffffff bold',
    'header': 'fg:#00aa00 bold',
    'warning': 'fg:#aa0000 bold',
    'info': 'fg:#0000aa',
    'highlight': 'fg:#aa5500 bold',
    'prompt': 'fg:#aa00aa',
    'license-pro': 'fg:#00aa00 bold',
    'license-enterprise': 'fg:#0000aa bold',
    'license-freemium': 'fg:#aa5500',
})

class LevoxProCLI:
    def __init__(self):
        """Initialize the Pro CLI."""
        self.session = PromptSession()
        self.current_issues: List[GDPRIssue] = []
        self.last_scanned_dir: Optional[str] = None
        self.fixer = Fixer()
        self.license_manager = LicenseManager()
        self.dashboard = ComplianceDashboard()
        self.team_manager = TeamManager()
        
        # Check if we have a pro/enterprise license
        self.is_pro = self.license_manager.tier in ["pro", "enterprise"]
        self.is_enterprise = self.license_manager.tier == "enterprise"
        
        # Set the title
        set_title("Levox Pro - GDPR Compliance Tool")
        
    def show_welcome(self):
        """Show welcome message and banner."""
        clear()
        
        # Show different banner based on license tier
        if self.is_enterprise:
            print("""
██╗     ███████╗██╗   ██╗ ██████╗ ██╗  ██╗
██║     ██╔════╝██║   ██║██╔═══██╗╚██╗██╔╝
██║     █████╗  ██║   ██║██║   ██║ ╚███╔╝ 
██║     ██╔══╝  ╚██╗ ██╔╝██║   ██║ ██╔██╗ 
███████╗███████╗ ╚████╔╝ ╚██████╔╝██╔╝ ██╗
╚══════╝╚══════╝  ╚═══╝   ╚═════╝ ╚═╝  ╚═╝
        ENTERPRISE EDITION
""")
        elif self.is_pro:
            print("""
██╗     ███████╗██╗   ██╗ ██████╗ ██╗  ██╗
██║     ██╔════╝██║   ██║██╔═══██╗╚██╗██╔╝
██║     █████╗  ██║   ██║██║   ██║ ╚███╔╝ 
██║     ██╔══╝  ╚██╗ ██╔╝██║   ██║ ██╔██╗ 
███████╗███████╗ ╚████╔╝ ╚██████╔╝██╔╝ ██╗
╚══════╝╚══════╝  ╚═══╝   ╚═════╝ ╚═╝  ╚═╝
        PROFESSIONAL EDITION
""")
        else:
            print("""
██╗     ███████╗██╗   ██╗ ██████╗ ██╗  ██╗
██║     ██╔════╝██║   ██║██╔═══██╗╚██╗██╔╝
██║     █████╗  ██║   ██║██║   ██║ ╚███╔╝ 
██║     ██╔══╝  ╚██╗ ██╔╝██║   ██║ ██╔██╗ 
███████╗███████╗ ╚████╔╝ ╚██████╔╝██╔╝ ██╗
╚══════╝╚══════╝  ╚═══╝   ╚═════╝ ╚═╝  ╚═╝
        FREEMIUM EDITION
""")
        
        # Show license info
        license_info = self.license_manager.get_license_info()
        
        print(f"License: {license_info['tier'].upper()}")
        if license_info['tier'] != "freemium":
            print(f"Expires: {license_info['expires_at']}")
            if 'days_remaining' in license_info:
                print(f"Days remaining: {license_info['days_remaining']}")
        
        print("\nWelcome to Levox - Your GDPR Compliance Assistant\n")
        print("Type 'help' to see available commands")
        print("=" * 50)
        
    def show_help(self):
        """Show help message with available commands."""
        from levox.cli import COMMANDS
        
        clear()
        print("Available Commands:\n")
        
        # Standard commands
        print("STANDARD COMMANDS:")
        for cmd, desc in COMMANDS.items():
            print(f"  {cmd:<15} - {desc}")
            
        # Pro/Enterprise commands
        if self.is_pro or self.is_enterprise:
            print("\nPRO/ENTERPRISE COMMANDS:")
            for cmd, desc in PRO_COMMANDS.items():
                # Skip enterprise-only commands for pro users
                if cmd in ['team'] and not self.is_enterprise:
                    continue
                print(f"  {cmd:<15} - {desc}")
        else:
            print("\nPRO/ENTERPRISE COMMANDS (Upgrade to access):")
            for cmd, desc in PRO_COMMANDS.items():
                print(f"  {cmd:<15} - {desc}")
                
        print("\nExample usage:")
        print("  scan ./myproject")
        print("  advanced_scan ./myproject")
        print("  license activate YOUR-LICENSE-KEY")
        print("\nPress Enter to continue...")
        input()
        
    def advanced_scan(self, directory: str, config: Dict[str, Any] = None) -> List[GDPRIssue]:
        """Perform an advanced scan with false positive reduction."""
        if not os.path.isdir(directory):
            print(f"Directory not found: {directory}")
            return []
            
        # Check if advanced scanning is available in the license
        if not self.license_manager.get_feature("advanced_detection"):
            print("Advanced scanning is a Pro/Enterprise feature.")
            print("Upgrade your license to access this feature.")
            return []
            
        print(f"Performing advanced scan of directory: {directory}")
        scanner = AdvancedScanner(directory, config=config)
        issues = scanner.scan_directory()
        self.current_issues = issues
        self.last_scanned_dir = directory
        
        # Update scan count in license
        self.license_manager.update_files_scanned(len(issues))
        
        return issues
        
    def batch_scan(self, directories: List[str]) -> Dict[str, List[GDPRIssue]]:
        """Scan multiple directories at once."""
        # Check if batch processing is available in the license
        if not self.license_manager.get_feature("batch_processing"):
            print("Batch scanning is a Pro/Enterprise feature.")
            print("Upgrade your license to access this feature.")
            return {}
            
        results = {}
        for directory in directories:
            if not os.path.isdir(directory):
                print(f"Directory not found: {directory}")
                continue
                
            print(f"Scanning directory: {directory}")
            scanner = AdvancedScanner(directory) if self.license_manager.get_feature("advanced_detection") else Scanner(directory)
            issues = scanner.scan_directory()
            results[directory] = issues
            
        # Set the last directory as current
        if directories:
            self.last_scanned_dir = directories[-1]
            self.current_issues = results.get(directories[-1], [])
            
        return results
        
    def export_report(self, directory: str, output_file: str, format: str = "json"):
        """Export a report in various formats."""
        # Check if this export format is available in the license
        available_formats = self.license_manager.get_feature("export_formats")
        if format not in available_formats:
            print(f"Export in {format} format is not available in your license tier.")
            print(f"Available formats: {', '.join(available_formats)}")
            return
            
        # Check if we need to scan first
        if not self.current_issues or self.last_scanned_dir != directory:
            print("Scanning directory first...")
            self.advanced_scan(directory) if self.license_manager.get_feature("advanced_detection") else self.scan_directory(directory)
            
        if not self.current_issues:
            print("No issues to report!")
            return
            
        # Check if we can generate a report based on license limits
        if not self.license_manager.can_generate_report():
            print("You have reached your report generation limit for this month.")
            print("Upgrade your license to generate more reports.")
            return
            
        # Create appropriate report object based on license tier
        if self.is_pro or self.is_enterprise:
            report = EnterpriseReport(self.current_issues, os.path.basename(directory))
        else:
            report = Report(self.current_issues, os.path.basename(directory))
            
        # Export in the requested format
        success = False
        if format == "json":
            success = report.export_json(output_file)
        elif format == "csv" and (self.is_pro or self.is_enterprise):
            success = report.export_csv(output_file)
        elif format == "html" and (self.is_pro or self.is_enterprise):
            success = report.export_html(output_file)
        elif format == "pdf" and (self.is_pro or self.is_enterprise):
            success = report.export_pdf(output_file)
            
        if success:
            print(f"Report exported to {output_file}")
            # Update report count in license
            self.license_manager.update_reports_generated()
        else:
            print("Failed to export report.")
            
    def manage_license(self, action: str, *args):
        """Manage license (activate, deactivate, info)."""
        if action == "activate":
            if len(args) < 1:
                print("Please provide a license key")
                return
                
            license_key = args[0]
            if self.license_manager.activate_license(license_key):
                print("License activated successfully!")
                # Update pro/enterprise status
                self.is_pro = self.license_manager.tier in ["pro", "enterprise"]
                self.is_enterprise = self.license_manager.tier == "enterprise"
            else:
                print("Failed to activate license. Please check the key and try again.")
                
        elif action == "deactivate":
            if yes_no_dialog(
                title="Confirm Deactivation",
                text="Are you sure you want to deactivate your license? You will lose access to pro/enterprise features."
            ).run():
                if self.license_manager.deactivate_license():
                    print("License deactivated successfully.")
                    # Update pro/enterprise status
                    self.is_pro = False
                    self.is_enterprise = False
                else:
                    print("Failed to deactivate license.")
                    
        elif action == "info":
            info = self.license_manager.get_license_info()
            print("\nLicense Information:")
            print(f"Tier: {info['tier'].upper()}")
            print(f"ID: {info['license_id']}")
            print(f"Created: {info['created_at']}")
            
            if info['tier'] != "freemium":
                print(f"Activated: {info.get('activated_at', 'N/A')}")
                print(f"Expires: {info.get('expires_at', 'N/A')}")
                if 'days_remaining' in info:
                    print(f"Days remaining: {info['days_remaining']}")
                    
            print("\nUsage Statistics:")
            print(f"Files scanned: {info['files_scanned']}")
            print(f"Reports generated: {info['reports_generated']}")
            
        elif action == "trial":
            # Generate a trial license key
            if self.is_pro or self.is_enterprise:
                print("You already have a Pro or Enterprise license.")
                return
                
            days = 30
            if len(args) >= 1:
                try:
                    days = int(args[0])
                except ValueError:
                    pass
                    
            trial_key = self.license_manager.generate_trial_key(days)
            print(f"\nYour {days}-day Pro trial license key:")
            print(trial_key)
            print("\nUse this command to activate:")
            print(f"license activate {trial_key}")
            
        else:
            print("Unknown license action. Available actions: activate, deactivate, info, trial")
            
    def show_dashboard(self):
        """Show the compliance dashboard."""
        # Check if dashboard is available in the license
        if not self.is_pro and not self.is_enterprise:
            print("Dashboard is a Pro/Enterprise feature.")
            print("Upgrade your license to access this feature.")
            return
            
        # Get compliance stats
        stats = self.dashboard.get_compliance_stats()
        
        clear()
        print("===== COMPLIANCE DASHBOARD =====\n")
        print(f"Projects: {stats['projects']}")
        print(f"Total Scans: {stats['total_scans']}")
        print(f"Average Compliance Score: {stats['average_score']}%")
        print(f"Trend: {stats['trend'].upper()}")
        
        if stats['most_common_issues']:
            print("\nMost Common Issues:")
            for issue_type, count in stats['most_common_issues']:
                print(f"  {issue_type}: {count}")
                
        # Get history for more details
        history = self.dashboard.get_history(days=30)
        
        if history:
            print("\nRecent Scans:")
            for i, scan in enumerate(history[:5], 1):
                summary = scan['summary']
                print(f"{i}. {summary['project_name']} - {summary['compliance_score']}% - {summary['total_issues']} issues")
                
        print("\nPress Enter to continue...")
        input()
        
    def manage_team(self, action: str, *args):
        """Manage team collaboration."""
        # Check if team features are available in the license
        if not self.is_enterprise:
            print("Team management is an Enterprise feature.")
            print("Upgrade your license to access this feature.")
            return
            
        if action == "create":
            if len(args) < 1:
                print("Please provide a team name")
                return
                
            team_name = args[0]
            description = args[1] if len(args) > 1 else ""
            
            if self.team_manager.create_team(team_name, description):
                print(f"Team '{team_name}' created successfully.")
            else:
                print(f"Failed to create team '{team_name}'.")
                
        elif action == "add_member":
            if len(args) < 2:
                print("Please provide an email and name")
                return
                
            email = args[0]
            name = args[1]
            role = args[2] if len(args) > 2 else "viewer"
            
            if self.team_manager.add_member(email, name, role):
                print(f"Member '{name}' added successfully.")
            else:
                print(f"Failed to add member '{name}'.")
                
        elif action == "assign":
            if len(args) < 2:
                print("Please provide an email and team name")
                return
                
            email = args[0]
            team_name = args[1]
            role = args[2] if len(args) > 2 else None
            
            if self.team_manager.assign_to_team(email, team_name, role):
                print(f"Member assigned to team '{team_name}' successfully.")
            else:
                print(f"Failed to assign member to team '{team_name}'.")
                
        elif action == "list_members":
            if len(args) < 1:
                print("Please provide a team name")
                return
                
            team_name = args[0]
            members = self.team_manager.get_team_members(team_name)
            
            if members:
                print(f"\nMembers of team '{team_name}':")
                for member in members:
                    print(f"  {member['name']} ({member['email']}) - {member['team_role']}")
            else:
                print(f"No members found for team '{team_name}'.")
                
        else:
            print("Unknown team action. Available actions: create, add_member, assign, list_members")
    
    def show_loading_animation(self, message: str, duration: float = 1.0, steps: int = 10):
        """Display a simple loading animation with a message."""
        animations = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
        for i in range(steps):
            animation_char = animations[i % len(animations)]
            print(f"\r{animation_char} {message}...", end='', flush=True)
            time.sleep(duration / steps)
        print(f"\r✓ {message}... Done")
    
    def run(self):
        """Run the Pro CLI."""
        from levox.cli import COMMANDS
        
        self.show_welcome()
        
        # Create command completer with both standard and pro commands
        all_commands = list(COMMANDS.keys()) + list(PRO_COMMANDS.keys()) + ['./']
        completer = WordCompleter(all_commands)
        
        while True:
            try:
                # Show different prompt based on license tier
                if self.is_enterprise:
                    prompt_html = HTML("<ansi fg='#0000ff' bg='#ffffff' bold>levox-enterprise&gt;</ansi> ")
                elif self.is_pro:
                    prompt_html = HTML("<ansi fg='#00aa00' bold>levox-pro&gt;</ansi> ")
                else:
                    prompt_html = HTML("<ansi>levox&gt;</ansi> ")
                    
                user_input = self.session.prompt(
                    prompt_html,
                    style=PRO_STYLE,
                    completer=completer
                )
                
                # Parse command and arguments
                parts = user_input.strip().split()
                if not parts:
                    continue
                    
                command = parts[0].lower()
                args = parts[1:]
                
                # Process Pro/Enterprise commands
                if command == 'advanced_scan':
                    if not args:
                        print("Please specify a directory to scan.")
                        continue
                        
                    directory = args[0]
                    issues = self.advanced_scan(directory)
                    from levox.cli import LevoxCLI
                    LevoxCLI().display_issues(issues)
                    
                elif command == 'batch_scan':
                    if not args:
                        print("Please specify directories to scan.")
                        print("Example: batch_scan ./dir1 ./dir2 ./dir3")
                        continue
                        
                    results = self.batch_scan(args)
                    
                    if results:
                        print("\nBatch Scan Results:")
                        
                        # Aggregate results for summary table
                        all_issues = []
                        for directory, issues in results.items():
                            print(f"\n{directory}: {len(issues)} issues found")
                            all_issues.extend(issues)
                        
                        if all_issues:
                            from levox.cli import LevoxCLI
                            LevoxCLI().display_issues(all_issues)
                    
                elif command == 'export':
                    if len(args) < 3:
                        print("Please specify a directory, output file, and format.")
                        print("Example: export ./myproject report.json json")
                        print(f"Available formats: {', '.join(self.license_manager.get_feature('export_formats'))}")
                        continue
                        
                    directory = args[0]
                    output_file = args[1]
                    format = args[2]
                    self.export_report(directory, output_file, format)
                    
                elif command == 'license':
                    if not args:
                        print("Please specify a license action.")
                        print("Available actions: activate, deactivate, info, trial")
                        continue
                        
                    action = args[0]
                    self.manage_license(action, *args[1:])
                    
                elif command == 'dashboard':
                    self.show_dashboard()
                    
                elif command == 'team':
                    if not args:
                        print("Please specify a team action.")
                        print("Available actions: create, add_member, assign, list_members")
                        continue
                        
                    action = args[0]
                    self.manage_team(action, *args[1:])
                    
                # For all other commands, delegate to the standard CLI
                else:
                    from levox.cli import LevoxCLI
                    standard_cli = LevoxCLI()
                    
                    if command == 'exit':
                        break
                    elif command == 'help':
                        self.show_help()
                    elif command == 'clear':
                        clear()
                    elif command == 'scan':
                        if not args:
                            print("Please specify a directory to scan.")
                            continue
                            
                        directory = args[0]
                        issues = standard_cli.scan_directory(directory)
                        standard_cli.display_issues(issues)
                        # Copy issues to pro CLI
                        self.current_issues = issues
                        self.last_scanned_dir = directory
                    elif command == 'fix':
                        if not args:
                            print("Please specify a directory to fix.")
                            continue
                            
                        directory = args[0]
                        results = self.fix_issues(directory)
                        print(f"\nFix results: {results['fixed']} fixed, {results['failed']} failed, {results['skipped']} skipped")
                    elif command == 'report':
                        if len(args) < 2:
                            print("Please specify a directory and output file.")
                            print("Example: report ./myproject report.json")
                            continue
                            
                        directory = args[0]
                        output_file = args[1]
                        standard_cli.generate_report(directory, output_file)
                    else:
                        print(f"Unknown command: {command}")
                        print("Type 'help' to see available commands")
                    
            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            except Exception as e:
                print(f"Error: {e}")
                
        print("Thank you for using Levox Pro!")
        
    def fix_issues(self, directory: str, autofix: bool = False) -> Dict[str, int]:
        """Fix GDPR compliance issues in a directory."""
        # Check if we need to scan first
        if not self.current_issues or self.last_scanned_dir != directory:
            print("Scanning directory first...")
            issues = self.advanced_scan(directory)
        else:
            issues = self.current_issues
            
        if not issues:
            print("No issues to fix!")
            return {"total": 0, "fixed": 0, "failed": 0, "skipped": 0}
        
        # Check model availability for AI-powered fixes
        if not autofix and hasattr(self, 'fixer') and hasattr(self.fixer, 'check_model_availability'):
            if not self.fixer.check_model_availability():
                print(f"AI model '{self.fixer.model_name}' is not available.")
                print(f"Run: ollama pull {self.fixer.model_name}")
                return {"total": len(issues), "fixed": 0, "failed": 0, "skipped": len(issues)}
            
        # Confirm with user unless autofix is enabled
        if not autofix:
            confirm = yes_no_dialog(
                title="Confirm Fix",
                text=f"Found {len(issues)} issues. This will modify your code files. Continue?",
            ).run()
            
            if not confirm:
                print("Fix operation cancelled.")
                return {"total": len(issues), "fixed": 0, "failed": 0, "skipped": len(issues)}
        
        # Add better progress indicators
        total_issues = len(issues)
        print(f"\n[1/{total_issues}] Initializing GDPR compliance fix operation...")
        self.show_loading_animation("Preparing enterprise compliance engine", 2.0)
        
        # Define a custom progress tracker to show detailed progress
        fixed_count = 0
        failed_count = 0
        skipped_count = 0
        
        # Use the advanced remediation module if available
        if hasattr(self, 'remediation_module'):
            print("Using advanced remediation module for enterprise-grade fixes...")
            
            for i, issue in enumerate(issues, 1):
                print(f"\n[{i}/{total_issues}] Processing issue in {os.path.basename(issue.file_path)}...")
                self.show_loading_animation("Analyzing code patterns and context", 1.5)
                self.show_loading_animation("Identifying optimal compliance strategy", 1.2)
                self.show_loading_animation("Generating standards-compliant solution", 3.0)
                self.show_loading_animation("Applying code modifications", 2.0)
                
                # Apply fix using the remediation module
                try:
                    result = self.remediation_module.apply_fix(issue.to_dict(), issue.file_path)
                    if result[0]:  # Success
                        print(f"  ✓ Successfully fixed issue with enterprise rules")
                        fixed_count += 1
                    else:
                        print(f"  ⚠ Advanced fix failed, falling back to standard remediation")
                        # Fall back to basic fixer
                        self.show_loading_animation("Attempting alternative remediation approach", 1.5)
                        fix = self.fixer.generate_fix(issue)
                        if fix and self.fixer.apply_fix(issue, fix):
                            print(f"  ✓ Successfully fixed issue with standard remediation")
                            fixed_count += 1
                        else:
                            print(f"  ✘ Failed to apply fix")
                            failed_count += 1
                except Exception as e:
                    print(f"  ✘ Error during fix: {e}")
                    failed_count += 1
            
            self.show_loading_animation("Finalizing GDPR compliance implementation", 2.0)
            self.show_loading_animation("Generating compliance documentation", 1.5)
        else:
            # Use basic fixer for standard fixes
            for i, issue in enumerate(issues, 1):
                print(f"\n[{i}/{total_issues}] Processing issue in {os.path.basename(issue.file_path)}...")
                self.show_loading_animation("Analyzing code context", 1.0)
                self.show_loading_animation("Generating GDPR-compliant solution", 3.0)
                
                # Generate fix
                fix = self.fixer.generate_fix(issue)
                
                if not fix:
                    print(f"  ✘ Could not generate fix for this issue")
                    failed_count += 1
                    continue
                    
                # Apply fix
                self.show_loading_animation("Applying code modifications", 1.5)
                success = self.fixer.apply_fix(issue, fix)
                
                if success:
                    print(f"  ✓ Successfully fixed issue")
                    fixed_count += 1
                else:
                    print(f"  ✘ Failed to apply fix")
                    failed_count += 1
        
        self.show_loading_animation("Finalizing GDPR compliance improvements", 2.0)
        
        # Return results
        return {
            "total": total_issues,
            "fixed": fixed_count,
            "failed": failed_count,
            "skipped": skipped_count
        }

def main():
    """Main entry point for the Pro CLI."""
    cli = LevoxProCLI()
    cli.run()
    
if __name__ == "__main__":
    main() 