"""
Test Runner Script for Mobilise Test Tool
This script demonstrates how to run test generation programmatically
"""

from smart_test_engine import SmartTestEngine
import json

def run_test_generation(website_url, login_id="", password=""):
    """Run test generation for a website"""
    
    print("=" * 60)
    print("Mobilise Test Automation Tool - Test Runner")
    print("=" * 60)
    print(f"\nWebsite URL: {website_url}")
    if login_id:
        print(f"Login ID: {login_id}")
        print(f"Password: {'*' * len(password)}")
    print("\n" + "=" * 60)
    print("Starting test generation...")
    print("=" * 60 + "\n")
    
    # Initialize test engine
    engine = SmartTestEngine(website_url, login_id, password)
    
    try:
        # Generate all test cases
        test_cases = engine.generate_all_tests()
        
        # Save report
        report_file = engine.save_report()
        
        # Display summary
        print("\n" + "=" * 60)
        print("TEST GENERATION SUMMARY")
        print("=" * 60)
        print(f"\nTotal Test Cases Generated: {sum(len(tests) for tests in test_cases.values())}")
        print(f"  - Positive Tests: {len(test_cases['positive'])}")
        print(f"  - Negative Tests: {len(test_cases['negative'])}")
        print(f"  - UI Tests: {len(test_cases['ui'])}")
        print(f"  - Functional Tests: {len(test_cases['functional'])}")
        print(f"\nReport saved to: reports/{report_file}")
        
        # Display sample test cases
        print("\n" + "=" * 60)
        print("SAMPLE TEST CASES")
        print("=" * 60)
        
        # Show first positive test
        if test_cases['positive']:
            print("\n[POSITIVE TEST]")
            pos_test = test_cases['positive'][0]
            print(f"  Test ID: {pos_test['test_id']}")
            print(f"  Test Name: {pos_test['test_name']}")
            print(f"  Priority: {pos_test.get('priority', 'N/A')}")
        
        # Show first negative test
        if test_cases['negative']:
            print("\n[NEGATIVE TEST]")
            neg_test = test_cases['negative'][0]
            print(f"  Test ID: {neg_test['test_id']}")
            print(f"  Test Name: {neg_test['test_name']}")
            print(f"  Priority: {neg_test.get('priority', 'N/A')}")
        
        # Show first UI test
        if test_cases['ui']:
            print("\n[UI TEST]")
            ui_test = test_cases['ui'][0]
            print(f"  Test ID: {ui_test['test_id']}")
            print(f"  Test Name: {ui_test['test_name']}")
            print(f"  Priority: {ui_test.get('priority', 'N/A')}")
        
        # Show first functional test
        if test_cases['functional']:
            print("\n[FUNCTIONAL TEST]")
            func_test = test_cases['functional'][0]
            print(f"  Test ID: {func_test['test_id']}")
            print(f"  Test Name: {func_test['test_name']}")
            print(f"  Test Type: {func_test.get('test_type', 'N/A')}")
            print(f"  Priority: {func_test.get('priority', 'N/A')}")
            print(f"  Steps: {len(func_test.get('steps', []))} steps")
        
        print("\n" + "=" * 60)
        print("Test generation completed successfully!")
        print("=" * 60 + "\n")
        
        return test_cases, report_file
        
    except Exception as e:
        print(f"\n[ERROR] Test generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None
    finally:
        engine.close()


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        website_url = sys.argv[1]
        login_id = sys.argv[2] if len(sys.argv) > 2 else ""
        password = sys.argv[3] if len(sys.argv) > 3 else ""
    else:
        # Default test website
        print("Usage: python run_tests.py <website_url> [login_id] [password]")
        print("\nRunning with default test website...")
        website_url = "https://schoolerpbeta.mobilisepro.com/Admin/Login.php"
        login_id = ""
        password = ""
    
    run_test_generation(website_url, login_id, password)


