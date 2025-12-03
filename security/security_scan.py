#!/usr/bin/env python3
"""
Security Scanning Script for AI Blog Generator

Runs multiple security checks:
- safety: Scans for known Python package vulnerabilities
- pip-audit: Alternative vulnerability scanner with better detection
- Generates JSON reports for CI/CD integration
"""

import subprocess
import json
import sys
from datetime import datetime
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success/failure."""
    print(f"\n🔍 {description}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print(f"✅ {description}: PASSED")
            return True, result.stdout
        else:
            print(f"⚠️  {description}: ISSUES FOUND")
            return False, result.stdout + result.stderr
    except Exception as e:
        print(f"❌ {description}: ERROR - {e}")
        return False, str(e)

def main():
    """Run all security checks."""
    print("=" * 70)
    print("🔒 AI Blog Generator - Security Vulnerability Scanning")
    print("=" * 70)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "scans": {}
    }
    
    all_passed = True
    
    # Run safety check
    passed, output = run_command("safety check --json", "Safety Check")
    report["scans"]["safety"] = {
        "passed": passed,
        "output": output[:500]  # Truncate for readability
    }
    all_passed = all_passed and passed
    
    # Run pip-audit
    passed, output = run_command("pip-audit --desc --format json", "Pip Audit")
    report["scans"]["pip_audit"] = {
        "passed": passed,
        "output": output[:500]
    }
    all_passed = all_passed and passed
    
    # Summary
    print("\n" + "=" * 70)
    print("SECURITY SCAN SUMMARY")
    print("=" * 70)
    
    for scan_name, result in report["scans"].items():
        status = "✅ PASSED" if result["passed"] else "⚠️  ISSUES FOUND"
        print(f"{scan_name}: {status}")
    
    # Save report
    report_path = Path("security_scan_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Full report saved to: {report_path}")
    
    # Exit code
    if all_passed:
        print("\n✅ All security scans passed!")
        return 0
    else:
        print("\n⚠️  Some security scans found issues. Review above.")
        print("Run individually for more details:")
        print("  safety check")
        print("  pip-audit --desc")
        return 1

if __name__ == "__main__":
    sys.exit(main())
