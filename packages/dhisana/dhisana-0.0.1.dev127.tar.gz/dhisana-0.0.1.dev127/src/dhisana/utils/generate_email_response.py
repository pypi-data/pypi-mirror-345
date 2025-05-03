import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from dhisana.schemas.sales import (
    ContentGenerationContext,
    MessageItem,
    MessageResponse,
    MessageGenerationInstructions
)
from dhisana.utils.assistant_tool_tag import assistant_tool
from dhisana.utils.generate_structured_output_internal import (
    get_structured_output_with_assistant_and_vector_store,
    get_structured_output_internal
)

# ---------------------------------------------------------------------------------------
# MODEL
# ---------------------------------------------------------------------------------------
class InboundEmailTriageResponse(BaseModel):
    """
    Model representing the structured response for an inbound email triage.
    - triage_status: "AUTOMATIC" or "END_CONVERSATION"
    - triage_reason: Reason text if triage_status == "END_CONVERSATION"
    - response_action_to_take: The recommended next action (e.g. SCHEDULE_MEETING, SEND_REPLY, etc.)
    - response_message: The actual body of the email response to be sent or used for approval.
    """
    triage_status: str  # "AUTOMATIC" or "END_CONVERSATION"
    triage_reason: Optional[str]
    response_action_to_take: str
    response_message: Optional[str]


# ---------------------------------------------------------------------------------------
# HELPER FUNCTION TO CLEAN CONTEXT
# ---------------------------------------------------------------------------------------
def cleanup_reply_campaign_context(campaign_context: ContentGenerationContext) -> ContentGenerationContext:
    clone_context = campaign_context.copy(deep=True)
    if clone_context.lead_info is not None:
        clone_context.lead_info.task_ids = None
        clone_context.lead_info.email_validation_status = None
        clone_context.lead_info.linkedin_validation_status = None
        clone_context.lead_info.research_status = None
        clone_context.lead_info.enchrichment_status = None
    return clone_context


# ---------------------------------------------------------------------------------------
# GET INBOUND EMAIL TRIAGE ACTION (NO EMAIL TEXT)
# ---------------------------------------------------------------------------------------
async def get_inbound_email_triage_action(
    context: ContentGenerationContext,
    tool_config: Optional[List[Dict]] = None
) -> InboundEmailTriageResponse:
    """
    Analyzes the inbound email thread, and triage guidelines
    to determine triage status, reason, and the recommended action to take.
    DOES NOT generate the final email text.
    """
    allowed_actions = [
        "UNSUBSCRIBE",
        "NOT_INTERESTED",
        "SCHEDULE_MEETING",
        "SEND_REPLY",
        "OOF_MESSAGE",
        "NEED_MORE_INFO",
        "FORWARD_TO_OTHER_USER",
        "NO_MORE_IN_ORGANIZATION",
        "OBJECTION_RAISED",
        "END_CONVERSATION",
    ]
    current_date_iso = datetime.datetime.now().isoformat()
    cleaned_context = cleanup_reply_campaign_context(context)
    if not cleaned_context.current_conversation_context.current_email_thread:
        cleaned_context.current_conversation_context.current_email_thread = []

    # Build a prompt that only requests triage info (no email body).
    triage_prompt = f"""
    You are a specialized email assistant. 
    Your task is to analyze the inbound email thread,
    and the provided triage guidelines to determine the correct triage action to take.

    1. Email thread or conversation:
    {[thread_item.model_dump() for thread_item in cleaned_context.current_conversation_context.current_email_thread]}

    2. Triage Guidelines:
    {cleaned_context.campaign_context.email_triage_guidelines}

    - If the request is standard, simple, or obviously handled by standard processes,
            set triage_status to "AUTOMATIC".
    - If the request is complex, sensitive, or needs special input,
            set triage_status to "END_CONVERSATION" and provide triage_reason.

    - Choose one action from this list: {allowed_actions}

    DO NOT reply to any PII or financial information requests; triage them as "END_CONVERSATION".
    Current date is: {current_date_iso}.
    If the user input or query is Not safe for work (NFSW), malicious, abusive or illegal END_CONVERSATION triage.

    If the user replied "thanks" or "I will get back to you later," you can end the conversation with END_CONVERSATION. 
    unless explicitly asked for more info.
    DO NOT try to spam users with multiple messages. END_CONVERSATION if the user is not interested or if multiple responses 
    have already been sent.
    If the user is responding with just "Thanks" or "Thanks for the info." end the conversation with END_CONVERSATION triage.
    If the user is not explicity asking for more information, or time for meeting end the conversation with END_CONVERSATION triage.
    If the user is saying let's schedule a meeting or catch-up, and you have not already asked for a meeting, check for a suitable time with SEND_REPLY.

    My intent is not to spam users with multiple messages and help them with info or meeting booking. Triage accordingly.
    Always check in this order. If users wants to unsubscribe, not interested Make you you set response_action_to_take to that first.:
    1. UNSUBSCRIBE
    2. NOT_INTERESTED
    3. OOF_MESSAGE
    4. SEND_REPLY
    3. END_CONVERSATION

    Keep the message response short, less than 150 words.
    Reply to user only when ABSOLUTELY necessary when user asks for more infor or time to meet or is interested in meeting. Else end the conversation with END_CONVERSATION triage.
    DO NOT SEND_REPLY if the user wants to unsubscribe or is not interested.    

    Your final output must be valid JSON with the structure:
    {{
    "triage_status": "AUTOMATIC" or "END_CONVERSATION",
    "triage_reason": "<reason if requires approval; otherwise null>",
    "response_action_to_take": "one of {allowed_actions}",
    "response_message": "<the email response to respond with if the response_action_to_take is SEND_REPLY. else keep it empty>"
    }}
    Current date: {current_date_iso}
"""

    # If there's a vector store ID, use that approach
    if (
        cleaned_context.external_known_data
        and cleaned_context.external_known_data.external_openai_vector_store_id
    ):
        triage_only, status = await get_structured_output_with_assistant_and_vector_store(
            prompt=triage_prompt,
            response_format=InboundEmailTriageResponse,
            vector_store_id=cleaned_context.external_known_data.external_openai_vector_store_id,
            tool_config=tool_config
        )
    else:
        triage_only, status = await get_structured_output_internal(
            prompt=triage_prompt,
            response_format=InboundEmailTriageResponse,
            tool_config=tool_config
        )

    if status != "SUCCESS":
        raise Exception("Error in generating triage action.")

    return triage_only


# ---------------------------------------------------------------------------------------
# CORE FUNCTION TO GENERATE SINGLE RESPONSE (ONE VARIATION)
# ---------------------------------------------------------------------------------------
async def generate_inbound_email_response_copy(
    campaign_context: ContentGenerationContext,
    variation: str,
    tool_config: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Generate a single inbound email triage response based on the provided context and
    a specific variation prompt.
    """
    allowed_actions = [
        "SCHEDULE_MEETING",
        "SEND_REPLY",
        "UNSUBSCRIBE",
        "OOF_MESSAGE",
        "NOT_INTERESTED",
        "NEED_MORE_INFO",
        "FORWARD_TO_OTHER_USER",
        "NO_MORE_IN_ORGANIZATION",
        "OBJECTION_RAISED",
        "END_CONVERSATION",
    ]
    current_date_iso = datetime.datetime.now().isoformat()
    cleaned_context = cleanup_reply_campaign_context(campaign_context)
    if not cleaned_context.current_conversation_context.current_email_thread:
        cleaned_context.current_conversation_context.current_email_thread = []

    prompt = f"""
    You are a specialized email assistant. 
    Your task is to analyze the user's email thread, the user/company info,
    and the provided triage guidelines to craft a response.

    Follow these instructions to generate the reply: 
    {variation}

    1. Understand the email thread or conversation to respond to:
    {[thread_item.model_dump() for thread_item in cleaned_context.current_conversation_context.current_email_thread] 
        if cleaned_context.current_conversation_context.current_email_thread else []}

    2. User & Company (Lead) Info:
    {cleaned_context.model_dump()}

    3. Triage Guidelines:
    {cleaned_context.campaign_context.email_triage_guidelines}

    - If the request is standard, simple, or obviously handled by standard processes,
        set triage_status to "AUTOMATIC".
    - If the request is complex, sensitive, or needs special input,
        set triage_status to "END_CONVERSATION" and provide triage_reason.

    4. Choose one action from this list: {allowed_actions}

    5. Provide your recommended email body that best addresses the user's message.
    DO NOT reply to any PII or financial information requests; triage them as "END_CONVERSATION".
    DO NOT reply anything negative about my product or company {campaign_context.lead_info.organization_name}; 
    triage them as "END_CONVERSATION".
    Current date is: {current_date_iso}.
    DO NOT share any link to internal or made up document. You can attach or send any document.
    If the user is asking for any document, point them to organization's website found in sender information if available:
    {campaign_context.sender_info.model_dump()}

    Use conversational name for company name.
    Use conversational name when using lead first name.
    Do not use special characters or spaces when using lead’s first name.
    In the subject or body DO NOT include any HTML tags like <a>, <b>, <i>, etc.
    The body and subject should be in plain text.
    If there is a link provided in the email, use it as is; do not wrap it in any HTML tags.
    DO NOT make up information. Use only the information provided in the context and instructions.
    Do NOT repeat the same message sent to the user in the past.
    Keep the thread conversational and friendly as a sales person would respond.
    Do NOT rehash/repeat the same previous message already sent. Keep the reply to the point.
    If the user replied "thanks" or "I will get back to you later," you can end the conversation with END_CONVERSATION. 
    unless explicitly asked for more info.
    DO NOT try to spam users with multiple messages. END_CONVERSATION if the user is not interested or if multiple responses 
    have already been sent.
    If the user is responding with just "Thanks" or "Thanks for the info." end the conversation with END_CONVERSATION triage.
    If the user is not explicity asking for more information, or time for meeting end the conversation with END_CONVERSATION triage.
    Keep the message response short, less than 150 words.
    Check for UNSUBSCRIBE or NOT_INTERESTED first before checking for other tirage rules.

    Your final output must be valid JSON with the structure:
    {{
    "triage_status": "AUTOMATIC" or "END_CONVERSATION",
    "triage_reason": "<reason if requires approval; otherwise null>",
    "response_action_to_take": "one of {allowed_actions}",
    "response_message": "<the email response to respond with if the response_action_to_take is SEND_REPLY. else keep it empty>"
    }}
    """


    # If there's a vector store ID, use that approach
    if (
        cleaned_context.external_known_data
        and cleaned_context.external_known_data.external_openai_vector_store_id
    ):
        initial_response, status = await get_structured_output_with_assistant_and_vector_store(
            prompt=prompt,
            response_format=InboundEmailTriageResponse,
            vector_store_id=cleaned_context.external_known_data.external_openai_vector_store_id,
            tool_config=tool_config
        )
    else:
        initial_response, status = await get_structured_output_internal(
            prompt=prompt,
            response_format=InboundEmailTriageResponse,
            tool_config=tool_config
        )

    if status != "SUCCESS":
        raise Exception("Error in generating the inbound email triage response.")

    response_item = MessageItem(
        message_id="",  # or generate one if appropriate
        thread_id="",
        sender_name=campaign_context.sender_info.sender_full_name or "",
        sender_email=campaign_context.sender_info.sender_email or "",
        receiver_name=campaign_context.lead_info.full_name or "",
        receiver_email=campaign_context.lead_info.email or "",
        iso_datetime=datetime.datetime.utcnow().isoformat(),
        subject="",  # or set some triage subject if needed
        body=initial_response.response_message
    )

    # Build a MessageResponse that includes triage metadata plus your message item
    response_message = MessageResponse(
        triage_status=initial_response.triage_status,
        triage_reason=initial_response.triage_reason,
        message_item=response_item,
        response_action_to_take=initial_response.response_action_to_take
    )
    return response_message.model_dump()


# ---------------------------------------------------------------------------------------
# MAIN ENTRY POINT - GENERATE MULTIPLE VARIATIONS
# ---------------------------------------------------------------------------------------
@assistant_tool
async def generate_inbound_email_response_variations(
    campaign_context: ContentGenerationContext,
    number_of_variations: int = 3,
    tool_config: Optional[List[Dict]] = None
) -> List[Dict[str, Any]]:
    """
    Generate multiple inbound email triage responses, each with a different 'variation'
    unless user instructions are provided. Returns a list of dictionaries conforming
    to InboundEmailTriageResponse.
    """
    # Default variation frameworks
    variation_specs = [
        "Short and friendly response focusing on quick resolution.",
        "More formal tone referencing user’s key points in the thread.",
        "Meeting-based approach if user needs further discussion or demo.",
        "Lean approach focusing on clarifying user’s questions or concerns.",
        "Solution-driven approach referencing a relevant product or case study."
    ]

    # Check if the user provided custom instructions
    message_instructions = campaign_context.message_instructions or MessageGenerationInstructions()
    user_instructions = (message_instructions.instructions_to_generate_message or "").strip()
    user_instructions_exist = bool(user_instructions)

    all_variations = []
    for i in range(number_of_variations):
        # If user instructions exist, use them for every variation
        if user_instructions_exist:
            variation_text = user_instructions
        else:
            # Otherwise, fallback to variation_specs
            variation_text = variation_specs[i % len(variation_specs)]

        try:
            triaged_response = await generate_inbound_email_response_copy(
                campaign_context=campaign_context,
                variation=variation_text,
                tool_config=tool_config
            )
            all_variations.append(triaged_response)
        except Exception as e:
            raise e

    return all_variations
