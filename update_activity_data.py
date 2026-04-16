from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:1234@127.0.0.1:5432/SkillStack_v2")
conn = engine.connect()

print("=== Step 3: Updating activity data to generic names ===")

# Update activity names to generic and set base_token
# Also set has_sub_category based on whether they need sub-categories

activities_to_update = [
    # (old_name_pattern, new_name, base_token, has_sub_category)
    ("Hackathon%", "Hackathon", 3, 1),
    ("NPTEL%", "NPTEL", 2, 1),
    ("Coursera", "Coursera", 4, 0),
    ("Udemy", "Udemy", 3, 0),
    ("Workshop", "Workshop", 2, 0),
    ("Certification%", "Certification", 4, 1),
    ("Internship%", "Internship", 4, 1),
    ("Coding-Contest%", "Coding Contest", 3, 1),
    ("Study Abroad", "Study Abroad", 6, 0),
    ("Seed Funding%", "Seed Funding Project", 8, 0),
    ("Startup", "Startup", 12, 0),
    ("CGPA%", "CGPA", 4, 0),
    ("Cultural", "Cultural", 3, 0),
    ("Sports%", "Sports/Music", 3, 0),
    ("Volunteer%", "Volunteer Activities", 3, 0),
    ("Value Added%", "Value Added Courses", 4, 0),
    ("Other College%", "Other College Events", 3, 0),
    ("Organizing%", "Organizing Events", 2, 0),
    ("NCC/NSS%", "NCC/NSS Activities", 3, 0),
    ("Research%", "Research", 4, 1),
    ("Best Paper%", "Best Paper Award", 6, 0),
]

for pattern, new_name, base_token, has_sub in activities_to_update:
    if "%" in pattern:
        pattern = pattern.replace("%", "")
        result = conn.execute(
            text(f"""
            UPDATE activity 
            SET activity_name = :new_name, 
                base_token = :base_token, 
                has_sub_category = :has_sub,
                token = 0
            WHERE activity_name LIKE :pattern
        """),
            {
                "new_name": new_name,
                "base_token": base_token,
                "has_sub": has_sub,
                "pattern": f"{pattern}%",
            },
        )
    else:
        result = conn.execute(
            text(f"""
            UPDATE activity 
            SET activity_name = :new_name, 
                base_token = :base_token, 
                has_sub_category = :has_sub,
                token = 0
            WHERE activity_name = :pattern
        """),
            {
                "new_name": new_name,
                "base_token": base_token,
                "has_sub": has_sub,
                "pattern": pattern,
            },
        )

print("  Updated activities to generic names")

print("\n=== Step 4: Inserting activity categories ===")

# Clear existing categories
conn.execute(text("DELETE FROM activity_category"))

# Get activity IDs after update
result = conn.execute(text("SELECT id, activity_name FROM activity"))
activities = {row[1]: row[0] for row in result.fetchall()}

print(f"  Found activities: {activities}")

# Insert categories with prefix
categories = []

# Hackathon categories
if "Hackathon" in activities:
    categories.append((activities["Hackathon"], "Hackathon Participate", 0))
    categories.append((activities["Hackathon"], "Hackathon Internal Win", 1))
    categories.append((activities["Hackathon"], "Hackathon External Win", 3))

# NPTEL categories
if "NPTEL" in activities:
    categories.append((activities["NPTEL"], "NPTEL Pass", 0))
    categories.append((activities["NPTEL"], "NPTEL Elite+Silver", 1))
    categories.append((activities["NPTEL"], "NPTEL Elite+Gold", 2))

# Certification categories
if "Certification" in activities:
    categories.append((activities["Certification"], "Certification Internal/Local", 0))
    categories.append((activities["Certification"], "Certification Global", 2))

# Internship categories
if "Internship" in activities:
    categories.append((activities["Internship"], "Internship Online", 0))
    categories.append((activities["Internship"], "Internship InOffice", 2))

# Coding Contest categories
if "Coding Contest" in activities:
    categories.append((activities["Coding Contest"], "Coding Contest Participate", 0))
    categories.append((activities["Coding Contest"], "Coding Contest Winner", 2))

# Research categories
if "Research" in activities:
    categories.append((activities["Research"], "Research Working Prototype", 2))
    categories.append((activities["Research"], "Research Paper", 0))
    categories.append((activities["Research"], "Research Resource Person Internal", 0))
    categories.append((activities["Research"], "Research Resource Person External", 2))

# Insert categories
for activity_id, cat_name, extra_token in categories:
    conn.execute(
        text("""
        INSERT INTO activity_category (activity_id, category_name, extra_token, is_active)
        VALUES (:activity_id, :cat_name, :extra_token, 1)
    """),
        {"activity_id": activity_id, "cat_name": cat_name, "extra_token": extra_token},
    )

print(f"  Inserted {len(categories)} categories")

conn.commit()

# Verify
print("\n=== Verification ===")
result = conn.execute(
    text(
        "SELECT id, activity_name, base_token, has_sub_category FROM activity ORDER BY id"
    )
)
print("Activities:")
for row in result:
    print(f"  ID:{row[0]} | {row[1]} | base_token:{row[2]} | has_sub:{row[3]}")

result = conn.execute(
    text(
        "SELECT id, activity_id, category_name, extra_token FROM activity_category ORDER BY id"
    )
)
print("\nCategories:")
for row in result:
    print(f"  ID:{row[0]} | activity_id:{row[1]} | {row[2]} | +{row[3]}")

conn.close()
print("\n=== Done! ===")
