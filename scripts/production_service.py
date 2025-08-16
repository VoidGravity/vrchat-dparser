#!/usr/bin/env python3
"""
VRChat Analytics Production Service

This service combines analytics processing with email sending for production use.
Optimized for memory efficiency and includes PROD email formatting.

Usage:
    python scripts/production_service.py [--force-email]
    
Options:
    --force-email: Force send email regardless of 24-hour interval (for testing)
"""

import sys
import os
import argparse
from datetime import datetime

# Import our analytics and email modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from process_vrchat_analytics import main as run_analytics
    from email_service import main as run_email_service, should_send_email, load_email_config
except ImportError as e:
    print(f"Error importing required modules: {e}")
    sys.exit(1)


def main():
    """Main production service function."""
    parser = argparse.ArgumentParser(description='VRChat Analytics Production Service')
    parser.add_argument('--force-email', action='store_true', 
                       help='Force send email regardless of 24-hour interval')
    args = parser.parse_args()
    
    print("VRChat Analytics Production Service")
    print("===================================")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Run analytics processing (memory-optimized)
    print("\n[1/2] Running analytics processing...")
    analytics_result = run_analytics()
    
    if analytics_result != 0:
        print("Analytics processing failed. Aborting.")
        return analytics_result
    
    print("Analytics processing completed successfully.")
    
    # Step 2: Check if email should be sent
    print("\n[2/2] Checking email service...")
    
    if args.force_email:
        print("Force email flag set - sending email regardless of interval.")
        email_result = run_email_service()
    else:
        # Load email config to check timing
        email_config = load_email_config()
        
        if should_send_email(email_config):
            print("24-hour interval reached - sending analytics email.")
            email_result = run_email_service()
        else:
            print("24-hour interval not reached - skipping email.")
            email_result = 0
    
    if email_result == 0:
        print("\nProduction service completed successfully.")
    else:
        print("\nProduction service completed with email issues.")
    
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return email_result


if __name__ == "__main__":
    exit(main())