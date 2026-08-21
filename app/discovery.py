import json
from pathlib import Path

from playwright.sync_api import sync_playwright


# =========================================================
# Configuration
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

BASE_URL = "http://127.0.0.1:8000"

ARTIFACT_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "member_lookup.json"
)

DISCOVERY_LOG_DIR = (
    PROJECT_ROOT
    / "evidence"
    / "discovery"
)


# =========================================================
# Save artifact
# =========================================================

def save_artifact(artifact):

    ARTIFACT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        ARTIFACT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            artifact,
            file,
            indent=2
        )

    print(
        f"Artifact saved: {ARTIFACT_PATH}"
    )


# =========================================================
# Save discovery log
# =========================================================

def save_discovery_log(log):

    DISCOVERY_LOG_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    log_path = (
        DISCOVERY_LOG_DIR
        / "discovery_12345.json"
    )

    with open(
        log_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            log,
            file,
            indent=2
        )

    print(
        f"Discovery log saved: {log_path}"
    )


# =========================================================
# Discovery workflow
# =========================================================

def discover_member_lookup():

    member_id = "12345"

    print()
    print("===================================")
    print("DISCOVERY RUN")
    print("===================================")
    print(
        "Goal: Look up a member and return "
        "their savings balance."
    )
    print(
        f"Target: {BASE_URL}"
    )
    print(
        f"Member ID: {member_id}"
    )
    print("===================================")

    # -----------------------------------------------------
    # Artifact contract
    # -----------------------------------------------------

    artifact = {
        "artifact_version": "1.0",
        "capability": {
            "name": "member_lookup",
            "description": (
                "Look up a bank member and return "
                "their savings balance."
            ),
            "surface": "web"
        },
        "inputs": {
            "member_id": {
                "type": "string",
                "required": True,
                "description": (
                    "Unique bank member identifier."
                )
            }
        },
        "actions": [],
        "outputs": {
            "member_name": {
                "type": "string"
            },
            "savings_balance": {
                "type": "string"
            }
        },
        "success_condition": {
            "type": "all",
            "conditions": [
                "Member Details is visible",
                "Member identity is verified",
                "Savings balance is extracted"
            ]
        },
        "known_outcomes": [
            {
                "outcome": "MEMBER_NOT_FOUND",
                "category": "business_outcome",
                "trigger": "Member not found."
            },
            {
                "outcome": "SERVICE_FAILURE",
                "category": "application_failure",
                "trigger": "Member service unavailable."
            }
        ]
    }

    # -----------------------------------------------------
    # Discovery evidence log
    # -----------------------------------------------------

    discovery_log = {
        "goal": (
            "Look up a member and return "
            "their savings balance."
        ),
        "target": BASE_URL,
        "input": {
            "member_id": member_id
        },
        "status": "running",
        "observations": [],
        "actions": []
    }

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,
            slow_mo=1500
        )

        page = browser.new_page()

        try:

            # =================================================
            # Action 1 — Navigate
            # =================================================

            print()
            print("Action 1: Navigate to portal")

            page.goto(BASE_URL)

            discovery_log["observations"].append({
                "step": 1,
                "observation": (
                    "Bank Operations Portal "
                    "is available."
                )
            })

            discovery_log["actions"].append({
                "step": 1,
                "action": "navigate",
                "target": {
                    "type": "url",
                    "value": BASE_URL
                }
            })

            artifact["actions"].append({
                "id": "step_1",
                "action": "navigate",
                "target": {
                    "type": "url",
                    "value": BASE_URL
                },
                "description": (
                    "Open the Bank Operations Portal."
                )
            })

            # =================================================
            # Action 2 — Open Member Search
            # =================================================

            print(
                "Action 2: Open Member Search"
            )

            page.get_by_role(
                "button",
                name="Member Search"
            ).click()

            discovery_log["observations"].append({
                "step": 2,
                "observation": (
                    "Member Search button "
                    "is available."
                )
            })

            discovery_log["actions"].append({
                "step": 2,
                "action": "click",
                "target": {
                    "type": "role",
                    "role": "button",
                    "name": "Member Search"
                }
            })

            artifact["actions"].append({
                "id": "step_2",
                "action": "click",
                "target": {
                    "type": "role",
                    "role": "button",
                    "name": "Member Search"
                },
                "description": (
                    "Open the member search workflow."
                )
            })

            # =================================================
            # Action 3 — Enter member ID
            # =================================================

            print(
                "Action 3: Enter member ID"
            )

            page.get_by_label(
                "Member ID"
            ).fill(member_id)

            discovery_log["observations"].append({
                "step": 3,
                "observation": (
                    "Member ID input field "
                    "is available."
                )
            })

            discovery_log["actions"].append({
                "step": 3,
                "action": "fill",
                "target": {
                    "type": "label",
                    "value": "Member ID"
                },
                "input": "{{member_id}}"
            })

            artifact["actions"].append({
                "id": "step_3",
                "action": "fill",
                "target": {
                    "type": "label",
                    "value": "Member ID"
                },
                "input": "{{member_id}}",
                "description": (
                    "Enter the requested member ID."
                )
            })

            # =================================================
            # Action 4 — Search
            # =================================================

            print(
                "Action 4: Search for member"
            )

            page.get_by_role(
                "button",
                name="Search Member"
            ).last.click()

            discovery_log["observations"].append({
                "step": 4,
                "observation": (
                    "Search Member action "
                    "was accepted."
                )
            })

            discovery_log["actions"].append({
                "step": 4,
                "action": "click",
                "target": {
                    "type": "role",
                    "role": "button",
                    "name": "Search Member"
                }
            })

            artifact["actions"].append({
                "id": "step_4",
                "action": "click",
                "target": {
                    "type": "role",
                    "role": "button",
                    "name": "Search Member"
                },
                "description": (
                    "Submit the member search."
                )
            })

            # =================================================
            # Action 5 — Verify Member Details
            # =================================================

            print(
                "Action 5: Verify Member Details"
            )

            page.get_by_text(
                "Member Details",
                exact=True
            ).wait_for()

            discovery_log["observations"].append({
                "step": 5,
                "observation": (
                    "Member Details page "
                    "is visible."
                )
            })

            discovery_log["actions"].append({
                "step": 5,
                "action": "verify",
                "target": {
                    "type": "text",
                    "value": "Member Details"
                }
            })

            artifact["actions"].append({
                "id": "step_5",
                "action": "verify",
                "target": {
                    "type": "text",
                    "value": "Member Details"
                },
                "description": (
                    "Verify that the member details "
                    "view is displayed."
                )
            })

            # =================================================
            # Action 6 — Verify member identity
            # =================================================

            print(
                "Action 6: Verify member identity"
            )

            page.get_by_text(
                "Chukshith N",
                exact=True
            ).wait_for()

            discovery_log["observations"].append({
                "step": 6,
                "observation": (
                    "Member identity verified "
                    "as Chukshith N."
                )
            })

            discovery_log["actions"].append({
                "step": 6,
                "action": "verify",
                "target": {
                    "type": "text",
                    "value": "Chukshith N"
                }
            })

            artifact["actions"].append({
                "id": "step_6",
                "action": "verify",
                "target": {
                    "type": "text",
                    "value": "Chukshith N"
                },
                "description": (
                    "Verify the discovered member identity."
                )
            })

            # =================================================
            # Action 7 — Extract savings balance
            # =================================================

            print(
                "Action 7: Extract savings balance"
            )

            balance_element = page.locator(
                ".profile-field-value"
            ).filter(
                has_text="$"
            ).first

            balance_element.wait_for()

            balance = (
                balance_element.inner_text()
            )

            print(
                f"Savings balance found: "
                f"{balance}"
            )

            discovery_log["observations"].append({
                "step": 7,
                "observation": (
                    f"Savings balance observed: "
                    f"{balance}"
                )
            })

            discovery_log["actions"].append({
                "step": 7,
                "action": "extract",
                "target": {
                    "type": "css",
                    "value": ".profile-field-value"
                },
                "output": "savings_balance"
            })

            artifact["actions"].append({
                "id": "step_7",
                "action": "extract",
                "target": {
                    "type": "css",
                    "value": ".profile-field-value"
                },
                "output": "savings_balance",
                "description": (
                    "Extract the displayed "
                    "savings balance."
                )
            })

            # =================================================
            # Final checkpoint
            # =================================================

            print()
            print(
                "Verifying final success condition..."
            )

            page.get_by_text(
                "Member Details",
                exact=True
            ).wait_for()

            discovery_log["status"] = "success"

            discovery_log["outputs"] = {
                "member_name": "Chukshith N",
                "savings_balance": balance
            }

            # -------------------------------------------------
            # Save artifact
            # -------------------------------------------------

            save_artifact(
                artifact
            )

            # -------------------------------------------------
            # Save discovery evidence
            # -------------------------------------------------

            save_discovery_log(
                discovery_log
            )

            print()
            print("===================================")
            print("DISCOVERY SUCCESSFUL")
            print("===================================")
            print(
                "Capability: member_lookup"
            )
            print(
                f"Member ID: {member_id}"
            )
            print(
                "Member: Chukshith N"
            )
            print(
                f"Savings Balance: {balance}"
            )
            print("===================================")

        except Exception as error:

            discovery_log["status"] = "failure"
            discovery_log["error"] = str(error)

            save_discovery_log(
                discovery_log
            )

            print()
            print("===================================")
            print("DISCOVERY FAILED")
            print("===================================")
            print(
                f"Error: {error}"
            )
            print("===================================")

        finally:

            browser.close()


# =========================================================
# Entry point
# =========================================================

if __name__ == "__main__":
    discover_member_lookup()