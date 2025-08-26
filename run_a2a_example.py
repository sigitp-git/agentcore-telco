#!/usr/bin/env python3
"""
Convenience script to run A2A examples from project root
"""

import subprocess
import sys
import os

def main():
    """Run the A2A integration example"""
    
    print("🌐 Running A2A Integration Example...")
    print("=" * 50)
    
    # Run the example script
    example_script = os.path.join("agent2agent", "examples", "a2a_integration_example_full.py")
    
    try:
        result = subprocess.run([
            sys.executable, example_script
        ], check=True, cwd=os.getcwd())
        
        print("\n✅ Example completed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Example failed with exit code {e.returncode}")
        sys.exit(e.returncode)
    except FileNotFoundError:
        print(f"❌ Example script not found: {example_script}")
        sys.exit(1)

if __name__ == "__main__":
    main()