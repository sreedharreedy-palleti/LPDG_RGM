What Is This Project Doing?
LPDG runs a radio network of around 320 gateways that collect smart meter readings. When a gateway silently fails, meters stop reporting.  
PDF
+ 1

A field technician visit costs €380.  
PDF

Leaving a broken gateway ignored costs €600 every week.  
PDF

The operations team can only dispatch 15 visits per week.  
PDF

Your program acts as the automated brain: it looks at telemetry data (disconnections, reboots, offline seconds) and picks the exact 15 gateways that need a visit most, for each of the 8 target weeks (120 visits total).  
PY
+ 2

How Every File in Your Folder Works Together
main.py (The Engine Driver): Starts the program. It checks if the data exists, runs the detection logic, creates the final predictions file, and tests the file to make sure it is valid.  
Unknown
+ 2

model.py (The Brain): Calculates which gateways are behaving abnormally compared to their normal 28-day baseline. It gives extra priority to repeated reboots and long offline times, ranking the top 15 each week.  
PY
+ 2

validate_submission.py (The Rule Checker): Checks that your output has exactly 120 rows, 5 correct columns, no missing scores, valid ranks 1 to 15, and clear reasons under 300 characters.  
PY

Dockerfile & docker-compose.yml (The Box): Packages your code so anyone can run it on their computer with one command without installing Python or libraries manually.  
YML
+ 2

tests/test_pipeline.py (The Unit Tests): Verifies that gateway IDs are formatted properly and that invalid inputs get caught.  
PY

DECISIONS.md & AI-USAGE.md (The Explanations): Explain why you built the system this way, where it can fail, and how you used AI tools responsibly.  
PDF

How the Evaluator Runs and Grades It
Step 1: One Command to Run

  
PDF

The evaluator runs:

Bash
docker compose up --build
  
MD


What they look for: The container must build without errors, find the data in ./data, run the calculations, and output ./output/predictions.csv.  
YML
+ 2

Step 2: Checking the Output File

  
PY
+ 1

The evaluator runs:

Bash
python validate_submission.py output/predictions.csv
  
PY


What they look for: It must print OK with zero errors. If this fails, the submission fails.  
PY
+ 1

Step 3: Checking Code Quality & Documentation

  
PDF

They look at your git commits to see if you committed changes step-by-step.  
PDF

They read DECISIONS.md to see your technical choices.  
PDF

They watch your 6–8 minute recording demonstrating the build and results.  
PDF