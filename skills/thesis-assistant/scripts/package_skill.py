#!/usr/bin/env python3
"""
Package script for thesis-assistant skill
Creates a .skill zip file from the skill directory
"""

import os
import zipfile
import shutil

SKILL_NAME = "thesis-assistant"
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = SKILL_DIR

def package_skill():
    skill_path = os.path.join(OUTPUT_DIR, f"{SKILL_NAME}.skill")

    with zipfile.ZipFile(skill_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(SKILL_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, OUTPUT_DIR)
                zipf.write(file_path, arcname)
                print(f"Added: {arcname}")

    print(f"\nSkill packaged successfully: {skill_path}")
    print(f"Size: {os.path.getsize(skill_path) / 1024:.2f} KB")

if __name__ == "__main__":
    package_skill()
