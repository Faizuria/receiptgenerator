import sqlite3
import json
from datetime import datetime
import sys

def check_user_access(discord_user_id):
    """
    Check if a Discord user has valid access based on the licenses table
    Returns: dict with access status and user info
    """
    try:
        # Connect to the database (use parent directory)
        import os
        db_path = os.path.join(os.path.dirname(__file__), '..', 'data.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if user exists in licenses table
        cursor.execute('SELECT owner_id, key, expiry, email FROM licenses WHERE owner_id = ?', (str(discord_user_id),))
        license_info = cursor.fetchone()
        
        if not license_info:
            return {
                'has_access': False,
                'message': 'No subscription found',
                'subscription_type': None,
                'expiry_date': None,
                'days_remaining': 0
            }
        
        owner_id, key, expiry_str, email = license_info
        
        # Parse expiry date
        try:
            expiry_date = datetime.strptime(expiry_str, "%d/%m/%Y %H:%M:%S")
            current_date = datetime.now()
            
            # Check if subscription has expired
            if current_date > expiry_date:
                return {
                    'has_access': False,
                    'message': 'Subscription expired',
                    'subscription_type': get_subscription_type(key),
                    'expiry_date': expiry_str,
                    'days_remaining': 0
                }
            
            # Calculate remaining days
            remaining_days = (expiry_date - current_date).days
            
            return {
                'has_access': True,
                'message': 'Access granted',
                'subscription_type': get_subscription_type(key),
                'expiry_date': expiry_str,
                'days_remaining': remaining_days,
                'email': email
            }
            
        except ValueError as e:
            return {
                'has_access': False,
                'message': f'Invalid expiry date format: {expiry_str}',
                'subscription_type': None,
                'expiry_date': expiry_str,
                'days_remaining': 0
            }
        
    except Exception as e:
        return {
            'has_access': False,
            'message': f'Database error: {str(e)}',
            'subscription_type': None,
            'expiry_date': None,
            'days_remaining': 0
        }
    finally:
        if 'conn' in locals():
            conn.close()

def get_subscription_type(key):
    """Extract subscription type from license key"""
    if key.startswith("1Day"):
        return "1 Day"
    elif key.startswith("3Day"):
        return "3 Days"
    elif key.startswith("5Day"):
        return "5 Days"
    elif key.startswith("1Week"):
        return "1 Week"
    elif key.startswith("1Month"):
        return "1 Month"
    elif key.startswith("LifetimeKey"):
        return "Lifetime"
    else:
        return "Unknown"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
        result = check_user_access(user_id)
        print(json.dumps(result))
    else:
        print(json.dumps({'error': 'No user ID provided'}))
