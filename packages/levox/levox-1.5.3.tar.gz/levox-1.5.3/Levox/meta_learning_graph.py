#!/usr/bin/env python
"""
Meta-Learning Visualization Tool for Levox

This script creates graphs to visualize the improvements made by the meta-learning system
over time, showing how false positives are reduced and detection accuracy improves.
"""
import os
import json
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict

# Try to import from Levox package
try:
    from levox.meta_learning import MetaLearningEngine
except ImportError:
    # If running from local directory
    try:
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from levox.meta_learning import MetaLearningEngine
    except ImportError:
        print("Error: Could not import MetaLearningEngine. Make sure Levox is installed.")
        sys.exit(1)

class MetaLearningVisualizer:
    """
    Class to visualize meta-learning improvements over time.
    """
    def __init__(self):
        """Initialize the visualizer with meta-learning data."""
        self.ml_engine = MetaLearningEngine()
        self.stats_history_file = os.path.join(
            os.path.dirname(self.ml_engine.data_dir),
            "stats_history.json"
        )
        self.history = self._load_history()
        
    def _load_history(self) -> List[Dict[str, Any]]:
        """Load historical stats data from file."""
        if os.path.exists(self.stats_history_file):
            try:
                with open(self.stats_history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading history data: {e}")
                return []
        return []
    
    def _save_history(self):
        """Save current history to file."""
        try:
            with open(self.stats_history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"Error saving history data: {e}")
    
    def record_current_stats(self):
        """Record current meta-learning stats to history."""
        current_stats = self.ml_engine.get_learning_stats()
        
        # Add timestamp
        current_stats["timestamp"] = datetime.datetime.now().isoformat()
        
        # Add allowlist sizes
        allowlist = self.ml_engine.get_auto_allowlist()
        current_stats["allowlist_files"] = len(allowlist.get("files", []))
        current_stats["allowlist_patterns"] = len(allowlist.get("patterns", []))
        current_stats["allowlist_extensions"] = len(allowlist.get("extensions", []))
        
        # Add to history
        self.history.append(current_stats)
        
        # Save updated history
        self._save_history()
        
        print(f"Recorded meta-learning stats at {current_stats['timestamp']}")
        
    def plot_feedback_growth(self, output_file: str = None):
        """Plot growth of feedback records over time."""
        if not self.history or len(self.history) < 2:
            print("Not enough history data to create graphs. Please record stats regularly.")
            return
            
        # Extract data
        dates = [datetime.datetime.fromisoformat(entry["timestamp"]) for entry in self.history]
        feedback_counts = [entry["feedback_count"] for entry in self.history]
        fp_counts = [sum(entry.get("false_positive_counts", {}).values()) for entry in self.history]
        fn_counts = [sum(entry.get("false_negative_counts", {}).values()) for entry in self.history]
        
        # Create figure
        plt.figure(figsize=(10, 6))
        
        # Plot data
        plt.plot(dates, feedback_counts, 'b-', marker='o', label='Total Feedback')
        plt.plot(dates, fp_counts, 'r-', marker='s', label='False Positives')
        plt.plot(dates, fn_counts, 'g-', marker='^', label='False Negatives')
        
        # Format the plot
        plt.title("Growth of Meta-Learning Feedback Over Time")
        plt.xlabel("Date")
        plt.ylabel("Count")
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        
        # Format x-axis as dates
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.gcf().autofmt_xdate()
        
        # Save or show
        if output_file:
            plt.savefig(output_file)
            print(f"Graph saved to {output_file}")
        else:
            plt.show()
            
    def plot_allowlist_growth(self, output_file: str = None):
        """Plot growth of auto-allowlist items over time."""
        if not self.history or len(self.history) < 2:
            print("Not enough history data to create graphs. Please record stats regularly.")
            return
            
        # Extract data
        dates = [datetime.datetime.fromisoformat(entry["timestamp"]) for entry in self.history]
        files = [entry.get("allowlist_files", 0) for entry in self.history]
        patterns = [entry.get("allowlist_patterns", 0) for entry in self.history]
        extensions = [entry.get("allowlist_extensions", 0) for entry in self.history]
        
        # Create figure
        plt.figure(figsize=(10, 6))
        
        # Plot data
        plt.plot(dates, files, 'b-', marker='o', label='Files')
        plt.plot(dates, patterns, 'r-', marker='s', label='Patterns')
        plt.plot(dates, extensions, 'g-', marker='^', label='Extensions')
        
        # Format the plot
        plt.title("Growth of Auto-Allowlist Items Over Time")
        plt.xlabel("Date")
        plt.ylabel("Count")
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        
        # Format x-axis as dates
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.gcf().autofmt_xdate()
        
        # Save or show
        if output_file:
            plt.savefig(output_file)
            print(f"Graph saved to {output_file}")
        else:
            plt.show()
    
    def plot_issue_type_distribution(self, output_file: str = None):
        """Plot distribution of issue types in feedback."""
        if not self.history:
            print("No history data available. Please record stats first.")
            return
            
        # Use the most recent entry
        latest = self.history[-1]
        
        # Get issue types and their false positive counts
        issue_types = latest.get("issue_types", [])
        fp_counts = latest.get("false_positive_counts", {})
        
        if not issue_types or not fp_counts:
            print("No issue type data available in the latest stats.")
            return
            
        # Convert to lists for plotting
        types = list(fp_counts.keys())
        counts = list(fp_counts.values())
        
        # Create figure
        plt.figure(figsize=(12, 6))
        
        # Create horizontal bar chart
        y_pos = np.arange(len(types))
        plt.barh(y_pos, counts, align='center')
        plt.yticks(y_pos, types)
        
        # Format the plot
        plt.title("False Positives by Issue Type")
        plt.xlabel("Count")
        plt.tight_layout()
        
        # Save or show
        if output_file:
            plt.savefig(output_file)
            print(f"Graph saved to {output_file}")
        else:
            plt.show()
            
    def compare_scan_results(self, before_file: str, after_file: str, output_file: str = None):
        """
        Compare scan results before and after meta-learning.
        
        Args:
            before_file: JSON file with scan results before meta-learning
            after_file: JSON file with scan results after meta-learning
            output_file: Optional file to save the graph
        """
        # Load before and after data
        try:
            with open(before_file, 'r') as f:
                before_data = json.load(f)
                
            with open(after_file, 'r') as f:
                after_data = json.load(f)
        except Exception as e:
            print(f"Error loading scan results: {e}")
            return
            
        # Extract issues by type
        before_issues = defaultdict(int)
        after_issues = defaultdict(int)
        
        for issue in before_data.get("issues", []):
            before_issues[issue.get("issue_type", "unknown")] += 1
            
        for issue in after_data.get("issues", []):
            after_issues[issue.get("issue_type", "unknown")] += 1
            
        # Get union of all issue types
        all_types = set(list(before_issues.keys()) + list(after_issues.keys()))
        
        # Create lists for plotting
        types = list(all_types)
        before_counts = [before_issues.get(t, 0) for t in types]
        after_counts = [after_issues.get(t, 0) for t in types]
        
        # Create figure
        plt.figure(figsize=(12, 8))
        
        # Set up bar positions
        bar_width = 0.35
        r1 = np.arange(len(types))
        r2 = [x + bar_width for x in r1]
        
        # Create grouped bar chart
        plt.bar(r1, before_counts, width=bar_width, label='Before Meta-Learning', color='red', alpha=0.7)
        plt.bar(r2, after_counts, width=bar_width, label='After Meta-Learning', color='green', alpha=0.7)
        
        # Format the plot
        plt.title("Comparison of Issues Before and After Meta-Learning")
        plt.xlabel("Issue Type")
        plt.ylabel("Count")
        plt.xticks([r + bar_width/2 for r in range(len(types))], types, rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        
        # Save or show
        if output_file:
            plt.savefig(output_file)
            print(f"Graph saved to {output_file}")
        else:
            plt.show()

def main():
    """Main function to run the visualizer."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Visualize Levox Meta-Learning Improvements')
    parser.add_argument('--record', action='store_true', help='Record current meta-learning stats')
    parser.add_argument('--feedback', action='store_true', help='Plot feedback growth')
    parser.add_argument('--allowlist', action='store_true', help='Plot allowlist growth')
    parser.add_argument('--issues', action='store_true', help='Plot issue type distribution')
    parser.add_argument('--compare', nargs=2, metavar=('BEFORE_FILE', 'AFTER_FILE'), 
                        help='Compare scan results before and after meta-learning')
    parser.add_argument('--output', help='Output file for graph (optional)')
    
    args = parser.parse_args()
    
    visualizer = MetaLearningVisualizer()
    
    if args.record:
        visualizer.record_current_stats()
        
    if args.feedback:
        visualizer.plot_feedback_growth(args.output)
        
    if args.allowlist:
        visualizer.plot_allowlist_growth(args.output)
        
    if args.issues:
        visualizer.plot_issue_type_distribution(args.output)
        
    if args.compare:
        visualizer.compare_scan_results(args.compare[0], args.compare[1], args.output)
        
    # If no action specified, show help
    if not (args.record or args.feedback or args.allowlist or args.issues or args.compare):
        parser.print_help()

if __name__ == "__main__":
    main() 