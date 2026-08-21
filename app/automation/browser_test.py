from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:8000"
MEMBER_ID = "12345"


def main():

    with sync_playwright() as p:

        # -------------------------------------------------
        # 1. Start Chromium
        # -------------------------------------------------

        browser = p.chromium.launch(
            headless=False,
            slow_mo=1500
        )

        page = browser.new_page()

        # -------------------------------------------------
        # 2. Open Bank Operations Portal
        # -------------------------------------------------

        page.goto(BASE_URL)

        print("Opened Bank Operations Portal")

        # -------------------------------------------------
        # 3. Open Member Search
        # -------------------------------------------------

        page.get_by_role(
            "button",
            name="Member Search"
        ).click()

        print("Opened Member Search")

        # -------------------------------------------------
        # 4. Enter Member ID
        # -------------------------------------------------

        page.get_by_label("Member ID").fill(MEMBER_ID)

        print(f"Entered member ID: {MEMBER_ID}")

        # -------------------------------------------------
        # 5. Search for member
        # -------------------------------------------------

        page.get_by_role(
            "button",
            name="Search Member"
        ).last.click()

        print("Clicked Search Member")

        # -------------------------------------------------
        # 6. Check for application/service failure
        # -------------------------------------------------

        service_failure = page.get_by_text(
            "Member service unavailable.",
            exact=True
        )

        if service_failure.is_visible():

            print()
            print("===================================")
            print("APPLICATION FAILURE")
            print("Outcome: SERVICE_FAILURE")
            print(f"Member ID: {MEMBER_ID}")
            print("Message: Member service unavailable.")
            print("===================================")

            browser.close()
            return

        # -------------------------------------------------
        # 7. Check for expected business outcome
        # -------------------------------------------------

        not_found_message = page.get_by_text(
            "Member not found.",
            exact=True
        )

        if not_found_message.is_visible():

            print()
            print("===================================")
            print("BUSINESS OUTCOME")
            print("Outcome: MEMBER_NOT_FOUND")
            print(f"Member ID: {MEMBER_ID}")
            print("Message: Member does not exist in the system.")
            print("===================================")

            browser.close()
            return

        # -------------------------------------------------
        # 8. Successful member lookup
        # -------------------------------------------------

        page.get_by_text(
            "Member Details",
            exact=True
        ).wait_for()

        print("Member Details page loaded")

        # -------------------------------------------------
        # 9. Verify member
        # -------------------------------------------------

        page.get_by_text(
            "Chukshith N",
            exact=True
        ).wait_for()

        print("Verified member: Chukshith N")

        # -------------------------------------------------
        # 10. Find savings balance
        # -------------------------------------------------

        balance_element = page.locator(
            ".profile-field-value"
        ).filter(
            has_text="$"
        ).first

        balance_element.wait_for()

        balance = balance_element.inner_text()

        print("Savings Balance:", balance)

        # -------------------------------------------------
        # 11. Successful workflow
        # -------------------------------------------------

        print()
        print("===================================")
        print("WORKFLOW SUCCESSFUL")
        print(f"Member ID: {MEMBER_ID}")
        print("Member: Chukshith N")
        print("Savings Balance:", balance)
        print("===================================")

        browser.close()


if __name__ == "__main__":
    main()