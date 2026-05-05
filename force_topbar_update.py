#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rents_system.settings')
django.setup()

def force_topbar_update():
    """Force update the topbar CSS and create a cache-busting solution"""
    print("🔄 FORCING TOPBAR UPDATE")
    print("=" * 40)
    
    # Update the CSS file with timestamp
    css_path = "c:/Users/kevin/rents_system/static/css/dashboard.css"
    
    try:
        with open(css_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add timestamp comment to force cache refresh
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Add timestamp at the top of the CSS
        updated_content = f"/* Cache-bust: {timestamp} */\n\n" + content
        
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"✅ CSS updated with timestamp: {timestamp}")
        
    except Exception as e:
        print(f"❌ Error updating CSS: {e}")
    
    # Check the base template structure
    template_path = "c:/Users/kevin/rents_system/accounts/templates/base_dashboard.html"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verify the key elements are present
        key_elements = [
            "ms-auto d-flex align-items-center gap-2",
            "Date Display",
            "Notification Bell", 
            "Logout Button"
        ]
        
        print("\n🔍 VERIFYING TEMPLATE STRUCTURE:")
        for element in key_elements:
            if element in content:
                print(f"   ✅ {element}: FOUND")
            else:
                print(f"   ❌ {element}: MISSING")
                
    except Exception as e:
        print(f"❌ Error reading template: {e}")
    
    print("\n" + "=" * 40)
    print("🚀 NEXT STEPS:")
    print("   1. Restart Django server: python manage.py runserver")
    print("   2. Clear browser cache: Ctrl + F5")
    print("   3. Check admin dashboard: http://127.0.0.1:8000/admin-dashboard/")
    print("   4. Verify topbar shows: Date + Bell + Logout on right side")
    
    print("\n📱 EXPECTED RESULT:")
    print("   📊 Admin dashboard topbar should show:")
    print("      Left: [☰] Dashboard")
    print("      Right: [📅 Date] [🔔 Bell] [🚪 Logout]")

if __name__ == "__main__":
    force_topbar_update()
