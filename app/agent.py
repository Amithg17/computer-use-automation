import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from playwright.sync_api import sync_playwright


# =========================================================
# CONFIGURATION
# =========================================================

load_dotenv()

BASE_URL = "http://127.0.0.1:8000"

MEMBER_ID = "12345"

MODEL = "gpt-5.4-mini"

MAX_ITERATIONS = 20

MAX_CONSECUTIVE_FAILURES = 3

# Human-in-the-loop settings. Set HUMAN_HANDOFF_TEST=1 to run a
# controlled demonstration of takeover/resume on the same browser session.
MAX_HUMAN_HANDOFFS = 2
HUMAN_HANDOFF_TEST = os.getenv("HUMAN_HANDOFF_TEST", "0") == "1"

SLOW_MO = 1200


PROJECT_ROOT = Path(__file__).resolve().parent.parent


ARTIFACT_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "member_lookup_agent.json"
)


EVIDENCE_DIR = (
    PROJECT_ROOT
    / "evidence"
    / "agent"
)


# =========================================================
# OPENAI CLIENT
# =========================================================

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:

    raise RuntimeError(
        "OPENAI_API_KEY was not found.\n"
        "Make sure your .env file contains:\n"
        "OPENAI_API_KEY=your_key"
    )


client = OpenAI(
    api_key=api_key
)


# =========================================================
# ALLOWED ACTIONS
# =========================================================

ALLOWED_ACTIONS = {
    "click",
    "fill",
    "verify",
    "extract",
    "finish",
}

# =========================================================
# SAFETY POLICY
# =========================================================
# Explicit allowlists keep the LLM constrained to the
# intended local application and workflow.

ALLOWED_ORIGIN = "http://127.0.0.1:8000"

ALLOWED_CLICK_BUTTONS = {
    "Member Search",
    "Search Member",
}

ALLOWED_FILL_LABELS = {
    "Member ID",
}

RISKY_ACTIONS = {
    "navigate",
    "submit",
    "delete",
    "purchase",
    "transfer",
    "send",
    "upload",
    "download",
    "login",
    "logout",
}

SAFETY_POLICY_VERSION = "1.0"


# =========================================================
# OBSERVE PAGE
# =========================================================

def observe_page(page):

    # -----------------------------------------------------
    # PAGE TEXT
    # -----------------------------------------------------

    try:

        visible_text = page.locator(
            "body"
        ).inner_text()

    except Exception:

        visible_text = ""


    # -----------------------------------------------------
    # BUTTONS
    # -----------------------------------------------------

    buttons = []

    try:

        button_locator = page.get_by_role(
            "button"
        )

        count = button_locator.count()

        for index in range(count):

            button = button_locator.nth(
                index
            )

            try:

                if (
                    button.is_visible()
                    and button.is_enabled()
                ):

                    name = (
                        button.inner_text()
                        .strip()
                    )

                    if name:
                        buttons.append(
                            name
                        )

            except Exception:

                continue

    except Exception:

        pass


    # -----------------------------------------------------
    # INPUTS
    # -----------------------------------------------------

    inputs = []

    try:

        input_locator = page.locator(
            "input"
        )

        count = input_locator.count()

        for index in range(count):

            element = input_locator.nth(
                index
            )

            try:

                if (
                    element.is_visible()
                    and element.is_enabled()
                    and element.is_editable()
                ):

                    inputs.append(
                        {
                            "type": element.get_attribute(
                                "type"
                            ),
                            "name": element.get_attribute(
                                "name"
                            ),
                            "id": element.get_attribute(
                                "id"
                            ),
                            "placeholder": element.get_attribute(
                                "placeholder"
                            ),
                            "aria_label": element.get_attribute(
                                "aria-label"
                            ),
                            "value": element.input_value()
                        }
                    )

            except Exception:

                continue

    except Exception:

        pass


    return {
        "url": page.url,
        "visible_text": visible_text[:10000],
        "buttons": buttons,
        "inputs": inputs
    }


# =========================================================
# NORMALIZE LLM DECISION
# =========================================================

def normalize_decision(decision):

    """
    Ensures the LLM output always has the same predictable
    structure.

    Empty strings are used for unused fields instead of
    None/null so the policy layer remains deterministic.
    """

    if not isinstance(
        decision,
        dict
    ):

        raise RuntimeError(
            "LLM decision is not a JSON object."
        )


    action = decision.get(
        "action",
        ""
    )


    target = decision.get(
        "target"
    )


    if not isinstance(
        target,
        dict
    ):

        target = {}


    normalized_target = {

        "type": str(
            target.get(
                "type",
                ""
            ) or ""
        ),

        "role": str(
            target.get(
                "role",
                ""
            ) or ""
        ),

        "name": str(
            target.get(
                "name",
                ""
            ) or ""
        ),

        "value": str(
            target.get(
                "value",
                ""
            ) or ""
        )
    }


    normalized = {

        "action": str(
            action or ""
        ),

        "target": normalized_target,

        "value": str(
            decision.get(
                "value",
                ""
            ) or ""
        ),

        "output": str(
            decision.get(
                "output",
                ""
            ) or ""
        ),

        "reason": str(
            decision.get(
                "reason",
                ""
            ) or ""
        )
    }


    return normalized


# =========================================================
# ASK LLM
# =========================================================

def ask_llm(
    goal,
    page_state,
    completed_actions
):

    prompt = f"""
You are controlling a browser to complete one simple
member lookup workflow.

USER GOAL:

{goal}


PREVIOUSLY COMPLETED ACTIONS:

{json.dumps(
    completed_actions,
    indent=2
)}


CURRENT PAGE:

URL:
{page_state["url"]}


VISIBLE BUTTONS:

{json.dumps(
    page_state["buttons"],
    indent=2
)}


VISIBLE EDITABLE INPUTS:

{json.dumps(
    page_state["inputs"],
    indent=2
)}


VISIBLE PAGE TEXT:

{page_state["visible_text"]}


=========================================================
IMPORTANT RULES
=========================================================

Return EXACTLY ONE action.

Never return two actions.

Never return an array.

Never return explanatory text outside the JSON object.

Use only the controls currently visible on the page.

Do not invent controls.

Do not repeat a successful action unnecessarily.

If Member ID already contains 12345, DO NOT fill it again.

After Member ID is entered, click Search Member.

After clicking Search Member, inspect the resulting page.

Do not choose finish until the member details and savings
balance have been successfully verified.


=========================================================
ACTION FORMAT
=========================================================

Every action must have exactly this structure:

{{
    "action": "...",
    "target": {{
        "type": "...",
        "role": "...",
        "name": "...",
        "value": "..."
    }},
    "value": "...",
    "output": "...",
    "reason": "..."
}}


=========================================================
CLICK
=========================================================

For a click:

target.type = "role"

target.role = "button"

target.name = the exact visible button name

target.value = ""

Example:

{{
    "action": "click",
    "target": {{
        "type": "role",
        "role": "button",
        "name": "Search Member",
        "value": ""
    }},
    "value": "",
    "output": "",
    "reason": "Click Search Member."
}}


=========================================================
FILL
=========================================================

For a fill:

target.type = "label"

target.value = the exact input label

value = the text to enter

target.role = ""

target.name = ""

Example:

{{
    "action": "fill",
    "target": {{
        "type": "label",
        "role": "",
        "name": "",
        "value": "Member ID"
    }},
    "value": "12345",
    "output": "",
    "reason": "Enter the requested member ID."
}}


=========================================================
VERIFY
=========================================================

For verification:

target.type = "text"

target.value = exact visible text

Example:

{{
    "action": "verify",
    "target": {{
        "type": "text",
        "role": "",
        "name": "",
        "value": "Chukshith N"
    }},
    "value": "",
    "output": "",
    "reason": "Verify the member identity."
}}


=========================================================
EXTRACT
=========================================================

For extraction:

target.type = "text"

target.value = exact visible text associated with
the requested value.

output = name of the output.

Example:

{{
    "action": "extract",
    "target": {{
        "type": "text",
        "role": "",
        "name": "",
        "value": "Savings"
    }},
    "value": "",
    "output": "savings_balance",
    "reason": "Extract the savings balance."
}}


=========================================================
FINISH
=========================================================

Only finish when the goal is complete.

Example:

{{
    "action": "finish",
    "target": {{
        "type": "",
        "role": "",
        "name": "",
        "value": ""
    }},
    "value": "",
    "output": "",
    "reason": "The member and savings balance have been verified."
}}


=========================================================
CURRENT TASK
=========================================================

Choose the SINGLE next action.
"""


    response = client.responses.create(

        model=MODEL,

        input=prompt,

        text={

            "format": {

                "type": "json_schema",

                "name": "browser_action",

                "strict": True,

                "schema": {

                    "type": "object",

                    "properties": {

                        "action": {

                            "type": "string",

                            "enum": [
                                "click",
                                "fill",
                                "verify",
                                "extract",
                                "finish"
                            ]
                        },

                        "target": {

                            "type": "object",

                            "properties": {

                                "type": {

                                    "type": "string",

                                    "enum": [
                                        "",
                                        "role",
                                        "label",
                                        "text"
                                    ]
                                },

                                "role": {

                                    "type": "string"
                                },

                                "name": {

                                    "type": "string"
                                },

                                "value": {

                                    "type": "string"
                                }
                            },

                            "required": [
                                "type",
                                "role",
                                "name",
                                "value"
                            ],

                            "additionalProperties": False
                        },

                        "value": {

                            "type": "string"
                        },

                        "output": {

                            "type": "string"
                        },

                        "reason": {

                            "type": "string"
                        }
                    },

                    "required": [
                        "action",
                        "target",
                        "value",
                        "output",
                        "reason"
                    ],

                    "additionalProperties": False
                }
            }
        }
    )


    raw_output = (
        response.output_text
        .strip()
    )


    print()
    print("-----------------------------------")
    print("LLM RAW RESPONSE")
    print("-----------------------------------")
    print(raw_output)
    print("-----------------------------------")


    # =====================================================
    # PARSE FIRST JSON OBJECT
    # =====================================================

    try:

        decoder = json.JSONDecoder()

        decision, end_position = (
            decoder.raw_decode(
                raw_output
            )
        )

    except json.JSONDecodeError as error:

        raise RuntimeError(
            "LLM returned invalid JSON.\n"
            f"Raw response:\n{raw_output}"
        ) from error


    decision = normalize_decision(
        decision
    )


    print()
    print(
        "PARSED ACTION:"
    )

    print(
        json.dumps(
            decision,
            indent=2
        )
    )


    return decision


# =========================================================
# SAFETY HELPERS
# =========================================================

def validate_page_origin(page):
    """Reject interaction if the browser leaves the approved origin."""
    current_url = page.url or ""

    if not current_url.startswith(ALLOWED_ORIGIN):
        return {
            "allowed": False,
            "reason": (
                "Browser is outside the approved origin: "
                f"{current_url}"
            ),
        }

    return {
        "allowed": True,
        "reason": "Page origin is approved.",
    }


def safety_policy_snapshot():
    """Return the explicit safety policy for evidence."""
    return {
        "version": SAFETY_POLICY_VERSION,
        "allowed_origin": ALLOWED_ORIGIN,
        "allowed_actions": sorted(ALLOWED_ACTIONS),
        "allowed_click_buttons": sorted(ALLOWED_CLICK_BUTTONS),
        "allowed_fill_labels": sorted(ALLOWED_FILL_LABELS),
        "risky_actions": sorted(RISKY_ACTIONS),
    }


# =========================================================
# VALIDATE ACTION
# =========================================================

def validate_action(
    page,
    decision
):

    action = decision.get(
        "action"
    )

    target = decision.get(
        "target",
        {}
    )

    # =====================================================
    # ORIGIN SAFETY CHECK
    # =====================================================

    origin_policy = validate_page_origin(page)

    if not origin_policy["allowed"]:
        return origin_policy


    # =====================================================
    # ACTION TYPE
    # =====================================================

    if action not in ALLOWED_ACTIONS:

        return {
            "allowed": False,
            "reason": (
                f"Unsupported action: {action}"
            )
        }


    # =====================================================
    # CLICK
    # =====================================================

    if action == "click":

        if target.get(
            "type"
        ) != "role":

            return {
                "allowed": False,
                "reason": (
                    "Click target must use "
                    "type='role'."
                )
            }


        if target.get(
            "role"
        ) != "button":

            return {
                "allowed": False,
                "reason": (
                    "Click target role must "
                    "be 'button'."
                )
            }


        button_name = target.get(
            "name",
            ""
        ).strip()


        if not button_name:

            return {
                "allowed": False,
                "reason": (
                    "Click target button name "
                    "is required."
                )
            }

        if button_name not in ALLOWED_CLICK_BUTTONS:

            return {
                "allowed": False,
                "reason": (
                    f"Button '{button_name}' is not "
                    "in the safety allowlist."
                )
            }


        locator = page.get_by_role(
            "button",
            name=button_name
        ).last


        try:

            if not locator.is_visible():

                return {
                    "allowed": False,
                    "reason": (
                        "Target button is not visible."
                    )
                }


            if not locator.is_enabled():

                return {
                    "allowed": False,
                    "reason": (
                        "Target button is disabled."
                    )
                }


        except Exception as error:

            return {
                "allowed": False,
                "reason": (
                    "Unable to inspect button: "
                    f"{error}"
                )
            }


        return {
            "allowed": True,
            "reason": "Click is allowed."
        }


    # =====================================================
    # FILL
    # =====================================================

    if action == "fill":

        if target.get(
            "type"
        ) != "label":

            return {
                "allowed": False,
                "reason": (
                    "Fill target must use "
                    "type='label'."
                )
            }


        label = target.get(
            "value",
            ""
        ).strip()


        if not label:

            return {
                "allowed": False,
                "reason": (
                    "Fill target label is required."
                )
            }

        if label not in ALLOWED_FILL_LABELS:

            return {
                "allowed": False,
                "reason": (
                    f"Input '{label}' is not in "
                    "the safety allowlist."
                )
            }


        fill_value = decision.get(
            "value",
            ""
        )


        if fill_value == "":

            return {
                "allowed": False,
                "reason": (
                    "Fill value is required."
                )
            }


        locator = page.get_by_label(
            label
        )


        try:

            if not locator.is_visible():

                return {
                    "allowed": False,
                    "reason": (
                        "Input is not visible."
                    )
                }


            if not locator.is_enabled():

                return {
                    "allowed": False,
                    "reason": (
                        "Input is disabled."
                    )
                }


            if not locator.is_editable():

                return {
                    "allowed": False,
                    "reason": (
                        "Input is not editable."
                    )
                }


            current_value = locator.input_value()


            if current_value == fill_value:

                return {
                    "allowed": False,
                    "reason": (
                        "Input already contains "
                        f"'{fill_value}'. "
                        "Do not fill it again."
                    )
                }


        except Exception as error:

            return {
                "allowed": False,
                "reason": (
                    "Unable to inspect input: "
                    f"{error}"
                )
            }


        return {
            "allowed": True,
            "reason": "Fill is allowed."
        }


    # =====================================================
    # VERIFY
    # =====================================================

    if action == "verify":

        if target.get(
            "type"
        ) != "text":

            return {
                "allowed": False,
                "reason": (
                    "Verify target must use "
                    "type='text'."
                )
            }


        text = target.get(
            "value",
            ""
        ).strip()


        if not text:

            return {
                "allowed": False,
                "reason": (
                    "Verification text is required."
                )
            }


        locator = page.get_by_text(
            text,
            exact=True
        )


        try:

            if not locator.is_visible():

                return {
                    "allowed": False,
                    "reason": (
                        "Verification text "
                        "is not visible."
                    )
                }


        except Exception as error:

            return {
                "allowed": False,
                "reason": (
                    "Unable to verify text: "
                    f"{error}"
                )
            }


        return {
            "allowed": True,
            "reason": "Verification is allowed."
        }


    # =====================================================
    # EXTRACT
    # =====================================================

    if action == "extract":

        if target.get(
            "type"
        ) != "text":

            return {
                "allowed": False,
                "reason": (
                    "Extract target must use "
                    "type='text'."
                )
            }


        text = target.get(
            "value",
            ""
        ).strip()


        if not text:

            return {
                "allowed": False,
                "reason": (
                    "Extraction target text "
                    "is required."
                )
            }


        if not decision.get(
            "output"
        ):

            return {
                "allowed": False,
                "reason": (
                    "Extraction output name "
                    "is required."
                )
            }


        locator = page.get_by_text(
            text,
            exact=False
        ).first


        try:

            if not locator.is_visible():

                return {
                    "allowed": False,
                    "reason": (
                        "Extraction target "
                        "is not visible."
                    )
                }


        except Exception as error:

            return {
                "allowed": False,
                "reason": (
                    "Unable to inspect "
                    "extraction target: "
                    f"{error}"
                )
            }


        return {
            "allowed": True,
            "reason": "Extraction is allowed."
        }


    # =====================================================
    # FINISH
    # =====================================================

    if action == "finish":

        if not verify_goal(page):

            return {
                "allowed": False,
                "reason": (
                    "Finish is blocked because the "
                    "final goal verification has not passed."
                )
            }

        return {
            "allowed": True,
            "reason": "Final goal verification passed."
        }


    return {
        "allowed": False,
        "reason": "Unknown action."
    }


# =========================================================
# EXECUTE ACTION
# =========================================================

def execute_action(
    page,
    decision
):

    action = decision.get(
        "action"
    )

    target = decision.get(
        "target",
        {}
    )


    # =====================================================
    # CLICK
    # =====================================================

    if action == "click":

        locator = page.get_by_role(
            "button",
            name=target["name"]
        ).last


        locator.click(
            timeout=5000
        )


        return {
            "status": "success",
            "action": "click",
            "target": target
        }


    # =====================================================
    # FILL
    # =====================================================

    if action == "fill":

        locator = page.get_by_label(
            target["value"]
        )


        locator.fill(
            decision["value"],
            timeout=5000
        )


        return {
            "status": "success",
            "action": "fill",
            "target": target,
            "value": decision["value"]
        }


    # =====================================================
    # VERIFY
    # =====================================================

    if action == "verify":

        locator = page.get_by_text(
            target["value"],
            exact=True
        )


        locator.wait_for(
            state="visible",
            timeout=5000
        )


        return {
            "status": "success",
            "action": "verify",
            "target": target
        }


    # =====================================================
    # EXTRACT
    # =====================================================

    if action == "extract":

        locator = page.get_by_text(
            target["value"],
            exact=False
        ).first


        locator.wait_for(
            state="visible",
            timeout=5000
        )


        extracted_text = (
            locator.inner_text()
        )


        return {
            "status": "success",
            "action": "extract",
            "target": target,
            "output": decision["output"],
            "value": extracted_text
        }


    # =====================================================
    # FINISH
    # =====================================================

    if action == "finish":

        return {
            "status": "finished",
            "action": "finish"
        }


    raise RuntimeError(
        f"Unsupported action: {action}"
    )


# =========================================================
# FINAL VERIFICATION
# =========================================================

def verify_goal(page):

    try:

        # -------------------------------------------------
        # Member Details
        # -------------------------------------------------

        page.get_by_text(
            "Member Details",
            exact=True
        ).wait_for(
            state="visible",
            timeout=5000
        )


        # -------------------------------------------------
        # Member name
        # -------------------------------------------------

        page.get_by_text(
            "Chukshith N",
            exact=True
        ).wait_for(
            state="visible",
            timeout=5000
        )


        # -------------------------------------------------
        # Savings information
        # -------------------------------------------------

        body_text = page.locator(
            "body"
        ).inner_text()


        savings_present = (
            "Savings" in body_text
            or "savings" in body_text
        )


        if not savings_present:

            return False


        return True


    except Exception:

        return False


# =========================================================
# HUMAN-IN-THE-LOOP HANDOFF
# =========================================================

def request_human_intervention(
    page,
    reason,
    iteration,
    decision,
    action_history,
    handoff_number
):
    """Pause the SAME live Playwright session for human takeover.

    The browser is intentionally not closed or recreated. The operator can
    interact with the visible browser window while this function waits on
    stdin. Pressing Enter records the handoff completion and lets the agent
    continue with the same page/session/context.
    """

    EVIDENCE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    screenshot_path = (
        EVIDENCE_DIR
        / f"human_handoff_{handoff_number}.png"
    )

    try:
        page.screenshot(
            path=str(screenshot_path),
            full_page=True
        )
    except Exception as error:
        screenshot_path = None
        print(f"Could not save handoff screenshot: {error}")

    handoff = {
        "type": "human_intervention",
        "status": "intervention_required",
        "iteration": iteration,
        "handoff_number": handoff_number,
        "reason": reason,
        "url": page.url,
        "decision": decision,
        "screenshot": str(screenshot_path) if screenshot_path else None
    }

    action_history.append(handoff)

    print()
    print("===================================")
    print("INTERVENTION REQUIRED")
    print("===================================")
    print(f"Reason: {reason}")
    print(f"Current URL: {page.url}")
    if screenshot_path:
        print(f"Handoff screenshot: {screenshot_path}")
    print()
    print("The SAME live browser session is paused for human control.")
    print("Use the open browser window to complete or correct the required action.")
    print("When finished, return to this terminal and press ENTER to resume.")
    print("===================================")

    input("Press ENTER after human intervention is complete: ")

    resume_state = observe_page(page)

    handoff["status"] = "resumed"
    handoff["resume_url"] = resume_state["url"]
    handoff["resume_observation"] = {
        "buttons": resume_state["buttons"],
        "inputs": resume_state["inputs"],
        "visible_text": resume_state["visible_text"][:2000]
    }

    print()
    print("===================================")
    print("HUMAN HANDOFF COMPLETE")
    print("===================================")
    print("Same browser session resumed.")
    print(f"Resume URL: {resume_state['url']}")
    print("===================================")

    return handoff


# =========================================================
# SAVE EVIDENCE
# =========================================================

def save_evidence(
    goal,
    action_history,
    final_state,
    status
):

    EVIDENCE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    evidence = {

        "run_type": "llm_discovery",

        "model": MODEL,

        "goal": goal,

        "status": status,

        "safety_policy": safety_policy_snapshot(),

        "actions": action_history,

        "final_state": final_state
    }


    evidence_path = (
        EVIDENCE_DIR
        / "agent_run_12345.json"
    )


    with open(
        evidence_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            evidence,
            file,
            indent=2
        )


    print()

    print(
        f"Agent evidence saved: "
        f"{evidence_path}"
    )


# =========================================================
# SAVE ARTIFACT
# =========================================================

def save_artifact(
    goal,
    action_history,
    final_state
):

    actions = []


    for item in action_history:

        decision = item.get(
            "decision",
            {}
        )

        result = item.get(
            "result",
            {}
        )


        if result.get(
            "status"
        ) != "success":

            continue


        action = decision.get(
            "action"
        )


        if action == "finish":

            continue


        artifact_action = {

            "id": (
                f"step_"
                f"{item['iteration']}"
            ),

            "action": action,

            "target": decision.get(
                "target"
            ),

            "description": decision.get(
                "reason",
                ""
            )
        }


        if action == "fill":

            value = decision.get(
                "value",
                ""
            )


            if value == MEMBER_ID:

                value = "{{member_id}}"


            artifact_action[
                "input"
            ] = value


        if action == "extract":

            artifact_action[
                "output"
            ] = decision.get(
                "output"
            )


        actions.append(
            artifact_action
        )


    artifact = {

        "artifact_version": "1.0",

        "generated_by": (
            "llm_discovery_agent"
        ),

        "capability": {

            "name": "member_lookup",

            "description": (
                "Look up a bank member "
                "and return their "
                "savings balance."
            ),

            "surface": "web"
        },

        "goal": goal,

        "inputs": {

            "member_id": {

                "type": "string",

                "required": True,

                "description": (
                    "Unique bank member "
                    "identifier."
                )
            }
        },

        "actions": actions,

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

                "Savings balance is present"
            ]
        },

        "discovery": {

            "model": MODEL,

            "target_url": BASE_URL,

            "final_url": final_state[
                "url"
            ],

            "safety_policy": safety_policy_snapshot()
        }
    }


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


    print()

    print(
        f"LLM artifact saved: "
        f"{ARTIFACT_PATH}"
    )


# =========================================================
# OFFLINE HUMAN-HANDOFF TEST
# =========================================================

def run_human_handoff_test():
    """Test pause/takeover/resume without making an LLM API call."""
    goal = "Demonstrate human takeover and resume on the same live browser session."
    action_history = []

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            slow_mo=SLOW_MO
        )
        page = browser.new_page()

        try:
            page.goto(
                BASE_URL,
                wait_until="domcontentloaded"
            )

            origin_check = validate_page_origin(page)
            if not origin_check["allowed"]:
                raise RuntimeError(origin_check["reason"])

            page.get_by_role(
                "button",
                name="Search Member"
            ).last.click(timeout=5000)

            handoff = request_human_intervention(
                page,
                (
                    "Offline controlled handoff test. "
                    "No LLM request is made. Take control of this "
                    "same browser session and complete the member lookup."
                ),
                1,
                {
                    "action": "human_handoff_test",
                    "target": {
                        "type": "",
                        "role": "",
                        "name": "",
                        "value": ""
                    },
                    "value": "",
                    "output": "",
                    "reason": "Offline handoff demonstration."
                },
                action_history,
                1
            )

            final_state = observe_page(page)

            evidence = {
                "run_type": "offline_human_handoff_test",
                "status": "success",
                "goal": goal,
                "safety_policy": safety_policy_snapshot(),
                "handoff": handoff,
                "same_browser_session": True,
                "resume_url": final_state["url"],
                "resume_observation": {
                    "buttons": final_state["buttons"],
                    "inputs": final_state["inputs"],
                    "visible_text": final_state["visible_text"][:2000]
                }
            }

            evidence_path = EVIDENCE_DIR / "human_handoff_test.json"

            with open(evidence_path, "w", encoding="utf-8") as file:
                json.dump(evidence, file, indent=2)

            print()
            print("===================================")
            print("HUMAN HANDOFF TEST SUCCESSFUL")
            print("===================================")
            print("No LLM API request was made.")
            print("Same browser session resumed successfully.")
            print(f"Evidence: {evidence_path}")
            print("===================================")

            return evidence

        except Exception as error:
            print()
            print("===================================")
            print("HUMAN HANDOFF TEST FAILED")
            print("===================================")
            print(f"Error: {error}")
            print("===================================")
            raise

        finally:
            browser.close()


# =========================================================
# MAIN AGENT
# =========================================================

def run_agent():


    goal = (
        "Look up member 12345 and "
        "return their current "
        "savings balance."
    )


    action_history = []


    completed_actions = []


    consecutive_failures = 0

    human_handoffs = 0


    print()

    print(
        "==================================="
    )

    print(
        "LLM-DRIVEN DISCOVERY"
    )

    print(
        "==================================="
    )

    print(
        f"Model: {MODEL}"
    )

    print(
        f"Goal: {goal}"
    )

    print(
        f"Target: {BASE_URL}"
    )

    print(
        "==================================="
    )


    with sync_playwright() as p:

        browser = p.chromium.launch(

            headless=False,

            slow_mo=SLOW_MO
        )


        page = browser.new_page()


        try:

            # -------------------------------------------------
            # Open application
            # -------------------------------------------------

            page.goto(
                BASE_URL,
                wait_until="domcontentloaded"
            )


            print()

            print(
                "Browser opened."
            )

            origin_check = validate_page_origin(page)

            if not origin_check["allowed"]:
                raise RuntimeError(
                    origin_check["reason"]
                )

            print(
                "Safety check: approved origin."
            )


            # -------------------------------------------------
            # Agent loop
            # -------------------------------------------------

            for iteration in range(
                1,
                MAX_ITERATIONS + 1
            ):

                print()

                print(
                    "==================================="
                )

                print(
                    f"ITERATION {iteration}"
                )

                print(
                    "==================================="
                )


                # =============================================
                # OBSERVE
                # =============================================

                page_state = observe_page(
                    page
                )


                print()

                print(
                    "OBSERVATION"
                )

                print(
                    f"URL: "
                    f"{page_state['url']}"
                )

                print(
                    f"Visible buttons: "
                    f"{page_state['buttons']}"
                )

                print(
                    f"Editable inputs: "
                    f"{page_state['inputs']}"
                )


                # =============================================
                # SAFETY: VERIFY CURRENT ORIGIN
                # =============================================

                origin_check = validate_page_origin(page)

                if not origin_check["allowed"]:
                    raise RuntimeError(
                        origin_check["reason"]
                    )

                # =============================================
                # DECIDE
                # =============================================

                decision = ask_llm(

                    goal,

                    page_state,

                    completed_actions
                )


                # =============================================
                # POLICY
                # =============================================

                policy = validate_action(

                    page,

                    decision
                )


                print()

                print(
                    "POLICY CHECK"
                )

                print(
                    f"Allowed: "
                    f"{policy['allowed']}"
                )

                print(
                    f"Reason: "
                    f"{policy['reason']}"
                )


                # =============================================
                # BLOCKED
                # =============================================

                if not policy[
                    "allowed"
                ]:

                    consecutive_failures += 1


                    print()

                    print(
                        "ACTION BLOCKED."
                    )

                    print(
                        f"Consecutive failures: "
                        f"{consecutive_failures}"
                    )


                    action_history.append(

                        {

                            "iteration": iteration,

                            "decision": decision,

                            "policy": policy,

                            "result": {

                                "status": "blocked"
                            }
                        }
                    )

                    # A blocked action is a safety boundary. Escalate to a
                    # human instead of repeatedly asking the model to retry.
                    if human_handoffs < MAX_HUMAN_HANDOFFS:

                        human_handoffs += 1

                        request_human_intervention(
                            page,
                            policy["reason"],
                            iteration,
                            decision,
                            action_history,
                            human_handoffs
                        )

                        consecutive_failures = 0
                        continue

                    raise RuntimeError(
                        "Maximum human handoffs reached after blocked actions."
                    )


                # =============================================
                # FINISH
                # =============================================

                if (
                    decision["action"]
                    == "finish"
                ):

                    print()

                    print(
                        "LLM requested FINISH."
                    )


                    verified = verify_goal(
                        page
                    )


                    if verified:

                        print(
                            "Final goal "
                            "verification PASSED."
                        )


                        action_history.append(

                            {

                                "iteration": iteration,

                                "decision": decision,

                                "policy": policy,

                                "result": {

                                    "status":
                                    "finished"
                                }
                            }
                        )


                        break


                    print(
                        "Final goal "
                        "verification FAILED."
                    )


                    consecutive_failures += 1


                    action_history.append(

                        {

                            "iteration": iteration,

                            "decision": decision,

                            "policy": policy,

                            "result": {

                                "status":
                                "finish_rejected"
                            }
                        }
                    )


                    if (
                        consecutive_failures
                        >= MAX_CONSECUTIVE_FAILURES
                    ):

                        raise RuntimeError(

                            "Agent attempted "
                            "to finish before "
                            "the goal was verified."
                        )


                    continue


                # =============================================
                # EXECUTE
                # =============================================

                try:

                    result = execute_action(

                        page,

                        decision
                    )


                    print()

                    print(
                        "ACTION EXECUTED"
                    )

                    print(
                        f"Status: "
                        f"{result['status']}"
                    )


                except Exception as error:

                    print()

                    print(
                        "ACTION EXECUTION FAILED"
                    )

                    print(
                        f"Error: {error}"
                    )


                    result = {

                        "status":
                        "execution_failed",

                        "error":
                        str(error)
                    }


                # =============================================
                # RECORD
                # =============================================

                action_history.append(

                    {

                        "iteration": iteration,

                        "decision": decision,

                        "policy": policy,

                        "result": result
                    }
                )


                # =============================================
                # UPDATE STATE
                # =============================================

                if (
                    result.get(
                        "status"
                    )
                    == "success"
                ):

                    consecutive_failures = 0


                    completed_actions.append(

                        {

                            "iteration":
                            iteration,

                            "action":
                            decision.get(
                                "action"
                            ),

                            "target":
                            decision.get(
                                "target"
                            ),

                            "value":
                            decision.get(
                                "value"
                            ),

                            "output":
                            decision.get(
                                "output"
                            )
                        }
                    )

                    # Controlled demonstration switch. This exercises the
                    # real same-session takeover/resume path without changing
                    # the normal production discovery behavior.
                    if (
                        HUMAN_HANDOFF_TEST
                        and human_handoffs == 0
                        and decision.get("action") != "finish"
                    ):

                        human_handoffs += 1

                        request_human_intervention(
                            page,
                            "Controlled human-handoff demonstration requested by HUMAN_HANDOFF_TEST=1.",
                            iteration,
                            decision,
                            action_history,
                            human_handoffs
                        )

                else:

                    consecutive_failures += 1


                    if (
                        consecutive_failures
                        >= MAX_CONSECUTIVE_FAILURES
                    ):

                        raise RuntimeError(

                            "Agent failed "
                            "to make progress."
                        )


            else:

                raise RuntimeError(

                    "Agent reached the "
                    "maximum number "
                    "of iterations."
                )


            # -------------------------------------------------
            # FINAL STATE
            # -------------------------------------------------

            final_state = observe_page(
                page
            )


            # -------------------------------------------------
            # FINAL VERIFICATION
            # -------------------------------------------------

            if not verify_goal(
                page
            ):

                save_evidence(

                    goal,

                    action_history,

                    final_state,

                    "goal_verification_failed"
                )


                raise RuntimeError(

                    "Final goal "
                    "verification failed."
                )


            # -------------------------------------------------
            # ARTIFACT
            # -------------------------------------------------

            save_artifact(

                goal,

                action_history,

                final_state
            )


            # -------------------------------------------------
            # EVIDENCE
            # -------------------------------------------------

            save_evidence(

                goal,

                action_history,

                final_state,

                "success"
            )


            print()

            print(
                "==================================="
            )

            print(
                "LLM DISCOVERY SUCCESSFUL"
            )

            print(
                "==================================="
            )

            print(
                f"Successful actions: "
                f"{len(completed_actions)}"
            )

            print(
                "Member: Chukshith N"
            )

            print(
                f"Artifact: "
                f"{ARTIFACT_PATH}"
            )

            print(
                "==================================="
            )


        except Exception as error:

            print()

            print(
                "==================================="
            )

            print(
                "LLM DISCOVERY FAILED"
            )

            print(
                "==================================="
            )

            print(
                f"Error: {error}"
            )

            print(
                "==================================="
            )


        finally:

            browser.close()


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    if HUMAN_HANDOFF_TEST:
        run_human_handoff_test()
    else:
        run_agent()