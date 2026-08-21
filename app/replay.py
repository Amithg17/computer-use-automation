import json
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


# =========================================================
# Configuration
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

ARTIFACT_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "member_lookup_agent.json"
)

SCREENSHOT_DIR = (
    PROJECT_ROOT
    / "evidence"
    / "screenshots"
)

REPLAY_LOG_DIR = (
    PROJECT_ROOT
    / "evidence"
    / "replay"
)

BASE_URL = "http://127.0.0.1:8000"

SLOW_MO = 1500

TIMEOUT = 15000

RETRY_COUNT = 5


# =========================================================
# Utility
# =========================================================

def pause(seconds=1.0):
    time.sleep(seconds)


# =========================================================
# Load artifact
# =========================================================

def load_artifact():

    if not ARTIFACT_PATH.exists():
        raise FileNotFoundError(
            "Capability artifact was not found:\n"
            f"{ARTIFACT_PATH}"
        )

    with open(
        ARTIFACT_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


# =========================================================
# Save replay log
# =========================================================

def save_replay_log(log):

    REPLAY_LOG_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    member_id = log["member_id"]

    log_path = (
        REPLAY_LOG_DIR
        / f"replay_{member_id}.json"
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
        f"Replay log saved: {log_path}"
    )


# =========================================================
# Save screenshot
# =========================================================

def save_screenshot(
    page,
    filename
):

    SCREENSHOT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    path = (
        SCREENSHOT_DIR
        / filename
    )

    try:

        page.screenshot(
            path=str(path),
            full_page=True
        )

        print(
            f"Screenshot saved: {path}"
        )

        return str(path)

    except Exception as error:

        print(
            f"Could not save screenshot: "
            f"{error}"
        )

        return None


# =========================================================
# Print page state
# =========================================================

def print_page_state(page):

    print()
    print("-----------------------------------")
    print("CURRENT PAGE STATE")
    print("-----------------------------------")
    print(
        f"URL: {page.url}"
    )

    try:

        text = page.locator(
            "body"
        ).inner_text()

        print("PAGE TEXT:")
        print(text[:4000])

    except Exception as error:

        print(
            f"Could not read page text: "
            f"{error}"
        )

    try:

        buttons = page.locator(
            "button"
        )

        count = buttons.count()

        print()
        print(
            f"BUTTON COUNT: {count}"
        )

        for index in range(
            min(count, 20)
        ):

            try:

                button = buttons.nth(
                    index
                )

                if button.is_visible():

                    print(
                        f"  BUTTON {index}: "
                        f"{button.inner_text().strip()}"
                    )

            except Exception:

                pass

    except Exception:

        pass

    print("-----------------------------------")


# =========================================================
# Get all frames
# =========================================================

def get_all_frames(page):

    frames = []

    try:

        frames.append(
            page.main_frame
        )

        for frame in page.frames:

            if frame not in frames:

                frames.append(frame)

    except Exception:

        pass

    return frames


# =========================================================
# Find Member Search button
# =========================================================

def find_member_search_button(page):

    print(
        "Searching for Member Search button..."
    )

    # -----------------------------------------------------
    # Strategy 1: role
    # -----------------------------------------------------

    for attempt in range(
        RETRY_COUNT
    ):

        try:

            locator = page.get_by_role(
                "button",
                name="Member Search"
            ).last

            if (
                locator.is_visible()
                and locator.is_enabled()
            ):

                print(
                    "Found Member Search "
                    "using role locator."
                )

                return locator

        except Exception:

            pass

        pause(0.5)


    # -----------------------------------------------------
    # Strategy 2: exact text
    # -----------------------------------------------------

    try:

        locator = page.get_by_text(
            "Member Search",
            exact=True
        ).last

        if (
            locator.is_visible()
            and locator.is_enabled()
        ):

            print(
                "Found Member Search "
                "using text locator."
            )

            return locator

    except Exception:

        pass


    # -----------------------------------------------------
    # Strategy 3: CSS button
    # -----------------------------------------------------

    try:

        buttons = page.locator(
            "button"
        )

        count = buttons.count()

        for index in range(count):

            candidate = buttons.nth(
                index
            )

            try:

                if not candidate.is_visible():

                    continue

                text = (
                    candidate.inner_text()
                    .strip()
                )

                if text == "Member Search":

                    if candidate.is_enabled():

                        print(
                            "Found Member Search "
                            "using button text."
                        )

                        return candidate

            except Exception:

                continue

    except Exception:

        pass


    # -----------------------------------------------------
    # Strategy 4: frames
    # -----------------------------------------------------

    for frame in get_all_frames(page):

        try:

            locator = frame.get_by_role(
                "button",
                name="Member Search"
            ).last

            if (
                locator.is_visible()
                and locator.is_enabled()
            ):

                print(
                    "Found Member Search "
                    "inside a frame."
                )

                return locator

        except Exception:

            continue


    return None


# =========================================================
# Click Member Search
# =========================================================

def click_member_search(page):

    for attempt in range(
        RETRY_COUNT
    ):

        print(
            f"Member Search attempt "
            f"{attempt + 1}/{RETRY_COUNT}"
        )

        locator = (
            find_member_search_button(
                page
            )
        )

        if locator is not None:

            try:

                locator.scroll_into_view_if_needed()

            except Exception:

                pass


            try:

                locator.click(
                    timeout=TIMEOUT
                )

                print(
                    "Clicked Member Search."
                )

                pause(1.5)

                return True

            except Exception as error:

                print(
                    f"Normal click failed: "
                    f"{error}"
                )

        pause(1)


    # -----------------------------------------------------
    # Final DOM-level fallback
    # -----------------------------------------------------

    try:

        result = page.evaluate(
            """
            () => {
                const buttons =
                    Array.from(
                        document.querySelectorAll("button")
                    );

                const button =
                    buttons.find(
                        b =>
                            b.innerText.trim()
                            === "Member Search"
                    );

                if (!button) {
                    return false;
                }

                button.click();
                return true;
            }
            """
        )

        if result:

            print(
                "Clicked Member Search "
                "using DOM fallback."
            )

            pause(1.5)

            return True

    except Exception as error:

        print(
            f"DOM click failed: {error}"
        )


    return False


# =========================================================
# Find Member ID input
# =========================================================

def find_member_id_input(page):

    print(
        "Searching for Member ID input..."
    )

    # -----------------------------------------------------
    # Search main page and all frames
    # -----------------------------------------------------

    frames = get_all_frames(
        page
    )


    for attempt in range(
        RETRY_COUNT
    ):

        for frame in frames:

            # ---------------------------------------------
            # Strategy 1: exact ID
            # ---------------------------------------------

            try:

                locator = frame.locator(
                    "#memberId"
                )

                if (
                    locator.count() > 0
                    and locator.first.is_visible()
                ):

                    print(
                        "Found Member ID "
                        "using #memberId."
                    )

                    return locator.first

            except Exception:

                pass


            # ---------------------------------------------
            # Strategy 2: name
            # ---------------------------------------------

            try:

                locator = frame.locator(
                    'input[name="member_id"]'
                )

                if (
                    locator.count() > 0
                    and locator.first.is_visible()
                ):

                    print(
                        "Found Member ID "
                        "using name attribute."
                    )

                    return locator.first

            except Exception:

                pass


            # ---------------------------------------------
            # Strategy 3: label
            # ---------------------------------------------

            try:

                locator = frame.get_by_label(
                    "Member ID"
                )

                if (
                    locator.count() > 0
                    and locator.first.is_visible()
                ):

                    print(
                        "Found Member ID "
                        "using label."
                    )

                    return locator.first

            except Exception:

                pass


            # ---------------------------------------------
            # Strategy 4: placeholder
            # ---------------------------------------------

            try:

                locator = frame.locator(
                    'input[placeholder="e.g. 12345"]'
                )

                if (
                    locator.count() > 0
                    and locator.first.is_visible()
                ):

                    print(
                        "Found Member ID "
                        "using placeholder."
                    )

                    return locator.first

            except Exception:

                pass


        pause(1)

        # Refresh frame list in case the application
        # created an iframe dynamically.
        frames = get_all_frames(
            page
        )


    return None


# =========================================================
# Fill Member ID
# =========================================================

def fill_member_id(
    page,
    member_id
):

    for attempt in range(
        RETRY_COUNT
    ):

        print(
            f"Member ID input attempt "
            f"{attempt + 1}/{RETRY_COUNT}"
        )

        locator = find_member_id_input(
            page
        )

        if locator is None:

            pause(1)

            continue


        try:

            locator.scroll_into_view_if_needed()

        except Exception:

            pass


        try:

            locator.fill(
                member_id,
                timeout=TIMEOUT
            )

            pause(0.5)

            current_value = (
                locator.input_value()
            )

            print(
                f"Member ID field now contains: "
                f"{current_value}"
            )

            if current_value == member_id:

                print(
                    "Member ID entered successfully."
                )

                return locator

        except Exception as error:

            print(
                f"Fill failed: {error}"
            )


        pause(1)


    raise RuntimeError(
        "Unable to locate or fill the "
        "Member ID input after multiple attempts."
    )


# =========================================================
# Find Search Member button
# =========================================================

def find_search_member_button(page):

    print(
        "Searching for Search Member button..."
    )

    frames = get_all_frames(
        page
    )


    for attempt in range(
        RETRY_COUNT
    ):

        for frame in frames:

            # ---------------------------------------------
            # Role locator
            # ---------------------------------------------

            try:

                buttons = frame.get_by_role(
                    "button",
                    name="Search Member"
                )

                count = buttons.count()

                for index in range(count):

                    candidate = buttons.nth(
                        index
                    )

                    if (
                        candidate.is_visible()
                        and candidate.is_enabled()
                    ):

                        print(
                            "Found Search Member "
                            "using role locator."
                        )

                        return candidate

            except Exception:

                pass


            # ---------------------------------------------
            # Button text
            # ---------------------------------------------

            try:

                buttons = frame.locator(
                    "button"
                )

                count = buttons.count()

                for index in range(count):

                    candidate = buttons.nth(
                        index
                    )

                    if not candidate.is_visible():

                        continue

                    text = (
                        candidate.inner_text()
                        .strip()
                    )

                    if text == "Search Member":

                        if candidate.is_enabled():

                            print(
                                "Found Search Member "
                                "using button text."
                            )

                            return candidate

            except Exception:

                pass


        pause(0.75)

        frames = get_all_frames(
            page
        )


    return None


# =========================================================
# Click Search Member
# =========================================================

def click_search_member(
    page
):

    for attempt in range(
        RETRY_COUNT
    ):

        print(
            f"Search Member attempt "
            f"{attempt + 1}/{RETRY_COUNT}"
        )

        locator = (
            find_search_member_button(
                page
            )
        )

        if locator is not None:

            try:

                locator.scroll_into_view_if_needed()

            except Exception:

                pass


            try:

                locator.click(
                    timeout=TIMEOUT
                )

                print(
                    "Clicked Search Member."
                )

                pause(1.5)

                return True

            except Exception as error:

                print(
                    f"Normal click failed: "
                    f"{error}"
                )

        pause(1)


    # -----------------------------------------------------
    # DOM fallback
    # -----------------------------------------------------

    try:

        result = page.evaluate(
            """
            () => {
                const buttons =
                    Array.from(
                        document.querySelectorAll("button")
                    );

                const button =
                    buttons.find(
                        b =>
                            b.innerText.trim()
                            === "Search Member"
                    );

                if (!button) {
                    return false;
                }

                button.click();
                return true;
            }
            """
        )

        if result:

            print(
                "Clicked Search Member "
                "using DOM fallback."
            )

            pause(1.5)

            return True

    except Exception as error:

        print(
            f"DOM click failed: {error}"
        )


    return False


# =========================================================
# Detect known runtime outcomes
# =========================================================

def detect_runtime_outcome(
    page,
    member_id
):

    # -----------------------------------------------------
    # Service failure
    # -----------------------------------------------------

    try:

        locator = page.get_by_text(
            "Member service unavailable.",
            exact=True
        )

        if locator.is_visible():

            return {
                "status": "failure",
                "category": "application_failure",
                "outcome": "SERVICE_FAILURE",
                "member_id": member_id,
                "message": (
                    "Member service unavailable."
                )
            }

    except Exception:

        pass


    # -----------------------------------------------------
    # Member not found
    # -----------------------------------------------------

    try:

        locator = page.get_by_text(
            "Member not found.",
            exact=True
        )

        if locator.is_visible():

            return {
                "status": "business_outcome",
                "category": "business_outcome",
                "outcome": "MEMBER_NOT_FOUND",
                "member_id": member_id,
                "message": (
                    "Member does not exist "
                    "in the system."
                )
            }

    except Exception:

        pass


    return None


# =========================================================
# Verify member details
# =========================================================

def verify_member_details(
    page
):

    print(
        "Verifying Member Details..."
    )

    page.get_by_text(
        "Member Details",
        exact=True
    ).wait_for(
        state="visible",
        timeout=TIMEOUT
    )

    print(
        "Member Details verified."
    )


# =========================================================
# Verify member name
# =========================================================

def verify_member_name(
    page
):

    print(
        "Verifying member identity..."
    )

    page.get_by_text(
        "Chukshith N",
        exact=True
    ).wait_for(
        state="visible",
        timeout=TIMEOUT
    )

    print(
        "Member identity verified."
    )


# =========================================================
# Extract savings balance
# =========================================================

def extract_savings_balance(
    page
):

    print(
        "Extracting savings balance..."
    )

    locator = page.locator(
        ".profile-field-value"
    )


    count = locator.count()

    if count == 0:

        raise RuntimeError(
            "No .profile-field-value "
            "elements were found."
        )


    # -----------------------------------------------------
    # Inspect visible profile fields.
    # -----------------------------------------------------

    for index in range(count):

        candidate = locator.nth(
            index
        )

        try:

            if not candidate.is_visible():

                continue

            text = (
                candidate.inner_text()
                .strip()
            )

            if text:

                print(
                    f"Profile field {index}: "
                    f"{text}"
                )

                # The artifact defines this CSS
                # selector as the savings balance
                # extraction target.
                return text

        except Exception:

            continue


    raise RuntimeError(
        "Savings balance could not be "
        "extracted from .profile-field-value."
    )


# =========================================================
# Deterministic replay
# =========================================================

def replay(
    member_id
):

    artifact = load_artifact()


    capability = artifact.get(
        "capability",
        {}
    )


    if capability.get(
        "name"
    ) != "member_lookup":

        raise RuntimeError(
            "Unexpected capability artifact."
        )


    actions = artifact.get(
        "actions",
        []
    )


    if not actions:

        raise RuntimeError(
            "Capability artifact contains "
            "no actions."
        )


    replay_log = {

        "capability":
        capability["name"],

        "artifact_version":
        artifact["artifact_version"],

        "member_id":
        member_id,

        "status":
        "running",

        "steps":
        [],

        "outputs":
        {}
    }


    print()
    print(
        "==================================="
    )
    print(
        "DETERMINISTIC REPLAY"
    )
    print(
        "==================================="
    )
    print(
        f"Capability : "
        f"{capability['name']}"
    )
    print(
        f"Version    : "
        f"{artifact['artifact_version']}"
    )
    print(
        f"Member ID  : {member_id}"
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

            # =================================================
            # STEP 1 — Navigate
            # =================================================

            print()
            print(
                "STEP 1: Navigate"
            )


            page.goto(
                BASE_URL,
                wait_until="domcontentloaded",
                timeout=TIMEOUT
            )


            page.wait_for_timeout(
                2000
            )


            print(
                f"Loaded: {page.url}"
            )


            replay_log[
                "steps"
            ].append(
                {
                    "step_id": "step_1",
                    "action": "navigate",
                    "status": "success"
                }
            )


            # =================================================
            # STEP 2 — Member Search
            # =================================================

            print()
            print(
                "STEP 2: Open Member Search"
            )


            if not click_member_search(
                page
            ):

                print_page_state(
                    page
                )

                screenshot = (
                    save_screenshot(
                        page,
                        "replay_member_search_failed.png"
                    )
                )


                raise RuntimeError(
                    "Could not open Member Search."
                )


            replay_log[
                "steps"
            ].append(
                {
                    "step_id": "step_2",
                    "action": "click",
                    "target": "Member Search",
                    "status": "success"
                }
            )


            # =================================================
            # STEP 3 — Fill Member ID
            # =================================================

            print()
            print(
                "STEP 3: Fill Member ID"
            )


            fill_member_id(
                page,
                member_id
            )


            replay_log[
                "steps"
            ].append(
                {
                    "step_id": "step_3",
                    "action": "fill",
                    "target": "Member ID",
                    "status": "success"
                }
            )


            # =================================================
            # STEP 4 — Search
            # =================================================

            print()
            print(
                "STEP 4: Search Member"
            )


            if not click_search_member(
                page
            ):

                print_page_state(
                    page
                )

                save_screenshot(
                    page,
                    f"search_member_failed_{member_id}.png"
                )


                raise RuntimeError(
                    "Could not click Search Member."
                )


            replay_log[
                "steps"
            ].append(
                {
                    "step_id": "step_4",
                    "action": "click",
                    "target": "Search Member",
                    "status": "success"
                }
            )


            # -------------------------------------------------
            # Screenshot after search
            # -------------------------------------------------

            save_screenshot(
                page,
                f"after_search_{member_id}.png"
            )


            # -------------------------------------------------
            # Check known outcomes
            # -------------------------------------------------

            outcome = detect_runtime_outcome(
                page,
                member_id
            )


            if outcome is not None:

                replay_log.update(
                    outcome
                )


                save_replay_log(
                    replay_log
                )


                print()
                print(
                    "==================================="
                )

                if (
                    outcome["status"]
                    == "business_outcome"
                ):

                    print(
                        "BUSINESS OUTCOME"
                    )

                else:

                    print(
                        "APPLICATION FAILURE"
                    )

                print(
                    "==================================="
                )

                print(
                    f"Outcome: "
                    f"{outcome['outcome']}"
                )

                print(
                    f"Member ID: "
                    f"{member_id}"
                )

                print(
                    f"Message: "
                    f"{outcome['message']}"
                )

                print(
                    "==================================="
                )


                return replay_log


            # =================================================
            # STEP 5 — Verify Member Details
            # =================================================

            print()
            print(
                "STEP 5: Verify Member Details"
            )


            verify_member_details(
                page
            )


            replay_log[
                "steps"
            ].append(
                {
                    "step_id": "step_5",
                    "action": "verify",
                    "target": "Member Details",
                    "status": "success"
                }
            )


            # =================================================
            # STEP 6 — Verify Name
            # =================================================

            print()
            print(
                "STEP 6: Verify Member Identity"
            )


            verify_member_name(
                page
            )


            replay_log[
                "steps"
            ].append(
                {
                    "step_id": "step_6",
                    "action": "verify",
                    "target": "Chukshith N",
                    "status": "success"
                }
            )


            # =================================================
            # STEP 7 — Extract Balance
            # =================================================

            print()
            print(
                "STEP 7: Extract Savings Balance"
            )


            balance = (
                extract_savings_balance(
                    page
                )
            )


            replay_log[
                "outputs"
            ][
                "savings_balance"
            ] = balance


            replay_log[
                "steps"
            ].append(
                {
                    "step_id": "step_7",
                    "action": "extract",
                    "target":
                    ".profile-field-value",
                    "output":
                    "savings_balance",
                    "value":
                    balance,
                    "status":
                    "success"
                }
            )


            # =================================================
            # Final success
            # =================================================

            replay_log[
                "outputs"
            ][
                "member_name"
            ] = "Chukshith N"


            replay_log[
                "status"
            ] = "success"


            print()
            print(
                "Checking success condition..."
            )


            verify_member_details(
                page
            )


            verify_member_name(
                page
            )


            print(
                "Checkpoint verified."
            )


            print()
            print(
                "==================================="
            )
            print(
                "REPLAY SUCCESSFUL"
            )
            print(
                "==================================="
            )
            print(
                f"Member ID: {member_id}"
            )
            print(
                "Member: "
                f"{replay_log['outputs']['member_name']}"
            )
            print(
                "Savings Balance: "
                f"{replay_log['outputs']['savings_balance']}"
            )
            print(
                "==================================="
            )


            save_replay_log(
                replay_log
            )


            return replay_log


        except Exception as error:

            replay_log[
                "status"
            ] = "failure"

            replay_log[
                "category"
            ] = "hard_failure"

            replay_log[
                "error"
            ] = str(error)


            # -------------------------------------------------
            # Diagnostic screenshot
            # -------------------------------------------------

            try:

                screenshot = (
                    save_screenshot(
                        page,
                        f"replay_error_{member_id}.png"
                    )
                )

                replay_log[
                    "diagnostic_screenshot"
                ] = screenshot

            except Exception:

                pass


            save_replay_log(
                replay_log
            )


            print()
            print(
                "==================================="
            )
            print(
                "REPLAY FAILED"
            )
            print(
                "==================================="
            )
            print(
                f"Member ID: {member_id}"
            )
            print(
                "Category: HARD_FAILURE"
            )
            print(
                f"Error: {error}"
            )
            print(
                "==================================="
            )


            return replay_log


        finally:

            browser.close()


# =========================================================
# Entry point
# =========================================================

if __name__ == "__main__":

    member_id = "12345"

    if len(sys.argv) > 1:

        member_id = sys.argv[1]

    replay(
        member_id
    )