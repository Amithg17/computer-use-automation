# =========================================================
# Browser Action Policy
# =========================================================

ALLOWED_ACTIONS = {
    "click",
    "fill",
    "verify",
    "extract",
    "finish",
}


ALLOWED_CLICK_ROLES = {
    "button",
}


ALLOWED_FILL_TARGET_TYPES = {
    "label",
}


ALLOWED_VERIFY_TARGET_TYPES = {
    "text",
}


ALLOWED_EXTRACT_TARGET_TYPES = {
    "css",
}


def validate_action(decision):
    """
    Validate an LLM-generated browser action before
    allowing Playwright to execute it.

    Returns:
        {
            "allowed": True/False,
            "reason": "..."
        }
    """

    if not isinstance(decision, dict):

        return {
            "allowed": False,
            "reason": "LLM decision must be a JSON object."
        }

    action = decision.get("action")

    if action not in ALLOWED_ACTIONS:

        return {
            "allowed": False,
            "reason": (
                f"Action '{action}' is not allowlisted."
            )
        }

    # =====================================================
    # CLICK
    # =====================================================

    if action == "click":

        target = decision.get("target")

        if not isinstance(target, dict):

            return {
                "allowed": False,
                "reason": (
                    "Click action requires a target."
                )
            }

        if target.get("type") != "role":

            return {
                "allowed": False,
                "reason": (
                    "Click target must use role targeting."
                )
            }

        if target.get("role") not in ALLOWED_CLICK_ROLES:

            return {
                "allowed": False,
                "reason": (
                    "Only button role clicks are allowed."
                )
            }

        if not target.get("name"):

            return {
                "allowed": False,
                "reason": (
                    "Button name is required."
                )
            }

        return {
            "allowed": True,
            "reason": "Click action is allowed."
        }

    # =====================================================
    # FILL
    # =====================================================

    if action == "fill":

        target = decision.get("target")

        if not isinstance(target, dict):

            return {
                "allowed": False,
                "reason": (
                    "Fill action requires a target."
                )
            }

        if target.get("type") not in (
            ALLOWED_FILL_TARGET_TYPES
        ):

            return {
                "allowed": False,
                "reason": (
                    "Fill target must use label targeting."
                )
            }

        if not target.get("value"):

            return {
                "allowed": False,
                "reason": (
                    "Fill target label is required."
                )
            }

        if "value" not in decision:

            return {
                "allowed": False,
                "reason": (
                    "Fill action requires a value."
                )
            }

        return {
            "allowed": True,
            "reason": "Fill action is allowed."
        }

    # =====================================================
    # VERIFY
    # =====================================================

    if action == "verify":

        target = decision.get("target")

        if not isinstance(target, dict):

            return {
                "allowed": False,
                "reason": (
                    "Verify action requires a target."
                )
            }

        if target.get("type") not in (
            ALLOWED_VERIFY_TARGET_TYPES
        ):

            return {
                "allowed": False,
                "reason": (
                    "Verify target must use text targeting."
                )
            }

        if not target.get("value"):

            return {
                "allowed": False,
                "reason": (
                    "Verify text is required."
                )
            }

        return {
            "allowed": True,
            "reason": "Verify action is allowed."
        }

    # =====================================================
    # EXTRACT
    # =====================================================

    if action == "extract":

        target = decision.get("target")

        if not isinstance(target, dict):

            return {
                "allowed": False,
                "reason": (
                    "Extract action requires a target."
                )
            }

        if target.get("type") not in (
            ALLOWED_EXTRACT_TARGET_TYPES
        ):

            return {
                "allowed": False,
                "reason": (
                    "Extract target must use CSS targeting."
                )
            }

        if not target.get("value"):

            return {
                "allowed": False,
                "reason": (
                    "Extract selector is required."
                )
            }

        if not decision.get("output"):

            return {
                "allowed": False,
                "reason": (
                    "Extract output name is required."
                )
            }

        return {
            "allowed": True,
            "reason": "Extract action is allowed."
        }

    # =====================================================
    # FINISH
    # =====================================================

    if action == "finish":

        return {
            "allowed": True,
            "reason": "Finish action is allowed."
        }

    return {
        "allowed": False,
        "reason": "Unknown policy state."
    }