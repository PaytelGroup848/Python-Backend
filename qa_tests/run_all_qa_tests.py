"""
Master Test Runner: Executes all QA test suites, outputs JUnit XML and JSON report
"""
import os
import sys
import time
import json
import unittest
import xml.etree.ElementTree as ET

# Ensure repo root and conftest are loaded
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import qa_tests.conftest

# Import test suites
from qa_tests.test_auth_unit import TestAuthAndTokens
from qa_tests.test_refresh_contracts import TestRefreshContracts
from qa_tests.test_logout_and_isolation import TestLogoutAndIsolation
from qa_tests.test_resilience_and_failures import TestResilienceAndFailures
from qa_tests.test_session_cleanup import TestSessionCleanup
from qa_tests.test_concurrency_load import TestConcurrencyLoad
from qa_tests.test_frontend_contracts import TestFrontendContracts
from qa_tests.test_bug_01_jwt_logging import TestBug01JwtLogging
from qa_tests.test_bug_02_assistant_authorization import TestBug02AssistantAuthorization
from qa_tests.test_bug_03_public_api import TestBug03PublicApi
from qa_tests.test_bug_04_upload_limits import TestBug04UploadLimits
from qa_tests.test_bug_05_websocket_auth import TestBug05WebSocketAuth
from qa_tests.test_bug_06_python_snippet import TestBug06PythonSnippet
from qa_tests.test_bug_07_reupload import TestBug07Reupload
from qa_tests.test_bug_08_ingestion_status import TestBug08IngestionStatus
from qa_tests.test_bug_09_api_key_refresh import TestBug09ApiKeyRefresh
from qa_tests.test_security_regression import TestSecurityRegression
from qa_tests.test_concurrency_regression import TestConcurrencyRegression
from qa_tests.test_case_insensitive_auth import TestCaseInsensitiveAuth


def run_suites():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()

    suite.addTests(loader.loadTestsFromTestCase(TestAuthAndTokens))
    suite.addTests(loader.loadTestsFromTestCase(TestRefreshContracts))
    suite.addTests(loader.loadTestsFromTestCase(TestLogoutAndIsolation))
    suite.addTests(loader.loadTestsFromTestCase(TestResilienceAndFailures))
    suite.addTests(loader.loadTestsFromTestCase(TestSessionCleanup))
    suite.addTests(loader.loadTestsFromTestCase(TestConcurrencyLoad))
    suite.addTests(loader.loadTestsFromTestCase(TestFrontendContracts))
    suite.addTests(loader.loadTestsFromTestCase(TestBug01JwtLogging))
    suite.addTests(loader.loadTestsFromTestCase(TestBug02AssistantAuthorization))
    suite.addTests(loader.loadTestsFromTestCase(TestBug03PublicApi))
    suite.addTests(loader.loadTestsFromTestCase(TestBug04UploadLimits))
    suite.addTests(loader.loadTestsFromTestCase(TestBug05WebSocketAuth))
    suite.addTests(loader.loadTestsFromTestCase(TestBug06PythonSnippet))
    suite.addTests(loader.loadTestsFromTestCase(TestBug07Reupload))
    suite.addTests(loader.loadTestsFromTestCase(TestBug08IngestionStatus))
    suite.addTests(loader.loadTestsFromTestCase(TestBug09ApiKeyRefresh))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityRegression))
    suite.addTests(loader.loadTestsFromTestCase(TestConcurrencyRegression))
    suite.addTests(loader.loadTestsFromTestCase(TestCaseInsensitiveAuth))

    def flatten_tests(suite_or_test):
        tests = []
        if isinstance(suite_or_test, unittest.TestSuite):
            for sub in suite_or_test:
                tests.extend(flatten_tests(sub))
        elif suite_or_test is not None and hasattr(suite_or_test, "id"):
            tests.append(suite_or_test)
        return tests

    all_test_cases = flatten_tests(suite)

    start_time = time.time()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    duration = time.time() - start_time

    total = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    passed = total - (failures + errors + skipped)

    # 1. Output machine-readable JSON
    reports_dir = os.path.join(REPO_ROOT, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    json_report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "duration_seconds": round(duration, 3),
        "total_tests": total,
        "passed": passed,
        "failed": failures + errors,
        "skipped": skipped,
        "blocked": 0,
        "results": []
    }

    # Record test names
    for test in all_test_cases:
        test_id = test.id()
        status = "PASSED"
        error_msg = ""
        for f in result.failures:
            if f[0] == test:
                status = "FAILED"
                error_msg = f[1]
        for e in result.errors:
            if e[0] == test:
                status = "ERROR"
                error_msg = e[1]

        json_report["results"].append({
            "test_id": test_id,
            "status": status,
            "error": error_msg[:500] if error_msg else None
        })

    json_path = os.path.join(reports_dir, "qa-results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_report, f, indent=2)

    # 2. Output JUnit XML
    testsuite_elem = ET.Element("testsuite", {
        "name": "Enterprise_QA_Suite",
        "tests": str(total),
        "failures": str(failures),
        "errors": str(errors),
        "skipped": str(skipped),
        "time": f"{duration:.3f}"
    })

    for r in json_report["results"]:
        tc_elem = ET.SubElement(testsuite_elem, "testcase", {
            "name": r["test_id"].split(".")[-1],
            "classname": ".".join(r["test_id"].split(".")[:-1])
        })
        if r["status"] == "FAILED":
            f_elem = ET.SubElement(tc_elem, "failure", {"message": "Test assertion failed"})
            f_elem.text = r["error"] or ""
        elif r["status"] == "ERROR":
            e_elem = ET.SubElement(tc_elem, "error", {"message": "Test execution error"})
            e_elem.text = r["error"] or ""

    xml_path = os.path.join(reports_dir, "junit.xml")
    tree = ET.ElementTree(testsuite_elem)
    tree.write(xml_path, encoding="utf-8", xml_declaration=True)

    print("\n" + "="*50)
    print("ENTERPRISE QA SUITE EXECUTION COMPLETED")
    print(f"JSON Report written to: {json_path}")
    print(f"JUnit XML written to:   {xml_path}")
    print(f"TOTAL: {total} | PASSED: {passed} | FAILED: {failures + errors} | SKIPPED: {skipped}")
    print("="*50)

    return 0 if (failures + errors) == 0 else 1


if __name__ == "__main__":
    sys.exit(run_suites())
