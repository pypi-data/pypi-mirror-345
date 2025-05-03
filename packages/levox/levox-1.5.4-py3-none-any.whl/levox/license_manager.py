"""
License manager for Levox features (Freemium vs Pro).
"""
import os
import json
import uuid
import hashlib
import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# Feature flags
FEATURES = {
    "freemium": {
        "max_files": 100,                     # Maximum files to scan
        "max_reports": 3,                     # Maximum reports per month
        "advanced_detection": False,          # Advanced detection algorithms
        "fix_suggestions": True,              # Provide fix suggestions
        "auto_fix": False,                    # Auto-apply fixes
        "batch_processing": False,            # Process multiple directories
        "custom_rules": False,                # Custom compliance rules
        "export_formats": ["json"],           # Export formats
        "integrations": [],                   # External integrations
        "api_access": False,                  # API access
        "team_collaboration": False,          # Team collaboration features
        "on_prem_deployment": False,          # On-premises deployment
    },
    "pro": {
        "max_files": float('inf'),            # Unlimited files
        "max_reports": float('inf'),          # Unlimited reports
        "advanced_detection": True,           # Advanced detection algorithms
        "fix_suggestions": True,              # Provide fix suggestions
        "auto_fix": True,                     # Auto-apply fixes
        "batch_processing": True,             # Process multiple directories
        "custom_rules": True,                 # Custom compliance rules
        "export_formats": ["json", "csv", "pdf", "html"], # Export formats
        "integrations": ["github", "gitlab", "jira", "slack"], # Integrations
        "api_access": True,                   # API access
        "team_collaboration": True,           # Team collaboration features
        "on_prem_deployment": True,           # On-premises deployment
    },
    "enterprise": {
        "max_files": float('inf'),            # Unlimited files
        "max_reports": float('inf'),          # Unlimited reports
        "advanced_detection": True,           # Advanced detection algorithms
        "fix_suggestions": True,              # Provide fix suggestions
        "auto_fix": True,                     # Auto-apply fixes
        "batch_processing": True,             # Process multiple directories
        "custom_rules": True,                 # Custom compliance rules
        "export_formats": ["json", "csv", "pdf", "html", "xml"], # Export formats
        "integrations": ["github", "gitlab", "jira", "slack", "teams", "sso"], # Integrations
        "api_access": True,                   # API access
        "team_collaboration": True,           # Team collaboration features
        "on_prem_deployment": True,           # On-premises deployment
        "sla_support": True,                  # SLA support
        "training": True,                     # Training sessions
        "compliance_audit": True,             # Compliance audit services
    }
}


class LicenseManager:
    def __init__(self):
        """Initialize license manager."""
        self.license_file = os.path.expanduser("~/.levox/license.json")
        self.license_data = self._load_license()
        self.tier = self.license_data.get("tier", "freemium")
        
    def _load_license(self) -> Dict[str, Any]:
        """Load license data from file or create a new one."""
        try:
            license_dir = os.path.dirname(self.license_file)
            if not os.path.exists(license_dir):
                os.makedirs(license_dir)
                
            if os.path.exists(self.license_file):
                with open(self.license_file, 'r') as f:
                    return json.load(f)
            else:
                # Create a new freemium license
                license_data = {
                    "tier": "freemium",
                    "license_id": str(uuid.uuid4()),
                    "created_at": datetime.datetime.now().isoformat(),
                    "expires_at": None,
                    "usage": {
                        "files_scanned": 0,
                        "reports_generated": 0,
                        "last_report_month": datetime.datetime.now().strftime("%Y-%m"),
                        "monthly_reports": 0
                    }
                }
                self._save_license(license_data)
                return license_data
        except Exception as e:
            print(f"Error loading license: {e}")
            # Return default freemium license
            return {"tier": "freemium", "usage": {"files_scanned": 0, "reports_generated": 0}}
    
    def _save_license(self, license_data: Dict[str, Any]) -> bool:
        """Save license data to file."""
        try:
            license_dir = os.path.dirname(self.license_file)
            if not os.path.exists(license_dir):
                os.makedirs(license_dir)
                
            with open(self.license_file, 'w') as f:
                json.dump(license_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving license: {e}")
            return False
    
    def activate_license(self, license_key: str) -> bool:
        """Activate a pro/enterprise license with the provided key."""
        # In a real implementation, this would verify the license key with a server
        # For this demo, we'll use a simple validation approach
        
        try:
            # Simple validation (not secure, just for demo)
            if len(license_key) < 20:
                print("Invalid license key")
                return False
                
            # Validate key format (simplified)
            parts = license_key.split('-')
            if len(parts) != 5:
                print("Invalid license key format")
                return False
                
            # Determine tier from key (simplified)
            tier = "pro"
            if parts[0].startswith("ENT"):
                tier = "enterprise"
                
            # Create expiration date (1 year from now for demo)
            expires_at = (datetime.datetime.now() + datetime.timedelta(days=365)).isoformat()
            
            # Update license data
            self.license_data["tier"] = tier
            self.license_data["license_key"] = license_key
            self.license_data["activated_at"] = datetime.datetime.now().isoformat()
            self.license_data["expires_at"] = expires_at
            
            # Save updated license
            if self._save_license(self.license_data):
                self.tier = tier
                return True
            return False
        except Exception as e:
            print(f"Error activating license: {e}")
            return False
    
    def deactivate_license(self) -> bool:
        """Deactivate the current license and revert to freemium."""
        try:
            self.license_data["tier"] = "freemium"
            self.license_data.pop("license_key", None)
            self.license_data.pop("activated_at", None)
            self.license_data.pop("expires_at", None)
            
            if self._save_license(self.license_data):
                self.tier = "freemium"
                return True
            return False
        except Exception as e:
            print(f"Error deactivating license: {e}")
            return False
    
    def get_feature(self, feature_name: str) -> Any:
        """Get the value of a feature based on the current license tier."""
        if feature_name not in FEATURES.get(self.tier, {}):
            # Fall back to freemium if feature not found in current tier
            return FEATURES.get("freemium", {}).get(feature_name)
        
        return FEATURES.get(self.tier, {}).get(feature_name)
    
    def can_scan_files(self, file_count: int) -> bool:
        """Check if the current license allows scanning the given number of files."""
        max_files = self.get_feature("max_files")
        current_files = self.license_data["usage"]["files_scanned"]
        
        # If max_files is infinity (pro/enterprise), always return True
        if max_files == float('inf'):
            return True
            
        return current_files + file_count <= max_files
    
    def update_files_scanned(self, file_count: int) -> None:
        """Update the count of files scanned."""
        self.license_data["usage"]["files_scanned"] += file_count
        self._save_license(self.license_data)
    
    def can_generate_report(self) -> bool:
        """Check if the current license allows generating another report."""
        max_reports = self.get_feature("max_reports")
        
        # If max_reports is infinity (pro/enterprise), always return True
        if max_reports == float('inf'):
            return True
            
        # Check if we're in a new month
        current_month = datetime.datetime.now().strftime("%Y-%m")
        last_month = self.license_data["usage"].get("last_report_month")
        
        if current_month != last_month:
            # Reset monthly report count for new month
            self.license_data["usage"]["last_report_month"] = current_month
            self.license_data["usage"]["monthly_reports"] = 0
            self._save_license(self.license_data)
            
        monthly_reports = self.license_data["usage"]["monthly_reports"]
        return monthly_reports < max_reports
    
    def update_reports_generated(self) -> None:
        """Update the count of reports generated."""
        self.license_data["usage"]["reports_generated"] += 1
        
        # Update monthly reports
        current_month = datetime.datetime.now().strftime("%Y-%m")
        if current_month == self.license_data["usage"].get("last_report_month"):
            self.license_data["usage"]["monthly_reports"] += 1
        else:
            self.license_data["usage"]["last_report_month"] = current_month
            self.license_data["usage"]["monthly_reports"] = 1
            
        self._save_license(self.license_data)
    
    def get_license_info(self) -> Dict[str, Any]:
        """Get information about the current license."""
        info = {
            "tier": self.tier,
            "license_id": self.license_data.get("license_id"),
            "created_at": self.license_data.get("created_at"),
            "expires_at": self.license_data.get("expires_at"),
            "files_scanned": self.license_data["usage"]["files_scanned"],
            "reports_generated": self.license_data["usage"]["reports_generated"],
        }
        
        if self.tier != "freemium":
            info["activated_at"] = self.license_data.get("activated_at")
            
            # Calculate remaining days if license has expiration
            if info["expires_at"]:
                expires = datetime.datetime.fromisoformat(info["expires_at"])
                now = datetime.datetime.now()
                remaining = (expires - now).days
                info["days_remaining"] = max(0, remaining)
        
        return info
    
    def generate_trial_key(self, days: int = 30) -> str:
        """Generate a trial license key for Pro features."""
        # In a real implementation, this would involve server-side validation
        # For this demo, we'll use a simple generation approach
        
        trial_id = str(uuid.uuid4())
        expires = datetime.datetime.now() + datetime.timedelta(days=days)
        
        # Create trial key
        components = [
            "PRO-TRIAL",
            trial_id[:8],
            trial_id[9:13],
            expires.strftime("%Y%m%d"),
            hashlib.md5(trial_id.encode()).hexdigest()[:8]
        ]
        
        license_key = "-".join(components)
        return license_key 