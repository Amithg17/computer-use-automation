# Computer Use Automation

## Overview

This project implements a browser-based member lookup workflow for a Bank Operations Portal.

The workflow accepts a member ID, searches for the member, verifies the member details, and returns the member's savings balance.

The project is divided into two main stages:

1. Workflow discovery
2. Deterministic replay

The discovered workflow is stored as a structured capability artifact and can then be executed repeatedly through the replay process.

## Workflow

The member lookup workflow follows these steps:

1. Open the Bank Operations Portal.
2. Open the Member Search page.
3. Enter the member ID.
4. Submit the search.
5. Verify that the member details are displayed.
6. Verify the member identity.
7. Extract the savings balance.

The application is available at:

http://127.0.0.1:8000

## Capability Artifact

The discovered workflow is stored in:

artifacts/member_lookup_agent.json

The capability contains:

- Capability name
- Required input
- Browser actions
- Action targets
- Expected outputs
- Success conditions
- Known runtime outcomes

The member lookup capability accepts:

member_id

and returns:

member_name

savings_balance

## Deterministic Replay

After the workflow has been discovered, it can be replayed using the saved capability artifact.

Run the following command for member 12345:

python app\replay.py 12345

The replay process executes the stored workflow through Playwright without requiring the workflow to be discovered again.

The member ID is provided as an input, allowing the same workflow to be tested with different members.

## Test Cases

The workflow has been tested using three member IDs.

### Member 12345

Command:

python app\replay.py 12345

Expected result:

Successful member lookup.

The member details and savings balance are returned.

### Member 99999

Command:

python app\replay.py 99999

Expected result:

MEMBER_NOT_FOUND

This represents a valid application response where the requested member does not exist.

### Member 50000

Command:

python app\replay.py 50000

Expected result:

SERVICE_FAILURE

This represents a failure reported by the member service.

These cases verify successful execution, an expected business result, and an application failure.

## Validation

Browser actions are checked before they are executed.

The workflow is restricted to the Bank Operations Portal:

http://127.0.0.1:8000

The member lookup workflow uses the following controls:

Member Search

Search Member

Member ID

The supported workflow actions are:

click

fill

verify

extract

finish

This keeps execution limited to the controls required by the member lookup workflow.

## Human Intervention

The project includes a controlled human intervention workflow.

When intervention is required, the browser session remains open so that a person can take control of the existing session.

The process is:

1. Pause the workflow.
2. Save the current execution state.
3. Allow the operator to use the open browser.
4. Complete the required action.
5. Resume execution using the same browser session.
6. Save the handoff evidence.

The controlled handoff test can be started with:

$env:HUMAN_HANDOFF_TEST="1"

python app\agent.py

Handoff evidence is stored under:

evidence/agent/

## Evidence

Execution records and screenshots are stored under the evidence directory.

The main directories are:

evidence/agent/

evidence/replay/

evidence/screenshots/

Replay results include:

evidence/replay/replay_12345.json

evidence/replay/replay_99999.json

evidence/replay/replay_50000.json

The evidence records the actions performed, execution results, screenshots, and runtime outcomes.

## Project Structure

computer-use-automation/

    app/
        agent.py
        replay.py

    artifacts/
        member_lookup_agent.json

    evidence/
        agent/
        replay/
        screenshots/

    README.md
    REPORT.md
    requirements.txt
    .gitignore

## Requirements

The project requires:

- Python 3.x
- Playwright
- The local Bank Operations Portal
- Required project dependencies

Install the dependencies with:

pip install -r requirements.txt

Install the Playwright browser with:

python -m playwright install

## Configuration

The project uses a local environment file for configuration.

The API key should be stored in the environment rather than directly in source code.

The .env file should not be committed to source control.

## Running the Application

Start the local Bank Operations Portal with:

python -m uvicorn app.main:app --reload

The application should then be available at:

http://127.0.0.1:8000

## Running the Workflow

Run workflow discovery with:

python app\agent.py

After the workflow has been successfully discovered, verify that the capability artifact exists:

artifacts/member_lookup_agent.json

Run the replay with:

python app\replay.py 12345

Additional test cases can be run with:

python app\replay.py 99999

python app\replay.py 50000

## Current Scope

The current implementation focuses on the member lookup workflow.

It includes:

- Browser workflow discovery
- Capability artifact creation
- Browser action validation
- Deterministic replay
- Runtime outcome handling
- Human intervention
- Execution evidence

The project does not currently provide general desktop automation, arbitrary website automation, distributed execution, or a production operator interface.

## Future Improvements

Possible future improvements include:

- Storing capabilities in a versioned registry instead of local JSON files
- Adding execution history and job management
- Adding retry and timeout handling
- Adding browser session recovery
- Adding capability versioning
- Adding better execution monitoring
- Supporting additional workflows

## Security

Credentials and configuration containing secrets must not be committed to source control.

Before submitting the project, verify that:

- API keys are not present in source files.
- The .env file is excluded from source control.
- Generated evidence does not contain sensitive credentials.
- The repository does not contain unnecessary sensitive information.

## Summary

The project provides a complete browser workflow for member lookup.

The workflow is discovered, saved as a capability, validated, and replayed through a deterministic execution process.

The implementation also handles successful lookups, member-not-found results, service failures, human intervention, and execution evidence.