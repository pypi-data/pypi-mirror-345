# Sales force CRM Tools
# TODO: This needs to be tested and validated like the HubSpot CRM tools.

import json
import os
from dhisana.utils.assistant_tool_tag import assistant_tool
from simple_salesforce import Salesforce
from urllib.parse import urljoin

@assistant_tool
async def run_salesforce_crm_query(query: str):
    """
    Executes a Salesforce SOQL query and returns the results as JSON.
    Use this to query Salesforce CRM data like Contacts, Leads, Company etc.

    Parameters:
    query (str): The SOQL query string to execute.

    Returns:
    str: JSON string containing the query results or error message.

    Raises:
    ValueError: If Salesforce credentials are not found.
    ValueError: If the query is empty.
    Exception: If the query fails or returns no results.
    """
    if not query.strip():
        return json.dumps({"error": "The query string cannot be empty"})

    # Salesforce credentials from environment variables
    SF_USERNAME = os.environ.get('SALESFORCE_USERNAME')
    SF_PASSWORD = os.environ.get('SALESFORCE_PASSWORD')
    SF_SECURITY_TOKEN = os.environ.get('SALESFORCE_SECURITY_TOKEN')
    SF_DOMAIN = os.environ.get('SALESFORCE_DOMAIN', 'login')  # Use 'test' for sandbox

    if not all([SF_USERNAME, SF_PASSWORD, SF_SECURITY_TOKEN]):
        return json.dumps({"error": "Salesforce credentials not found in environment variables"})

    # Initialize Salesforce connection
    try:
        sf = Salesforce(
            username=SF_USERNAME,
            password=SF_PASSWORD,
            security_token=SF_SECURITY_TOKEN,
            domain=SF_DOMAIN
        )

        # Execute the query
        result = sf.query_all(query)
        if not result['records']:
            return json.dumps({"error": "No records found for the provided query"})
    except Exception as e:
        return json.dumps({"error": f"Query failed: {e}"})

    # Return the results as a JSON string
    return json.dumps(result)

@assistant_tool
async def fetch_salesforce_contact_info(contact_id=None, email=None):
    """
    Fetch contact information from Salesforce using the contact's Salesforce ID or email.

    Parameters:
    contact_id (str): Unique Salesforce contact ID.
    email (str): Contact's email address.

    Returns:
    dict: JSON response containing contact information.

    Raises:
    ValueError: If Salesforce credentials are not provided or if neither contact_id nor email is provided.
    ValueError: If no contact is found.
    """
    # Salesforce credentials from environment variables
    SF_USERNAME = os.environ.get('SALESFORCE_USERNAME')
    SF_PASSWORD = os.environ.get('SALESFORCE_PASSWORD')
    SF_SECURITY_TOKEN = os.environ.get('SALESFORCE_SECURITY_TOKEN')
    SF_DOMAIN = os.environ.get('SALESFORCE_DOMAIN', 'login')  # Use 'test' for sandbox

    if not all([SF_USERNAME, SF_PASSWORD, SF_SECURITY_TOKEN]):
        return json.dumps({"error": "Salesforce credentials not found in environment variables"})

    if not contact_id and not email:
        return json.dumps({"error": "Either Salesforce contact ID or email must be provided"})

    try:
        # Connect to Salesforce
        sf = Salesforce(
            username=SF_USERNAME,
            password=SF_PASSWORD,
            security_token=SF_SECURITY_TOKEN,
            domain=SF_DOMAIN
        )

        if contact_id:
            # Fetch contact by ID
            contact = sf.Contact.get(contact_id)
        else:
            # Sanitize email input
            sanitized_email = email.replace("'", "\\'")
            query = f"""
            SELECT Id, Name, Email, Phone, MobilePhone, Title, Department, MailingAddress, LastActivityDate, LeadSource,
                   Account.Id, Account.Name, Account.Industry, Account.Website, Account.Phone, Account.BillingAddress
            FROM Contact 
            WHERE Email = '{sanitized_email}'
            """
            result = sf.query(query)
            if result['totalSize'] == 0:
                return json.dumps({"error": "No contact found with the provided email"})
            contact = result['records'][0]

        return json.dumps(contact)
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch contact information: {e}"})
    

@assistant_tool
async def read_salesforce_list_entries(object_type: str, listview_name: str, entries_count: int):
    """
    Reads entries from a Salesforce list view and returns the results as JSON.
    Retrieves up to the specified number of entries.

    Parameters:
    object_type (str): The Salesforce object type (e.g., 'Contact').
    listview_name (str): The name of the list view to read from.
    entries_count (int): The number of entries to read.

    Returns:
    str: JSON string containing the list entries or error message.
    """
    if not listview_name.strip() or not object_type.strip():
        return json.dumps({"error": "The object type and list view name cannot be empty"})

    if entries_count <= 0:
        return json.dumps({"error": "Entries count must be a positive integer"})

    # Salesforce credentials from environment variables
    SF_USERNAME = os.environ.get('SALESFORCE_USERNAME')
    SF_PASSWORD = os.environ.get('SALESFORCE_PASSWORD')
    SF_SECURITY_TOKEN = os.environ.get('SALESFORCE_SECURITY_TOKEN')
    SF_DOMAIN = os.environ.get('SALESFORCE_DOMAIN', 'login')  # Use 'test' for sandbox

    if not all([SF_USERNAME, SF_PASSWORD, SF_SECURITY_TOKEN]):
        return json.dumps({"error": "Salesforce credentials not found in environment variables"})

    # Initialize Salesforce connection
    try:
        sf = Salesforce(
            username=SF_USERNAME,
            password=SF_PASSWORD,
            security_token=SF_SECURITY_TOKEN,
            domain=SF_DOMAIN
        )

        # Step 1: Get List View ID
        list_views_url = urljoin(sf.base_url, f"sobjects/{object_type}/listviews")
        list_views_response = sf._call_salesforce('GET', list_views_url)

        if list_views_response.status_code != 200:
            return json.dumps({"error": f"Failed to retrieve list views: {list_views_response.text}"})

        list_views_data = list_views_response.json()
        list_view = next(
            (lv for lv in list_views_data['listviews'] if lv['label'] == listview_name),
            None
        )

        if not list_view:
            return json.dumps({"error": "List view not found"})

        # Step 2: Fetch entries with pagination
        entries_url = urljoin(sf.base_url, list_view['resultsUrl'])
        records = []

        while len(records) < entries_count and entries_url:
            entries_response = sf._call_salesforce('GET', entries_url)
            if entries_response.status_code != 200:
                return json.dumps({"error": f"Failed to retrieve entries: {entries_response.text}"})

            entries_data = entries_response.json()
            entries = entries_data.get('records', [])
            records.extend(entries)

            if len(records) >= entries_count:
                break

            # Check for next page
            next_page_url = entries_data.get('nextPageUrl')
            if next_page_url:
                entries_url = urljoin(sf.base_url, next_page_url)
            else:
                entries_url = None  # No more pages

        # Trim the records to the desired count
        records = records[:entries_count]

        if not records:
            return json.dumps({"error": "No entries found for the specified list view"})

    except Exception as e:
        return json.dumps({"error": f"Query failed: {e}"})

    # Return the results as a JSON string
    return json.dumps(records)
