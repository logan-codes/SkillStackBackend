#!/usr/bin/env python3
"""
Comprehensive API Test Script for SkillStack Backend
Outputs results to test_results.csv
"""

import csv
import time
import requests
from datetime import datetime
from typing import Optional

BASE_URL = "http://localhost:8000/api/v1"

# Test Data from Seed
TEST_USERS = {
    "student_a": {"email": "arun.kumar@college.edu", "id": 1, "name": "Arun Kumar"},
    "student_b": {"email": "rahul.verma@college.edu", "id": 3, "name": "Rahul Verma"},
    "teacher_a": {
        "email": "dr.ravi.krishna@college.edu",
        "id": 9,
        "name": "Dr. Ravi Krishna",
    },
    "teacher_b": {
        "email": "prof.meera.sen@college.edu",
        "id": 10,
        "name": "Prof. Meera Sen",
    },
}

tokens = {}
results = []
test_count = 0
pass_count = 0
fail_count = 0


def get_token(email: str) -> Optional[str]:
    """Login and get token"""
    resp = requests.post(f"{BASE_URL}/users/login", json={"email_id": email})
    if resp.status_code == 200:
        return resp.json()["access_token"]
    return None


def headers(token: Optional[str] = None):
    """Create headers with optional token"""
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def run_test(
    test_id: str,
    category: str,
    test_case: str,
    method: str,
    endpoint: str,
    token: Optional[str] = None,
    body: Optional[dict] = None,
    expected_status: int = 200,
):
    global test_count, pass_count, fail_count, results

    test_count += 1
    url = BASE_URL + endpoint
    elapsed = 0
    actual_status = 0
    status_str = "FAIL"
    resp_preview = ""

    start_time = time.time()
    try:
        if method == "GET":
            response = requests.get(url, headers=headers(token), timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers(token), json=body, timeout=10)
        elif method == "PUT":
            response = requests.put(url, headers=headers(token), json=body, timeout=10)
        elif method == "DELETE":
            response = requests.delete(
                url, headers=headers(token), json=body, timeout=10
            )
        else:
            raise Exception(f"Unknown method: {method}")

        elapsed = int((time.time() - start_time) * 1000)

        actual_status = response.status_code
        passed = actual_status == expected_status

        if passed:
            pass_count += 1
            status_str = "PASS"
        else:
            fail_count += 1
            status_str = "FAIL"

        resp_preview = str(response.text)[:100].replace("\n", " ").replace(",", ";")

    except Exception as e:
        elapsed = int((time.time() - start_time) * 1000)
        actual_status = 0
        passed = False
        status_str = "ERROR"
        resp_preview = str(e)[:100]

    results.append(
        {
            "Test_ID": test_id,
            "Category": category,
            "Test_Case": test_case,
            "Method": method,
            "Endpoint": endpoint,
            "Expected_Status": expected_status,
            "Actual_Status": actual_status,
            "Result": status_str,
            "Time_ms": elapsed,
            "Response": resp_preview,
        }
    )

    print(f"[{status_str}] {test_id}: {test_case} ({actual_status}, {elapsed}ms)")
    return passed, response if "response" in dir() else None


def main():
    global tokens

    print("=" * 70)
    print("SKILLSTACK API TEST SUITE")
    print("=" * 70)
    print(f"Started: {datetime.now()}")
    print()

    # Login all users
    print("Logging in users...")
    for key, user in TEST_USERS.items():
        token = get_token(user["email"])
        if token:
            tokens[key] = token
            print(f"  OK {user['name']} logged in")
        else:
            print(f"  FAIL {user['name']} login failed")
    print()

    # ========================================
    # A. AUTHENTICATION TESTS
    # ========================================
    print("A. AUTHENTICATION TESTS")
    print("-" * 50)

    # A1: Valid student login
    run_test(
        "A1",
        "Auth",
        "Student login valid",
        "POST",
        "/users/login",
        body={"email_id": "arun.kumar@college.edu"},
        expected_status=200,
    )

    # A2: Valid teacher login
    run_test(
        "A2",
        "Auth",
        "Teacher login valid",
        "POST",
        "/users/login",
        body={"email_id": "dr.ravi.krishna@college.edu"},
        expected_status=200,
    )

    # A3: Invalid email
    run_test(
        "A3",
        "Auth",
        "Login with invalid email",
        "POST",
        "/users/login",
        body={"email_id": "invalid@college.edu"},
        expected_status=404,
    )

    # A4: No token access
    run_test(
        "A4",
        "Auth",
        "Access without token",
        "GET",
        "/users/me",
        token=None,
        expected_status=403,
    )

    # A5: Invalid token
    run_test(
        "A5",
        "Auth",
        "Access with invalid token",
        "GET",
        "/users/me",
        token="invalid_token",
        expected_status=403,
    )

    print()

    # ========================================
    # B. STUDENT GOALS TESTS
    # ========================================
    print("B. STUDENT GOALS TESTS")
    print("-" * 50)

    # B1: Get activities
    run_test(
        "B1",
        "Goals",
        "GET activities for goals",
        "GET",
        "/goals/activities",
        token=tokens.get("student_a"),
        expected_status=200,
    )

    # B2: Create goals (valid - min 16 tokens)
    goals_body = {
        "activities": [
            {"activity_id": 1, "activity_name": "NPTEL-Pass", "tokens": 2},
            {"activity_id": 4, "activity_name": "Coursera", "tokens": 4},
            {"activity_id": 7, "activity_name": "Hackathon-Participate", "tokens": 3},
            {"activity_id": 11, "activity_name": "Organizing Events", "tokens": 2},
            {"activity_id": 17, "activity_name": "Internship-Online", "tokens": 4},
            {
                "activity_id": 22,
                "activity_name": "Coding-Contest-Participation",
                "tokens": 3,
            },
        ]
    }
    run_test(
        "B2",
        "Goals",
        "Create goals with 18 tokens",
        "POST",
        "/goals/",
        token=tokens.get("student_a"),
        body=goals_body,
        expected_status=201,
    )

    # B3: Create goals (invalid - below 16 tokens)
    goals_body_fail = {
        "activities": [
            {"activity_id": 1, "activity_name": "NPTEL-Pass", "tokens": 2},
            {"activity_id": 6, "activity_name": "Workshop", "tokens": 2},
        ]
    }
    run_test(
        "B3",
        "Goals",
        "Create goals below 16 tokens",
        "POST",
        "/goals/",
        token=tokens.get("student_a"),
        body=goals_body_fail,
        expected_status=400,
    )

    # B4: Get my goals
    run_test(
        "B4",
        "Goals",
        "GET my goals",
        "GET",
        "/goals/",
        token=tokens.get("student_a"),
        expected_status=200,
    )

    print()

    # ========================================
    # C. STUDENT ACTIVITIES WORKFLOW TESTS
    # ========================================
    print("C. STUDENT ACTIVITIES WORKFLOW")
    print("-" * 50)

    # C1: Get activities for workflow
    run_test(
        "C1",
        "Workflow",
        "GET activities for workflow",
        "GET",
        "/my-activities/activities",
        token=tokens.get("student_a"),
        expected_status=200,
    )

    # C2: Get categories for activity (NPTEL - id 1)
    run_test(
        "C2",
        "Workflow",
        "GET categories for NPTEL",
        "GET",
        "/my-activities/1/categories",
        token=tokens.get("student_a"),
        expected_status=200,
    )

    # C3: Start activity (valid)
    start_body = {"custom_name": "NPTEL Python", "student_goal_id": 1}
    run_test(
        "C3",
        "Workflow",
        "Start NPTEL activity",
        "POST",
        "/my-activities/1/start",
        token=tokens.get("student_a"),
        body=start_body,
        expected_status=201,
    )

    # C4: Start activity (invalid goal for activity)
    start_body_invalid = {
        "custom_name": "Workshop",
        "student_goal_id": 6,  # Workshop goal, but using Hackathon activity
    }
    run_test(
        "C4",
        "Workflow",
        "Start with invalid goal",
        "POST",
        "/my-activities/5/start",
        token=tokens.get("student_a"),
        body=start_body_invalid,
        expected_status=400,
    )

    # C5: Start duplicate activity
    run_test(
        "C5",
        "Workflow",
        "Start duplicate activity",
        "POST",
        "/my-activities/1/start",
        token=tokens.get("student_a"),
        body=start_body,
        expected_status=400,
    )

    # C6: Update activity (PENDING status - editable)
    update_body = {"custom_name": "NPTEL Python Updated"}
    run_test(
        "C6",
        "Workflow",
        "Update activity at PENDING",
        "PUT",
        "/my-activities/1",
        token=tokens.get("student_a"),
        body=update_body,
        expected_status=200,
    )

    # C7: Update with invalid dates
    update_body_dates = {"start_date": "2026-05-01", "end_date": "2026-04-01"}
    run_test(
        "C7",
        "Workflow",
        "Update with invalid dates",
        "PUT",
        "/my-activities/1",
        token=tokens.get("student_a"),
        body=update_body_dates,
        expected_status=400,
    )

    # C8: Submit proof (from ONGOING to SUBMITTED)
    proof_body = {"proof": "https://example.com/certificate.pdf", "student_goal_id": 1}
    run_test(
        "C8",
        "Workflow",
        "Submit proof",
        "PUT",
        "/my-activities/1/proof",
        token=tokens.get("student_a"),
        body=proof_body,
        expected_status=200,
    )

    # C9: Delete activity at PENDING
    run_test(
        "C9",
        "Workflow",
        "Delete activity at PENDING",
        "DELETE",
        "/my-activities",
        token=tokens.get("student_a"),
        body={"activity_ids": [2]},
        expected_status=200,
    )

    print()

    # ========================================
    # D. TEACHER REVIEW TESTS
    # ========================================
    print("D. TEACHER REVIEW TESTS")
    print("-" * 50)

    # First, student starts another activity for teacher to review
    start_body2 = {"custom_name": "Coursera Data Science", "student_goal_id": 4}
    requests.post(
        f"{BASE_URL}/my-activities/2/start",
        headers=headers(tokens.get("student_a")),
        json=start_body2,
    )
    # Teacher approves (status 1 -> 2)
    review_body = {"action": "approve"}
    run_test(
        "D1",
        "Teacher",
        "Approve at PENDING (1->2)",
        "POST",
        "/my-activities/3/teacher-review",
        token=tokens.get("teacher_a"),
        body=review_body,
        expected_status=200,
    )

    # Teacher approves (status 3 -> 4, adds tokens)
    review_body_approve = {"action": "approve"}
    run_test(
        "D2",
        "Teacher",
        "Approve at SUBMITTED (3->4)",
        "POST",
        "/my-activities/1/teacher-review",
        token=tokens.get("teacher_a"),
        body=review_body_approve,
        expected_status=200,
    )

    # Teacher rejects at PENDING (1 -> 5)
    review_body_reject1 = {"action": "reject"}
    run_test(
        "D3",
        "Teacher",
        "Reject at PENDING (1->5)",
        "POST",
        "/my-activities/4/teacher-review",
        token=tokens.get("teacher_a"),
        body=review_body_reject1,
        expected_status=200,
    )

    # Teacher rejects at Submitted (3 -> 2, needs reason)
    review_body_reject2_no_reason = {"action": "reject"}
    run_test(
        "D4",
        "Teacher",
        "Reject at Submitted without reason",
        "POST",
        "/my-activities/3/teacher-review",
        token=tokens.get("teacher_a"),
        body=review_body_reject2_no_reason,
        expected_status=400,
    )

    # Teacher rejects at Submitted with reason
    review_body_reject2 = {"action": "reject", "reason": "Certificate not clear"}
    run_test(
        "D5",
        "Teacher",
        "Reject at Submitted with reason",
        "POST",
        "/my-activities/3/teacher-review",
        token=tokens.get("teacher_a"),
        body=review_body_reject2,
        expected_status=200,
    )

    # Teacher cannot approve at ONGOING (2)
    review_body_approve_ongoing = {"action": "approve"}
    run_test(
        "D6",
        "Teacher",
        "Approve at ONGOING (should fail)",
        "POST",
        "/my-activities/3/teacher-review",
        token=tokens.get("teacher_a"),
        body=review_body_approve_ongoing,
        expected_status=400,
    )

    # Get teacher's students
    run_test(
        "D7",
        "Teacher",
        "GET teacher's students",
        "GET",
        "/my-activities/teacher/students",
        token=tokens.get("teacher_a"),
        expected_status=200,
    )

    # Get student profile
    run_test(
        "D8",
        "Teacher",
        "GET student profile",
        "GET",
        "/my-activities/teacher/students/1",
        token=tokens.get("teacher_a"),
        expected_status=200,
    )

    # Wrong teacher accessing student (Section B teacher accessing Section A student)
    run_test(
        "D9",
        "Teacher",
        "Unauthorized teacher access",
        "GET",
        "/my-activities/teacher/students/1",
        token=tokens.get("teacher_b"),
        expected_status=403,
    )

    # Get student activities by status
    run_test(
        "D10",
        "Teacher",
        "GET student activities by status",
        "GET",
        "/my-activities/teacher/students/1/activities",
        token=tokens.get("teacher_a"),
        expected_status=200,
    )

    print()

    # ========================================
    # E. TOKEN HISTORY TESTS
    # ========================================
    print("E. TOKEN HISTORY TESTS")
    print("-" * 50)

    # E1: Get my token summary
    run_test(
        "E1",
        "Tokens",
        "GET my token summary",
        "GET",
        "/users/tokens",
        token=tokens.get("student_a"),
        expected_status=200,
    )

    # E2: Get my token transactions
    run_test(
        "E2",
        "Tokens",
        "GET my transactions",
        "GET",
        "/users/tokens/transactions",
        token=tokens.get("student_a"),
        expected_status=200,
    )

    # E3: Teacher get student token summary
    run_test(
        "E3",
        "Tokens",
        "Teacher get student tokens",
        "GET",
        "/users/students/1/tokens",
        token=tokens.get("teacher_a"),
        expected_status=200,
    )

    # E4: Student cannot get other student tokens
    run_test(
        "E4",
        "Tokens",
        "Student get other student tokens",
        "GET",
        "/users/students/3/tokens",
        token=tokens.get("student_a"),
        expected_status=403,
    )

    print()

    # ========================================
    # F. LEADERBOARD TESTS
    # ========================================
    print("F. LEADERBOARD TESTS")
    print("-" * 50)

    # F1: Global leaderboard
    run_test(
        "F1",
        "Leaderboard",
        "GET global leaderboard",
        "GET",
        "/users/leaderboard",
        token=tokens.get("student_a"),
        expected_status=200,
    )

    # F2: Leaderboard with section filter
    run_test(
        "F2",
        "Leaderboard",
        "GET section A leaderboard",
        "GET",
        "/users/leaderboard?section=A",
        token=tokens.get("student_a"),
        expected_status=200,
    )

    # F3: Leaderboard with class coordinator filter
    run_test(
        "F3",
        "Leaderboard",
        "GET class coordinator leaderboard",
        "GET",
        "/users/leaderboard?class_coordinator_id=9",
        token=tokens.get("student_a"),
        expected_status=200,
    )

    # F4: My rank
    run_test(
        "F4",
        "Leaderboard",
        "GET my rank",
        "GET",
        "/users/leaderboard/me",
        token=tokens.get("student_a"),
        expected_status=200,
    )

    # F5: Class coordinator specific leaderboard
    run_test(
        "F5",
        "Leaderboard",
        "GET specific teacher leaderboard",
        "GET",
        "/users/leaderboard/class-coordinator/9",
        token=tokens.get("student_a"),
        expected_status=200,
    )

    print()

    # ========================================
    # G. SECURITY TESTS
    # ========================================
    print("G. SECURITY TESTS")
    print("-" * 50)

    # G1: Student cannot access teacher endpoints
    run_test(
        "G1",
        "Security",
        "Student access teacher students",
        "GET",
        "/my-activities/teacher/students",
        token=tokens.get("student_a"),
        expected_status=403,
    )

    # G2: Student cannot access admin endpoint
    run_test(
        "G2",
        "Security",
        "Student access users all",
        "GET",
        "/users/all",
        token=tokens.get("student_a"),
        expected_status=403,
    )

    # G3: Unassigned teacher cannot access student
    run_test(
        "G3",
        "Security",
        "Unassigned teacher access",
        "GET",
        "/my-activities/teacher/students/1",
        token=tokens.get("teacher_b"),
        expected_status=403,
    )

    # G4: Invalid activity ID
    run_test(
        "G4",
        "Security",
        "Invalid activity ID",
        "GET",
        "/my-activities/999/categories",
        token=tokens.get("student_a"),
        expected_status=404,
    )

    # G5: Invalid student goal ID
    run_test(
        "G5",
        "Security",
        "Invalid goal ID",
        "GET",
        "/goals/999",
        token=tokens.get("student_a"),
        expected_status=404,
    )

    print()

    # ========================================
    # H. MALPRACTICE TESTS
    # ========================================
    print("H. MALPRACTICE TESTS")
    print("-" * 50)

    # H1: Apply malpractice
    malpractice_body = {
        "malpractice_id": 1,
        "description": "Plagiarism detected in certificate",
    }
    run_test(
        "H1",
        "Malpractice",
        "Apply plagiarism",
        "POST",
        "/my-activities/teacher/students/1/malpractice",
        token=tokens.get("teacher_a"),
        body=malpractice_body,
        expected_status=200,
    )

    # H2: Get student malpractice history
    run_test(
        "H2",
        "Malpractice",
        "Get malpractice history",
        "GET",
        "/my-activities/teacher/students/1/malpractice",
        token=tokens.get("teacher_a"),
        expected_status=200,
    )

    # H3: Reverse malpractice
    run_test(
        "H3",
        "Malpractice",
        "Reverse malpractice",
        "POST",
        "/my-activities/teacher/students/1/malpractice/reverse-selected",
        token=tokens.get("teacher_a"),
        body=[1],
        expected_status=200,
    )

    print()

    # ========================================
    # WRITE CSV REPORT
    # ========================================
    print("Writing CSV report...")

    with open("test_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "Test_ID",
                "Category",
                "Test_Case",
                "Method",
                "Endpoint",
                "Expected_Status",
                "Actual_Status",
                "Result",
                "Time_ms",
                "Response",
            ],
        )
        writer.writeheader()
        writer.writerows(results)

    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {test_count}")
    print(f"Passed: {pass_count} PASS")
    print(f"Failed: {fail_count} FAIL")
    print(f"Success Rate: {(pass_count / test_count * 100):.1f}%")
    print(f"Completed: {datetime.now()}")
    print(f"Report saved to: test_results.csv")
    print("=" * 70)
    print(f"Total Tests: {test_count}")
    print(f"Passed: {pass_count} ✓")
    print(f"Failed: {fail_count} ✗")
    print(f"Success Rate: {(pass_count / test_count * 100):.1f}%")
    print(f"Completed: {datetime.now()}")
    print(f"Report saved to: test_results.csv")
    print("=" * 70)


if __name__ == "__main__":
    main()
