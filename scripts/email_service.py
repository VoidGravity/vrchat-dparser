#!/usr/bin/env python3
"""
VRChat Analytics Email Service

This service handles scheduled email sending for VRChat analytics data.
Only sends emails after 24 hours have passed with full data and includes
PROD prefix in email subjects.

Usage:
    python scripts/email_service.py
"""

import os
import smtplib
import csv
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Try to import python-dotenv, fall back to defaults if not available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not found. Using default configuration.")


def load_email_config():
    """Load email configuration from environment variables."""
    config = {
        'SMTP_SERVER': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
        'SMTP_PORT': int(os.getenv('SMTP_PORT', '587')),
        'EMAIL_USERNAME': os.getenv('EMAIL_USERNAME', ''),
        'EMAIL_PASSWORD': os.getenv('EMAIL_PASSWORD', ''),
        'TO_EMAIL': os.getenv('TO_EMAIL', ''),
        'FROM_EMAIL': os.getenv('FROM_EMAIL', ''),
        'ANALYTICS_FILE': os.getenv('ANALYTICS_FILE', 'worlds_aggregated.csv'),
        'LAST_EMAIL_FILE': os.getenv('LAST_EMAIL_FILE', '.last_email_sent'),
        'EMAIL_INTERVAL_HOURS': int(os.getenv('EMAIL_INTERVAL_HOURS', '24'))
    }
    return config


def should_send_email(config):
    """
    Check if enough time has passed since the last email was sent.
    Only send emails after the configured interval (default 24 hours).
    """
    last_email_file = config['LAST_EMAIL_FILE']
    interval_hours = config['EMAIL_INTERVAL_HOURS']
    
    if not os.path.exists(last_email_file):
        return True
    
    try:
        with open(last_email_file, 'r') as f:
            last_sent_str = f.read().strip()
        
        last_sent = datetime.fromisoformat(last_sent_str)
        time_since_last = datetime.now() - last_sent
        
        return time_since_last >= timedelta(hours=interval_hours)
    except (ValueError, FileNotFoundError):
        return True


def update_last_email_time(config):
    """Update the timestamp of when the last email was sent."""
    with open(config['LAST_EMAIL_FILE'], 'w') as f:
        f.write(datetime.now().isoformat())


def get_analytics_summary(analytics_file):
    """
    Read the analytics CSV and create a summary for the email.
    Returns only essential information to avoid memory issues.
    """
    if not os.path.exists(analytics_file):
        return "Analytics file not found."
    
    try:
        with open(analytics_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            worlds = list(reader)
        
        if not worlds:
            return "No world data available."
        
        # Create a concise summary without memory-intensive statistics
        summary = f"""Analytics Summary:
        
Total Worlds Processed: {len(worlds)}
Data File: {analytics_file}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Top 3 Worlds by Average Occupants:"""
        
        # Only show top 3 to keep email concise
        for i, world in enumerate(worlds[:3], 1):
            name = world.get('world_name', 'Unknown')
            avg_occupants = world.get('average_occupants', '0')
            summary += f"\n{i}. {name}: {avg_occupants} avg occupants"
        
        return summary
        
    except Exception as e:
        return f"Error reading analytics data: {str(e)}"


def create_email_message(config, analytics_summary):
    """Create the email message with PROD prefix and analytics data."""
    today = datetime.now().strftime('%Y-%m-%d')
    subject = f"PROD Daily Analytics - {today}"
    
    msg = MIMEMultipart()
    msg['From'] = config['FROM_EMAIL']
    msg['To'] = config['TO_EMAIL']
    msg['Subject'] = subject
    
    # Email body with summary (not full statistics to save memory)
    body = f"""VRChat Analytics Report - {today}

{analytics_summary}

Full analytics data is attached as CSV file.

This email is sent automatically every {config['EMAIL_INTERVAL_HOURS']} hours.
"""
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach the CSV file if it exists
    if os.path.exists(config['ANALYTICS_FILE']):
        try:
            with open(config['ANALYTICS_FILE'], 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(config["ANALYTICS_FILE"])}'
            )
            msg.attach(part)
        except Exception as e:
            print(f"Warning: Could not attach analytics file: {e}")
    
    return msg


def send_email(config, message):
    """Send the email using SMTP."""
    try:
        server = smtplib.SMTP(config['SMTP_SERVER'], config['SMTP_PORT'])
        server.starttls()
        server.login(config['EMAIL_USERNAME'], config['EMAIL_PASSWORD'])
        
        text = message.as_string()
        server.sendmail(config['FROM_EMAIL'], config['TO_EMAIL'], text)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def main():
    """Main email service function."""
    print("VRChat Analytics Email Service")
    print("==============================")
    
    config = load_email_config()
    
    # Validate required configuration
    required_fields = ['EMAIL_USERNAME', 'EMAIL_PASSWORD', 'TO_EMAIL', 'FROM_EMAIL']
    missing_fields = [field for field in required_fields if not config[field]]
    
    if missing_fields:
        print(f"Error: Missing required email configuration: {', '.join(missing_fields)}")
        print("Please set the required environment variables.")
        return 1
    
    print(f"Checking if email should be sent (interval: {config['EMAIL_INTERVAL_HOURS']} hours)...")
    
    if not should_send_email(config):
        print("Email interval not reached. No email will be sent.")
        return 0
    
    print("24-hour interval reached. Preparing analytics email...")
    
    # Get analytics summary
    analytics_summary = get_analytics_summary(config['ANALYTICS_FILE'])
    
    # Create email message
    message = create_email_message(config, analytics_summary)
    
    # Send email
    print("Sending analytics email...")
    if send_email(config, message):
        update_last_email_time(config)
        print("Email sent successfully!")
        return 0
    else:
        print("Failed to send email.")
        return 1


if __name__ == "__main__":
    exit(main())