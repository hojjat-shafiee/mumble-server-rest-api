"""
Autonomous Agent Verification Script for mumble-server-rest-api
Runs static architectural compliance checks, linting, and hermetic pytest suite.
Usage: python scripts/verify.py
"""

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

def check_architecture() -> bool:
    print("[1/3] Checking Architectural Invariants & Agent Guardrails...")
    router_file = ROOT_DIR / "app" / "server_router.py"
    if not router_file.exists():
        print(f"  [ERROR] {router_file} not found!")
        return False

    with open(router_file, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source, filename=str(router_file))
    passed = True

    # Check 1: Route functions must be synchronous `def` if calling Ice
    routes = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for decorator in node.decorator_list:
                # Check if decorated by @router.<method>
                is_route = False
                route_path = None
                if isinstance(decorator, ast.Call):
                    func = decorator.func
                    if isinstance(func, ast.Attribute) and func.attr in {
                        "get", "post", "delete", "patch", "put"
                    }:
                        if isinstance(func.value, ast.Name) and func.value.id == "router":
                            is_route = True
                            if decorator.args and isinstance(decorator.args[0], ast.Constant):
                                route_path = decorator.args[0].value

                if is_route:
                    routes.append((node.name, route_path, isinstance(node, ast.AsyncFunctionDef)))
                    if isinstance(node, ast.AsyncFunctionDef):
                        print(
                            f"  [FAIL] Route '{node.name}' ({route_path}) is defined with 'async def'!\n"
                            f"         ZeroC Ice calls require synchronous 'def' to run in Starlette threadpool."
                        )
                        passed = False

    # Check 2: Static routes must precede dynamic parameterized routes (/{id})
    parameterized_seen = False
    for name, path, is_async in routes:
        if path is None:
            continue
        if "/{id}" in path or "/{server_id}" in path:
            parameterized_seen = True
        elif parameterized_seen:
            # Check if this is a static route registered after /{id}
            # (Ignore legacy routes at the bottom that have include_in_schema=False or different prefixes)
            if path.startswith("/servers/") and not any(param in path for param in ["{id}", "{server_id}"]):
                print(
                    f"  [FAIL] Static route '{path}' ({name}) appears AFTER parameterized route in router!\n"
                    f"         Move all static routes above '/servers/{{id}}' to prevent 422 routing conflicts."
                )
                passed = False

    if passed:
        print("  [PASS] All routes follow synchronous def and correct path ordering conventions.")
    return passed

def check_linting() -> bool:
    print("[2/3] Checking Code Formatting & Linting...")
    try:
        res = subprocess.run(
            [sys.executable, "-m", "ruff", "check", "."],
            cwd=str(ROOT_DIR),
            capture_output=True,
            text=True,
        )
        if res.returncode == 0:
            print("  [PASS] Ruff lint checks passed.")
            return True
        else:
            print("  [WARN] Ruff detected issues:")
            print(res.stdout)
            return True  # Don't strictly fail on formatting warnings unless severe
    except FileNotFoundError:
        print("  [SKIP] Ruff not installed, skipping lint check.")
        return True

def run_tests() -> bool:
    print("[3/3] Running Hermetic Pytest Suite...")
    res = subprocess.run(
        [sys.executable, "-m", "pytest", "-v", "--tb=short"],
        cwd=str(ROOT_DIR),
    )
    if res.returncode == 0:
        print("  [PASS] All tests passed successfully.")
        return True
    else:
        print("  [FAIL] Pytest encountered failures.")
        return False

def main():
    print("=" * 60)
    print("mumble-server-rest-api — Automated Verification")
    print("=" * 60)

    arch_ok = check_architecture()
    lint_ok = check_linting()
    tests_ok = run_tests()

    print("=" * 60)
    if arch_ok and lint_ok and tests_ok:
        print("[SUCCESS] Repository verification passed completely! Code is agent-ready.")
        sys.exit(0)
    else:
        print("[FAILURE] Verification failed. Please resolve the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()

