"""
Behave Environment Configuration with Allure Reporting

This module configures the test environment for Behave BDD tests and sets up Allure reporting.
It handles test execution hooks and generates detailed test reports using Allure.

Requirements:
    - Python 3.7+
    - behave==1.2.6
    - allure-behave==2.13.2
    - allure-python-commons==2.13.2
    - Allure command-line tool version 2.33.0

Usage:
    1. Install dependencies:
       pip install -r requirements.txt

    2. Install Allure command-line tool:
       Windows (using Scoop): scoop install allure
       
    3. Run tests:
       behave tests/

    4. View reports:
       Reports will automatically open in your default browser after test execution
"""

from pathlib import Path
import sys
import os
import subprocess
import shutil
import atexit

# Add the parent directory to the path so we can import the modules
sys.path.append(str(Path(__file__).parent.parent))

from src.ecommerce.init_db import init_db

def find_allure_path():
    """
    Find the Allure executable path in common installation locations.
    
    Returns:
        str: Path to the Allure executable if found, None otherwise
    """
    # Common Allure installation paths on Windows
    possible_paths = [
        os.path.join(os.environ.get('USERPROFILE', ''), 'scoop', 'shims', 'allure.cmd'),
        os.path.join(os.environ.get('APPDATA', ''), 'npm', 'allure.cmd'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'npm', 'allure.cmd'),
        os.path.join(os.environ.get('PROGRAMFILES', ''), 'allure', 'bin', 'allure.bat'),
        os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'allure', 'bin', 'allure.bat'),
        'allure',
        'allure.cmd',
        'allure.bat'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def generate_allure_report():
    """
    Generate and open the Allure report.
    This function is registered to run after all tests complete.
    """
    try:
        # Find Allure executable
        allure_path = find_allure_path()
        if not allure_path:
            print("Allure not found. Please install Allure and ensure it's in your PATH.")
            return
        
        # Clean up old report directory
        if os.path.exists('allure-report'):
            shutil.rmtree('allure-report')
        
        print("\nGenerating fresh Allure report...")
        subprocess.run([allure_path, 'generate', 'allure-results', '-o', 'allure-report', '--clean'], check=True)
        
        print("Opening report in browser...")
        subprocess.Popen([allure_path, 'open', 'allure-report'])
    except Exception as e:
        print(f"Error generating report: {e}")

def before_all(context):
    """
    Run before all test scenarios.
    Sets up the test environment and initializes reporting.
    
    Args:
        context: Behave context object
    """
    context.config.setup_logging()
    
    # Initialize database
    init_db()
    
    # Clean and create allure-results directory
    if os.path.exists('allure-results'):
        shutil.rmtree('allure-results')
    os.makedirs('allure-results', exist_ok=True)
    
    # Create environment.properties with basic info
    with open('allure-results/environment.properties', 'w') as f:
        f.write(f'Python.Version={sys.version.split()[0]}\n')
        f.write('Framework=Behave\n')
        f.write('Language=Python\n')
    
    # Register the report generation to run after all tests
    atexit.register(generate_allure_report) 