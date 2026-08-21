from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Vista Club Bank")


# =========================================================
# MOCK MEMBER DATA
# =========================================================

MEMBERS = {
    "12345": {
        "member_id": "12345",
        "name": "Chukshith N",
        "status": "Active",
        "member_since": "March 2019",
        "phone": "(555) 014-7821",
        "email": "chukshith.n@example.test",
        "accounts": [
            {
                "account_number": "****1234",
                "type": "Savings",
                "status": "Active",
                "balance": 30000.50,
            },
            {
                "account_number": "****5678",
                "type": "Checking",
                "status": "Active",
                "balance": 15000.00,
            },
        ],
    },

    "67890": {
        "member_id": "67890",
        "name": "Sri K",
        "status": "Active",
        "member_since": "August 2021",
        "phone": "(555) 019-4421",
        "email": "sri.k@example.test",
        "accounts": [
            {
                "account_number": "****4321",
                "type": "Savings",
                "status": "Active",
                "balance": 9000.40,
            },
            {
                "account_number": "****8765",
                "type": "Checking",
                "status": "Active",
                "balance": 3950.00,
            },
        ],
    },

    "24680": {
        "member_id": "24680",
        "name": "Amith G",
        "status": "Active",
        "member_since": "January 2018",
        "phone": "(555) 011-2388",
        "email": "amith.g@example.test",
        "accounts": [
            {
                "account_number": "****2468",
                "type": "Savings",
                "status": "Active",
                "balance": 6560.45,
            },
            {
                "account_number": "****1357",
                "type": "Checking",
                "status": "Active",
                "balance": 2497.97,
            },
        ],
    },

    "13579": {
        "member_id": "13579",
        "name": "Manish K",
        "status": "Active",
        "member_since": "June 2022",
        "phone": "(555) 016-9342",
        "email": "manish.k@example.test",
        "accounts": [
            {
                "account_number": "****5791",
                "type": "Savings",
                "status": "Active",
                "balance": 6785.40,
            },
            {
                "account_number": "****2461",
                "type": "Checking",
                "status": "Active",
                "balance": 2150.00,
            },
        ],
    },
}


# =========================================================
# MAIN APPLICATION
# =========================================================

@app.get("/", response_class=HTMLResponse)
def home():

    return """
<!DOCTYPE html>

<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>Vista Club Bank</title>


    <style>

        /* =================================================
           GLOBAL
        ================================================= */

        * {
            box-sizing: border-box;
        }


        body {

            margin: 0;

            font-family:
                Arial,
                Helvetica,
                sans-serif;

            background: #f3f5f8;

            color: #1f2937;
        }


        /* =================================================
           TOP BAR
        ================================================= */

        .topbar {

            height: 64px;

            background: #172033;

            color: white;

            display: flex;

            align-items: center;

            justify-content: space-between;

            padding: 0 28px;

            box-shadow:
                0 2px 6px rgba(0, 0, 0, 0.15);
        }


        .brand {

            display: flex;

            align-items: center;

            gap: 12px;
        }


        .brand-icon {

            width: 36px;

            height: 36px;

            border-radius: 8px;

            background: #2563eb;

            display: flex;

            align-items: center;

            justify-content: center;

            font-weight: bold;
        }


        .brand-name {

            font-size: 17px;

            font-weight: 600;
        }


        .environment {

            font-size: 12px;

            color: #9ca3af;

            margin-top: 2px;
        }


        .operator {

            display: flex;

            align-items: center;

            gap: 10px;

            font-size: 14px;
        }


        .operator-avatar {

            width: 34px;

            height: 34px;

            border-radius: 50%;

            background: #374151;

            display: flex;

            align-items: center;

            justify-content: center;
        }


        /* =================================================
           APPLICATION LAYOUT
        ================================================= */

        .layout {

            display: flex;

            min-height:
                calc(100vh - 64px);
        }


        /* =================================================
           SIDEBAR
        ================================================= */

        .sidebar {

            width: 230px;

            background: #111827;

            padding: 24px 14px;

            color: white;
        }


        .sidebar-section {

            margin-bottom: 26px;
        }


        .sidebar-label {

            color: #6b7280;

            font-size: 11px;

            font-weight: 700;

            letter-spacing: 0.08em;

            padding: 0 12px;

            margin-bottom: 10px;
        }


        .nav-button {

            width: 100%;

            background: transparent;

            border: none;

            color: #d1d5db;

            text-align: left;

            padding: 12px;

            border-radius: 6px;

            cursor: pointer;

            font-size: 14px;

            margin-bottom: 4px;
        }


        .nav-button:hover {

            background: #1f2937;

            color: white;
        }


        .nav-button.active {

            background: #2563eb;

            color: white;
        }


        /* =================================================
           MAIN CONTENT
        ================================================= */

        .main {

            flex: 1;

            padding: 32px;

            max-width: 1400px;
        }


        .page-header {

            margin-bottom: 28px;
        }


        .page-header h1 {

            margin: 0 0 6px 0;

            font-size: 26px;
        }


        .page-header p {

            margin: 0;

            color: #6b7280;

            font-size: 14px;
        }


        /* =================================================
           DASHBOARD STATISTICS
        ================================================= */

        .stats {

            display: grid;

            grid-template-columns:
                repeat(3, minmax(180px, 1fr));

            gap: 18px;

            margin-bottom: 28px;
        }


        .stat-card {

            background: white;

            border: 1px solid #e5e7eb;

            border-radius: 8px;

            padding: 20px;
        }


        .stat-label {

            color: #6b7280;

            font-size: 13px;
        }


        .stat-value {

            font-size: 25px;

            font-weight: 700;

            margin-top: 8px;
        }


        /* =================================================
           PANELS
        ================================================= */

        .panel {

            background: white;

            border: 1px solid #e5e7eb;

            border-radius: 8px;

            margin-bottom: 24px;

            overflow: hidden;
        }


        .panel-header {

            padding: 18px 22px;

            border-bottom:
                1px solid #e5e7eb;

            display: flex;

            justify-content: space-between;

            align-items: center;
        }


        .panel-header h2 {

            margin: 0;

            font-size: 16px;
        }


        .panel-body {

            padding: 22px;
        }


        /* =================================================
           SEARCH FORM
        ================================================= */

        .search-row {

            display: flex;

            gap: 12px;

            align-items: end;
        }


        .form-group {

            display: flex;

            flex-direction: column;

            gap: 7px;
        }


        .form-group label {

            font-size: 13px;

            font-weight: 600;
        }


        .form-group input {

            width: 300px;

            padding: 11px 12px;

            border:
                1px solid #d1d5db;

            border-radius: 6px;

            font-size: 14px;

            outline: none;
        }


        .form-group input:focus {

            border-color: #2563eb;

            box-shadow:
                0 0 0 2px
                rgba(37, 99, 235, 0.1);
        }


        .primary-button {

            padding: 11px 18px;

            border: none;

            border-radius: 6px;

            background: #2563eb;

            color: white;

            font-size: 14px;

            font-weight: 600;

            cursor: pointer;
        }


        .primary-button:hover {

            background: #1d4ed8;
        }


        .primary-button:disabled {

            background: #93c5fd;

            cursor: not-allowed;
        }


        /* =================================================
           MEMBER PROFILE
        ================================================= */

        .member-header {

            display: flex;

            justify-content: space-between;

            align-items: center;

            margin-bottom: 24px;
        }


        .member-name {

            font-size: 22px;

            font-weight: 700;
        }


        .member-id {

            color: #6b7280;

            font-size: 13px;

            margin-top: 5px;
        }


        .status-badge {

            padding: 6px 11px;

            border-radius: 999px;

            background: #dcfce7;

            color: #166534;

            font-size: 12px;

            font-weight: 600;
        }


        .profile-grid {

            display: grid;

            grid-template-columns:
                repeat(3, 1fr);

            gap: 20px;

            margin-bottom: 28px;
        }


        .profile-field {

            background: #f9fafb;

            border:
                1px solid #e5e7eb;

            padding: 15px;

            border-radius: 6px;
        }


        .profile-field-label {

            color: #6b7280;

            font-size: 12px;

            margin-bottom: 6px;
        }


        .profile-field-value {

            font-size: 14px;

            font-weight: 600;
        }


        /* =================================================
           ACCOUNTS TABLE
        ================================================= */

        table {

            width: 100%;

            border-collapse: collapse;
        }


        th {

            background: #f9fafb;

            color: #6b7280;

            font-size: 12px;

            text-align: left;

            padding: 13px;

            border-bottom:
                1px solid #e5e7eb;
        }


        td {

            padding: 15px 13px;

            border-bottom:
                1px solid #e5e7eb;

            font-size: 14px;
        }


        .balance {

            font-weight: 700;
        }


        .account-status {

            color: #166534;

            font-size: 12px;

            font-weight: 600;
        }


        /* =================================================
           ALERTS
        ================================================= */

        .alert {

            padding: 13px 15px;

            border-radius: 6px;

            margin-top: 18px;

            font-size: 13px;
        }


        .alert-error {

            background: #fef2f2;

            border:
                1px solid #fecaca;

            color: #991b1b;
        }


        .alert-info {

            background: #eff6ff;

            border:
                1px solid #bfdbfe;

            color: #1e40af;
        }


        .alert-success {

            background: #ecfdf5;

            border:
                1px solid #a7f3d0;

            color: #065f46;
        }


        /* =================================================
           UTILITY
        ================================================= */

        .hidden {

            display: none;
        }


        .back-button {

            background: white;

            border:
                1px solid #d1d5db;

            padding: 9px 14px;

            border-radius: 6px;

            cursor: pointer;

            font-size: 13px;
        }


        .back-button:hover {

            background: #f9fafb;
        }


        .loading {

            display: inline-flex;

            align-items: center;

            gap: 8px;
        }


        .spinner {

            width: 14px;

            height: 14px;

            border:
                2px solid #bfdbfe;

            border-top-color: #2563eb;

            border-radius: 50%;

            animation:
                spin 0.8s linear infinite;
        }


        @keyframes spin {

            to {
                transform: rotate(360deg);
            }
        }


        /* =================================================
           RESPONSIVE
        ================================================= */

        @media (max-width: 900px) {

            .sidebar {

                width: 190px;
            }


            .stats {

                grid-template-columns: 1fr;
            }


            .profile-grid {

                grid-template-columns: 1fr;
            }


            .search-row {

                flex-direction: column;

                align-items: flex-start;
            }

        }

    </style>

</head>


<body>


<!-- =====================================================
     TOP BAR
===================================================== -->

<header class="topbar">

    <div class="brand">

        <div class="brand-icon">
            BO
        </div>

        <div>

            <div class="brand-name">
                Bank Operations
            </div>

            <div class="environment">
                Internal Operations Portal
            </div>

        </div>

    </div>


    <div class="operator">

        <div>
            Operations User
        </div>

        <div class="operator-avatar">
            OU
        </div>

    </div>

</header>



<!-- =====================================================
     APPLICATION LAYOUT
===================================================== -->

<div class="layout">


    <!-- =================================================
         SIDEBAR
    ================================================== -->

    <aside class="sidebar">


        <div class="sidebar-section">

            <div class="sidebar-label">
                WORKSPACE
            </div>


            <button
                class="nav-button active"
                id="dashboardButton"
                onclick="showDashboard()"
            >
                Dashboard
            </button>


            <button
                class="nav-button"
                id="memberSearchButton"
                onclick="showMemberSearch()"
            >
                Member Search
            </button>

        </div>



        <div class="sidebar-section">

            <div class="sidebar-label">
                OPERATIONS
            </div>


            <button
                class="nav-button"
                onclick="showComingSoon()"
            >
                Account Services
            </button>


            <button
                class="nav-button"
                onclick="showComingSoon()"
            >
                Transaction Review
            </button>

        </div>

    </aside>



    <!-- =================================================
         MAIN CONTENT
    ================================================== -->

    <main class="main">


        <!-- =================================================
             DASHBOARD
        ================================================== -->

        <section id="dashboardPage">


            <div class="page-header">

                <h1>
                    Operations Dashboard
                </h1>

                <p>
                    Internal member servicing and account
                    operations.
                </p>

            </div>



            <div class="stats">


                <div class="stat-card">

                    <div class="stat-label">
                        Active Members
                    </div>

                    <div class="stat-value">
                        4
                    </div>

                </div>



                <div class="stat-card">

                    <div class="stat-label">
                        Accounts Serviced
                    </div>

                    <div class="stat-value">
                        8
                    </div>

                </div>



                <div class="stat-card">

                    <div class="stat-label">
                        System Status
                    </div>

                    <div class="stat-value">
                        Operational
                    </div>

                </div>

            </div>



            <div class="panel">

                <div class="panel-header">

                    <h2>
                        Member Operations
                    </h2>

                </div>


                <div class="panel-body">

                    <p>
                        Search for a member to view profile
                        and account information.
                    </p>


                    <button
                        class="primary-button"
                        id="dashboardSearchButton"
                        onclick="showMemberSearch()"
                    >
                        Search Member
                    </button>

                </div>

            </div>

        </section>



        <!-- =================================================
             MEMBER SEARCH
        ================================================== -->

        <section
            id="memberSearchPage"
            class="hidden"
        >


            <div class="page-header">

                <h1>
                    Member Search
                </h1>

                <p>
                    Locate a member using their unique
                    member identifier.
                </p>

            </div>



            <div class="panel">


                <div class="panel-header">

                    <h2>
                        Search Member Records
                    </h2>

                </div>



                <div class="panel-body">


                    <div class="search-row">


                        <div class="form-group">

                            <label for="memberId">
                                Member ID
                            </label>


                            <input
                                id="memberId"
                                name="member_id"
                                type="text"
                                placeholder="e.g. 12345"
                                autocomplete="off"
                            >

                        </div>



                        <button
                            class="primary-button"
                            id="searchMemberButton"
                            onclick="searchMember()"
                        >
                            Search Member
                        </button>

                    </div>


                    <div
                        id="searchResult"
                    ></div>

                </div>

            </div>

        </section>



        <!-- =================================================
             MEMBER DETAILS
        ================================================== -->

        <section
            id="memberDetailsPage"
            class="hidden"
        >


            <div class="page-header">

                <button
                    class="back-button"
                    onclick="showMemberSearch()"
                >
                    ← Back to Search
                </button>

            </div>


            <div id="memberDetails"></div>

        </section>



        <!-- =================================================
             COMING SOON
        ================================================== -->

        <section
            id="comingSoonPage"
            class="hidden"
        >


            <div class="page-header">

                <h1>
                    Operations
                </h1>

                <p>
                    This module is reserved for a future
                    workflow.
                </p>

            </div>



            <div class="panel">

                <div class="panel-body">

                    <div class="alert alert-info">

                        This operation is not enabled in the
                        current demonstration environment.

                    </div>

                </div>

            </div>

        </section>


    </main>

</div>



<script>


// =========================================================
// PAGE NAVIGATION
// =========================================================

function hideAllPages() {

    document
        .getElementById("dashboardPage")
        .classList.add("hidden");


    document
        .getElementById("memberSearchPage")
        .classList.add("hidden");


    document
        .getElementById("memberDetailsPage")
        .classList.add("hidden");


    document
        .getElementById("comingSoonPage")
        .classList.add("hidden");
}


function clearActiveNavigation() {

    document
        .querySelectorAll(".nav-button")
        .forEach(button => {

            button.classList.remove("active");

        });
}


function showDashboard() {

    hideAllPages();

    clearActiveNavigation();


    document
        .getElementById("dashboardPage")
        .classList.remove("hidden");


    document
        .getElementById("dashboardButton")
        .classList.add("active");
}


function showMemberSearch() {

    hideAllPages();

    clearActiveNavigation();


    document
        .getElementById("memberSearchPage")
        .classList.remove("hidden");


    document
        .getElementById("memberSearchButton")
        .classList.add("active");


    document
        .getElementById("memberId")
        .focus();
}


function showComingSoon() {

    hideAllPages();

    clearActiveNavigation();


    document
        .getElementById("comingSoonPage")
        .classList.remove("hidden");
}



// =========================================================
// MEMBER SEARCH
// =========================================================

async function searchMember() {

    const memberId =
        document
            .getElementById("memberId")
            .value
            .trim();


    const result =
        document
            .getElementById("searchResult");


    const searchButton =
        document
            .getElementById("searchMemberButton");


    // Empty input

    if (!memberId) {

        result.innerHTML = `
            <div class="alert alert-error">

                Please enter a member ID.

            </div>
        `;

        return;
    }


    // Disable button while searching

    searchButton.disabled = true;


    result.innerHTML = `
        <div class="alert alert-info">

            <span class="loading">

                <span class="spinner"></span>

                Searching member records...

            </span>

        </div>
    `;


    try {

        const response =
            await fetch(
                "/api/members/" +
                encodeURIComponent(memberId)
            );


        const data =
            await response.json();


        // ---------------------------------------------
        // Member not found
        // ---------------------------------------------

        if (data.status === "not_found") {

            result.innerHTML = `
                <div class="alert alert-error">

                    <strong>Member not found.</strong>

                    <br><br>

                    Member ID
                    <strong>${memberId}</strong>
                    does not exist in the system.

                    <br><br>

                    Please verify the member ID and
                    try again.

                </div>
            `;

            return;
        }


        // ---------------------------------------------
        // Simulated application error
        // ---------------------------------------------

        if (data.status === "error") {

            result.innerHTML = `
                <div class="alert alert-error">

                    <strong>
                        Member service unavailable.
                    </strong>

                    <br><br>

                    The member service encountered a
                    temporary application error.

                    <br><br>

                    Please try again.

                </div>
            `;

            return;
        }


        // ---------------------------------------------
        // Successful search
        // ---------------------------------------------

        if (data.status === "success") {

            renderMemberDetails(data.member);


            hideAllPages();


            document
                .getElementById("memberDetailsPage")
                .classList.remove("hidden");


            return;
        }


        // ---------------------------------------------
        // Unknown response
        // ---------------------------------------------

        result.innerHTML = `
            <div class="alert alert-error">

                Unexpected response from member service.

            </div>
        `;


    } catch (error) {

        result.innerHTML = `
            <div class="alert alert-error">

                <strong>
                    Application error.
                </strong>

                <br><br>

                The system could not complete the
                member search.

            </div>
        `;

    } finally {

        searchButton.disabled = false;

    }
}



// =========================================================
// MEMBER DETAILS
// =========================================================

function renderMemberDetails(member) {


    const savings =
        member.accounts.find(
            account =>
                account.type === "Savings"
        );


    const accountsRows =
        member.accounts
            .map(account => `

                <tr>

                    <td>
                        ${account.account_number}
                    </td>

                    <td>
                        ${account.type}
                    </td>

                    <td>

                        <span class="account-status">

                            ${account.status}

                        </span>

                    </td>

                    <td class="balance">

                        $${account.balance.toLocaleString(
                            "en-US",
                            {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2
                            }
                        )}

                    </td>

                </tr>

            `)
            .join("");


    document
        .getElementById("memberDetails")
        .innerHTML = `


            <div class="page-header">

                <h1>
                    Member Details
                </h1>

                <p>
                    Account and profile information
                    for the selected member.
                </p>

            </div>



            <div class="panel">


                <div class="panel-body">


                    <div class="member-header">


                        <div>

                            <div class="member-name">

                                ${member.name}

                            </div>


                            <div class="member-id">

                                Member ID:
                                ${member.member_id}

                            </div>

                        </div>



                        <div class="status-badge">

                            ${member.status}

                        </div>

                    </div>



                    <!-- PROFILE -->

                    <div class="profile-grid">


                        <div class="profile-field">

                            <div class="profile-field-label">

                                Member ID

                            </div>

                            <div class="profile-field-value">

                                ${member.member_id}

                            </div>

                        </div>



                        <div class="profile-field">

                            <div class="profile-field-label">

                                Member Since

                            </div>

                            <div class="profile-field-value">

                                ${member.member_since}

                            </div>

                        </div>



                        <div class="profile-field">

                            <div class="profile-field-label">

                                Phone

                            </div>

                            <div class="profile-field-value">

                                ${member.phone}

                            </div>

                        </div>



                        <div class="profile-field">

                            <div class="profile-field-label">

                                Email

                            </div>

                            <div class="profile-field-value">

                                ${member.email}

                            </div>

                        </div>



                        <div class="profile-field">

                            <div class="profile-field-label">

                                Savings Balance

                            </div>

                            <div class="profile-field-value">

                                $${savings.balance.toLocaleString(
                                    "en-US",
                                    {
                                        minimumFractionDigits: 2,
                                        maximumFractionDigits: 2
                                    }
                                )}

                            </div>

                        </div>


                    </div>



                    <!-- ACCOUNTS -->

                    <h3>
                        Accounts
                    </h3>



                    <table>

                        <thead>

                            <tr>

                                <th>
                                    Account Number
                                </th>

                                <th>
                                    Account Type
                                </th>

                                <th>
                                    Status
                                </th>

                                <th>
                                    Current Balance
                                </th>

                            </tr>

                        </thead>


                        <tbody>

                            ${accountsRows}

                        </tbody>

                    </table>


                </div>

            </div>

        `;
}


</script>


</body>

</html>
"""


# =========================================================
# MEMBER LOOKUP API
# =========================================================

@app.get("/api/members/{member_id}")
def get_member(member_id: str):

    # -----------------------------------------------------
    # Simulated application failure
    #
    # We will use this later when demonstrating
    # deterministic replay error handling.
    # -----------------------------------------------------

    if member_id == "50000":

        return {
            "status": "error",
            "error_type": "MEMBER_SERVICE_UNAVAILABLE",
            "message": "Member service temporarily unavailable",
        }


    # -----------------------------------------------------
    # Look up member
    # -----------------------------------------------------

    member = MEMBERS.get(member_id)


    # -----------------------------------------------------
    # Business outcome: member does not exist
    # -----------------------------------------------------

    if member is None:

        return {
            "status": "not_found",
            "outcome": "MEMBER_NOT_FOUND",
            "member_id": member_id,
        }


    # -----------------------------------------------------
    # Successful lookup
    # -----------------------------------------------------

    return {
        "status": "success",
        "member": member,
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "ok",
        "service": "Vista-club-bank",
        "active_members": len(MEMBERS),
    }