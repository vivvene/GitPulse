#!/usr/bin/env python3
"""
⚡ GitPulse CLI: Zero-Dollar Serverless Git Recovery & Telemetry Client
Can be run 100% offline (local engine fallback) or against a live AWS Lambda Function URL.
"""
import sys
import os
import subprocess
import json
import time
import argparse
import urllib.request
import tempfile
import shutil

# Reconfigure stdout for utf-8 on Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "backend", "src")))
try:
    from utils.git_graph import GitRecoveryEngine
    HAS_LOCAL_ENGINE = True
except ImportError:
    HAS_LOCAL_ENGINE = False


def find_git_binary() -> str:
    """Find git executable on system, checking standard Windows locations if not on PATH."""
    git_cmd = shutil.which("git")
    if git_cmd:
        return git_cmd
    standard_paths = [
        r"C:\Program Files\Git\cmd\git.exe",
        r"C:\Program Files\Git\bin\git.exe",
        r"C:\Program Files (x86)\Git\cmd\git.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Git\cmd\git.exe"),
    ]
    for p in standard_paths:
        if os.path.exists(p):
            return p
    return "git"

GIT_BIN = find_git_binary()

import shlex

def run_git(cmd: str, cwd: str = None) -> tuple[int, str]:
    """Execute git command and return (exit_code, output)."""
    try:
        args = [GIT_BIN] + shlex.split(cmd)
        proc = subprocess.run(
            args,
            shell=False,
            cwd=cwd or os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return proc.returncode, proc.stdout.strip()
    except Exception as e:
        return 1, str(e)


def detect_git_state(repo_path: str = None) -> dict:
    """Detect current repository health and failure states."""
    cwd = repo_path or os.getcwd()
    _, git_dir = run_git("rev-parse --git-dir", cwd=cwd)
    if not git_dir:
        return {"error": "Not a git repository."}

    # 1. Check HEAD commit
    _, head_commit = run_git("rev-parse HEAD", cwd=cwd)
    
    # 2. Check branch
    _, branch = run_git("branch --show-current", cwd=cwd)
    is_detached = False
    if not branch or branch == "":
        is_detached = True
        branch = "HEAD (Detached)"

    # 3. Check in-progress rebase or merge
    git_abs = os.path.join(cwd, git_dir) if not os.path.isabs(git_dir) else git_dir
    is_rebase = os.path.exists(os.path.join(git_abs, "rebase-merge")) or os.path.exists(os.path.join(git_abs, "rebase-apply"))
    is_merge = os.path.exists(os.path.join(git_abs, "MERGE_HEAD"))

    # 4. Reflog tail
    _, reflog = run_git("reflog -n 5 --oneline", cwd=cwd)
    reflog_lines = reflog.splitlines() if reflog else []

    # Determine state classification
    state_type = "HEALTHY"
    if is_rebase:
        state_type = "IN_PROGRESS_REBASE"
    elif is_merge:
        state_type = "MERGE_CONFLICT"
    elif is_detached:
        state_type = "DETACHED_HEAD"
    elif any("reset: moving to" in line for line in reflog_lines[:2]):
        state_type = "ACCIDENTAL_RESET"

    return {
        "repo_id": os.path.basename(os.path.abspath(cwd)),
        "state_type": state_type,
        "head_commit": head_commit,
        "branch_name": branch,
        "reflog_tail": reflog_lines,
        "author": os.environ.get("USER", os.environ.get("USERNAME", "developer"))
    }


def send_telemetry(payload: dict, function_url: str = None) -> dict:
    """Send telemetry to AWS Lambda Function URL or execute local fallback engine."""
    url = function_url or os.environ.get("GITPULSE_LAMBDA_URL")
    if url:
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=5) as res:
                return json.loads(res.read().decode("utf-8"))
        except Exception as e:
            print(f"⚠️ [GitPulse Cloud] Function URL request error ({e}). Falling back to local engine...")

    # Local Engine Fallback (100% Free, zero cloud dependency)
    if HAS_LOCAL_ENGINE:
        plan = GitRecoveryEngine.analyze(
            state_type=payload["state_type"],
            head_commit=payload["head_commit"],
            branch_name=payload["branch_name"],
            reflog_tail=payload["reflog_tail"]
        )
        return {
            "status": "SUCCESS (OFFLINE_ENGINE)",
            "incident_id": f"inc_local_{int(time.time())}",
            "recovery_plan": plan
        }
    else:
        return {"error": "No cloud URL configured and local recovery engine not found."}


def cli_status():
    """Print current repository status."""
    state = detect_git_state()
    if "error" in state:
        print(f"❌ {state['error']}")
        return

    print("\n🔍 GitPulse Repository Health Inspection")
    print("=" * 45)
    print(f"• Repository ID : {state['repo_id']}")
    print(f"• Active Branch : {state['branch_name']}")
    print(f"• HEAD Commit   : {state['head_commit'][:7] if state['head_commit'] else 'None'}")
    
    color = "\033[92m" if state['state_type'] == "HEALTHY" else "\033[91m"
    reset = "\033[0m"
    print(f"• State Status  : {color}{state['state_type']}{reset}")
    print("=" * 45)

    if state['state_type'] != "HEALTHY":
        print(f"⚠️ Anomaly detected! Run 'python gitpulse.py heal' to generate deterministic recovery.")
    else:
        print("✅ Repository is in clean working state.")


def cli_heal(function_url: str = None):
    """Diagnose git failure and output recovery script."""
    state = detect_git_state()
    if "error" in state:
        print(f"❌ {state['error']}")
        return

    print("\n🩺 GitPulse Diagnostic & Recovery Engine")
    print("=" * 50)
    print(f"Ingesting state: {state['state_type']} on branch '{state['branch_name']}'...")
    
    t0 = time.time()
    res = send_telemetry(state, function_url)
    elapsed_ms = int((time.time() - t0) * 1000)

    if "error" in res:
        print(f"❌ Error: {res['error']}")
        return

    plan = res.get("recovery_plan", {})
    steps = plan.get("steps", [])

    print(f"⚡ Recovery plan generated in {elapsed_ms}ms")
    print(f"• Safety Classification: {plan.get('safety_level', 'STANDARD')}")
    print(f"• Incident Reference   : {res.get('incident_id', 'local')}\n")

    print("📋 Deterministic Recovery Script:")
    print("-" * 50)
    for step in steps:
        print(f"[{step['step_number']}] {step['description']}")
        print(f"    \033[92m$ {step['command']}\033[0m\n")

    if plan.get("rollback_command"):
        print(f"🛡️ Emergency Rollback Command:\n    \033[93m$ {plan['rollback_command']}\033[0m")
    print("=" * 50)


def cli_demo():
    """Spin up an ephemeral sandbox repo, trigger an intentional disaster, and heal it."""
    temp_dir = tempfile.mkdtemp(prefix="gitpulse_demo_")
    print("\n🎬 Starting GitPulse Disaster & Recovery Demo (100% Offline & Free)")
    print("=" * 60)
    print(f"1. Initializing isolated sandbox repo at: {temp_dir}")
    
    run_git("init", cwd=temp_dir)
    run_git("config user.email 'demo@gitpulse.dev'", cwd=temp_dir)
    run_git("config user.name 'GitPulse Demo'", cwd=temp_dir)

    # Initial commits
    with open(os.path.join(temp_dir, "app.py"), "w") as f:
        f.write("print('Hello Hackathon!')\n")
    run_git("add .", cwd=temp_dir)
    run_git("commit -m 'Initial commit on main'", cwd=temp_dir)

    # Branch feature
    run_git("checkout -b feature-payment", cwd=temp_dir)
    with open(os.path.join(temp_dir, "payment.py"), "w") as f:
        f.write("# Critical payment logic\n")
    run_git("add .", cwd=temp_dir)
    run_git("commit -m 'feat: add payment pipeline'", cwd=temp_dir)

    # Trigger disaster: Detached HEAD on initial commit
    run_git("checkout --detach HEAD~1", cwd=temp_dir)
    
    print("2. 💥 Disaster Triggered: HEAD detached on prior commit!")
    state = detect_git_state(temp_dir)
    print(f"   Detected State: \033[91m{state['state_type']}\033[0m (Branch: {state['branch_name']})")
    print(f"   HEAD commit   : {state['head_commit'][:7]}")

    print("\n3. 🚀 Running GitPulse Deterministic Recovery Engine...")
    t0 = time.time()
    res = send_telemetry(state)
    elapsed = int((time.time() - t0) * 1000)
    
    plan = res.get("recovery_plan", {})
    print(f"   Plan synthesized in {elapsed}ms! Steps generated:")
    for step in plan.get("steps", []):
        print(f"   -> Step {step['step_number']}: {step['command']}")

    # Clean up sandbox
    shutil.rmtree(temp_dir, ignore_errors=True)
    print("\n✅ Sandbox cleaned. Demonstration complete!")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="GitPulse: Cloud-Synced Git Recovery & Telemetry Hub CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    subparsers.add_parser("status", help="Inspect current repository health")
    
    heal_parser = subparsers.add_parser("heal", help="Diagnose git failures and output recovery instructions")
    heal_parser.add_argument("--url", help="AWS Lambda Function URL endpoint", default=None)

    subparsers.add_parser("demo", help="Run interactive disaster and recovery simulation demo")

    args = parser.parse_args()
    if args.command == "status":
        cli_status()
    elif args.command == "heal":
        cli_heal(getattr(args, "url", None))
    elif args.command == "demo":
        cli_demo()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
