from levox.fixer import Fixer
from levox.scanner import GDPRIssue
import os

def test_fixer():
    """Test the Fixer class with a simple sample issue."""
    print("Testing Fixer class...")
    
    # Create a sample file with a potential GDPR issue
    test_file = "test_gdpr_issue.py"
    
    with open(test_file, "w") as f:
        f.write("""
# This is a test file with GDPR issues
def collect_user_data():
    user_data = {
        "name": input("Enter your name: "),
        "email": input("Enter your email: "),
        "address": input("Enter your address: "),
        "phone": input("Enter your phone number: ")
    }
    
    # Store data without validation or consent
    store_user_data(user_data)
    return user_data
""")
    
    # Create a sample GDPR issue
    issue = GDPRIssue(
        file_path=test_file,
        line_number=3,
        issue_type="pii_collection",
        description="Collecting personal data without proper consent mechanism",
        severity="high"
    )
    
    # Create a fixer instance
    fixer = Fixer(model_name="deepseek-r1:1.5b")
    
    # Check if model is available
    print(f"Checking if model is available...")
    model_available = fixer.check_model_availability()
    print(f"Model available: {model_available}")
    
    if model_available:
        # Generate a fix
        print(f"Generating fix for issue...")
        fix = fixer.generate_fix(issue)
        
        if fix:
            print(f"Generated fix: ")
            print("=" * 50)
            print(fix)
            print("=" * 50)
            
            # Try to apply the fix
            print(f"Applying fix...")
            result = fixer.apply_fix(issue, fix)
            print(f"Apply result: {result}")
            
            # Show the fixed file
            print(f"Fixed file content:")
            print("-" * 50)
            with open(test_file, "r") as f:
                print(f.read())
            print("-" * 50)
        else:
            print("Failed to generate fix")
    else:
        print("Model is not available")
    
    # Clean up
    try:
        os.remove(test_file)
        print(f"Removed test file: {test_file}")
    except:
        pass

if __name__ == "__main__":
    test_fixer() 