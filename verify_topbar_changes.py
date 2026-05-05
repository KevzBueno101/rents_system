#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rents_system.settings')
django.setup()

def verify_topbar_changes():
    """Verify that the topbar changes are properly implemented"""
    print("🔍 VERIFYING TOPBAR CHANGES")
    print("=" * 40)
    
    # Check the base dashboard template
    base_template_path = "c:/Users/kevin/rents_system/accounts/templates/base_dashboard.html"
    
    try:
        with open(base_template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key Bootstrap classes
        checks = [
            ("d-flex align-items-center flex-wrap", "Main flex container"),
            ("ms-auto d-flex align-items-center gap-2", "Right side positioning"),
            ("d-none d-md-flex align-items-center gap-1", "Date display"),
            ("position-relative", "Notification bell positioning"),
            ("btn btn-sm btn-outline-dark", "Logout button")
        ]
        
        print("\n✅ CHECKING BOOTSTRAP CLASSES:")
        all_found = True
        for class_name, description in checks:
            if class_name in content:
                print(f"   ✅ {description}: FOUND")
            else:
                print(f"   ❌ {description}: NOT FOUND")
                all_found = False
        
        if all_found:
            print("\n🎉 ALL BOOTSTRAP CLASSES FOUND!")
            print("   📱 Date, bell, and logout should be in top-right")
            print("   🔧 Using ms-auto for right positioning")
            print("   📱 Responsive with d-none d-md-flex")
        else:
            print("\n⚠️  SOME CLASSES MISSING")
        
        # Check specific structure
        if "<!-- PUSH RIGHT - TOP RIGHT COMPONENTS -->" in content:
            print("   ✅ Right section comment found")
        else:
            print("   ❌ Right section comment missing")
        
        if "<!-- Date Display -->" in content:
            print("   ✅ Date display section found")
        else:
            print("   ❌ Date display section missing")
            
    except Exception as e:
        print(f"❌ Error reading template: {e}")
    
    print("\n" + "=" * 40)
    print("📋 TROUBLESHOOTING STEPS:")
    print("   1. Clear browser cache (Ctrl+F5)")
    print("   2. Restart Django server")
    print("   3. Check browser developer tools")
    print("   4. Verify CSS files are loading")
    
    print("\n🚀 EXPECTED BEHAVIOR:")
    print("   📊 Admin dashboard topbar should show:")
    print("      - Left: Mobile menu + 'Dashboard' title")
    print("      - Right: Date + bell icon + logout button")
    print("   📱 On mobile: Date and logout text hidden")

if __name__ == "__main__":
    verify_topbar_changes()
