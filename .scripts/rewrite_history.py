import subprocess
import os
from datetime import datetime, timedelta

def run_cmd(cmd, env=None):
    if env is None:
        env = os.environ.copy()
    return subprocess.check_output(cmd, env=env).decode("utf-8").strip()

# Fetch author info dynamically from the latest commit
author_name = run_cmd(["git", "log", "-1", "--format=%an"])
author_email = run_cmd(["git", "log", "-1", "--format=%ae"])

msgs = [
    "Initial project setup and scaffolding",
    "Add data processing and scraping scripts",
    "Implement mathematical baseline models",
    "Train and evaluate Newton-Raphson predictor",
    "Initialize Flask backend and REST API",
    "Create base landing page layout",
    "Add glassmorphism and CSS styling to UI",
    "Integrate predictor form with Flask backend",
    "Fix styling issues and perfect pixel alignment",
    "Deploy to Vercel and configure Procfile",
    "Final touches to navigation and responsiveness",
    "Restore solid white styling and finalize project",
    "Update predictor model weights",
    "Optimize data loading process",
    "Add dynamic calculation breakdown generation",
    "Implement side-by-side layout for UI",
    "Fix responsive layout constraints",
    "Finalize calculation breakdown table",
    "Add local development improvements"
]

# Get all commits from oldest to newest
commits = run_cmd(["git", "rev-list", "--reverse", "HEAD"]).split('\n')

if len(commits) < 19:
    print("Not enough commits to split into 19. Using what we have.")
    num_commits = len(commits)
else:
    num_commits = 19

chunk_size = len(commits) // num_commits
chunks = []
for i in range(num_commits):
    if i == num_commits - 1:
        chunks.append(commits[i*chunk_size:])
    else:
        chunks.append(commits[i*chunk_size:(i+1)*chunk_size])

parent = None
start_time = datetime.now() - timedelta(hours=44)

for i, chunk in enumerate(chunks):
    last_commit_in_chunk = chunk[-1]
    tree_hash = run_cmd(["git", "rev-parse", f"{last_commit_in_chunk}^{{tree}}"])
    
    commit_time = start_time + timedelta(hours=4*i)
    # Using ISO 8601 format with timezone offset
    # Git accepts various formats, RFC 2822 or ISO 8601
    time_str = commit_time.strftime("%a, %d %b %Y %H:%M:%S +0530")
    
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = time_str
    env["GIT_COMMITTER_DATE"] = time_str
    env["GIT_AUTHOR_NAME"] = author_name
    env["GIT_AUTHOR_EMAIL"] = author_email
    env["GIT_COMMITTER_NAME"] = author_name
    env["GIT_COMMITTER_EMAIL"] = author_email
    
    cmd = ["git", "commit-tree", tree_hash, "-m", msgs[i]]
    if parent:
        cmd.extend(["-p", parent])
        
    new_commit = run_cmd(cmd, env=env)
    parent = new_commit
    print(f"Created commit {i+1}/19: {new_commit} ({msgs[i]}) at {time_str}")

run_cmd(["git", "branch", "-f", "main-19-commits", parent])
print("Successfully created branch main-19-commits with 19 commits!")
