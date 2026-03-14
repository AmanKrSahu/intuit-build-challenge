"""
Pytest configuration and custom hooks for precise per-file logging.
Hooks intercept test outcomes to automatically dump formatted logs locally to `output/<module_name>.log`.
"""
import pytest
import os

# Dictionary to store logs grouped by test module name
module_logs = {}


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    report = outcome.get_result()

    # We only care about the actual execution call, not setup/teardown
    # unless a setup/teardown specifically collapsed.
    if report.when == "call" or (report.when in ("setup", "teardown") and report.failed):
        # Extract module name (e.g., 'test_analyzer')
        module_path = report.nodeid.split('::')[0]
        module_name = os.path.basename(module_path).replace('.py', '')

        if module_name not in module_logs:
            module_logs[module_name] = []

        test_func = report.nodeid.split('::')[-1]

        # Format the status ticks precisely
        if report.passed:
            status_mark = "✓ PASSED"
        elif report.failed:
            status_mark = "✗ FAILED"
        else:
            status_mark = "○ SKIPPED"

        log_entry = f"{status_mark} : {test_func}"

        # Include captured stdout context if printed by the test natively
        stdout = ""
        for secname, secval in report.sections:
            if "stdout" in secname:
                stdout += secval

        if stdout.strip():
            log_entry += f"\n  Output:\n    " + \
                "\n    ".join(stdout.strip().split('\n'))

        # Inject stacktrace exceptions if logic breaks
        if report.failed and report.longreprtext:
            log_entry += f"\n  Error:\n    " + \
                "\n    ".join(report.longreprtext.strip().split('\n'))

        module_logs[module_name].append({
            'status': report.passed,
            'text': log_entry
        })


def pytest_sessionfinish(session, exitstatus):
    """
    Hook called sequentially after whole test run finishes. 
    It cascades perfectly formatted summaries back directly to `output/<module_name>.log`.
    """
    os.makedirs("output", exist_ok=True)

    for module_name, logs in module_logs.items():
        log_file = os.path.join("output", f"{module_name}.log")

        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"{'='*80}\n")
            f.write(f"   TEST EXECUTION SUMMARY: {module_name}.py\n")
            f.write(f"{'='*80}\n\n")

            all_passed = True
            for log in logs:
                f.write(log['text'] + "\n\n")
                if not log['status']:
                    all_passed = False

            f.write(f"{'-'*80}\n")
            if all_passed and logs:
                f.write("✓ ALL TESTS PASSED SUCCESSFULLY\n")
            elif not logs:
                f.write("○ NO TESTS EXECUTED IN THIS MODULE\n")
            else:
                f.write("✗ SOME TESTS FAILED\n")
            f.write(f"{'-'*80}\n")
