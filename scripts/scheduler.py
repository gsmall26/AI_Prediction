# Runs periodic checks using schedule library

import schedule
import time
import subprocess

def run_nlp():
    subprocess.run(["python", "scripts/nlp_extraction.py"])

def run_scoring():
    subprocess.run(["python", "scripts/outcome_retrieval.py"])

# Example: run NLP every minute, scoring every 2 minutes
schedule.every(1).minutes.do(run_nlp)
schedule.every(2).minutes.do(run_scoring)

print("Scheduler started. Ctrl+C to stop.")
while True:
    schedule.run_pending()
    time.sleep(1)
