from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from dhisana.schemas.sales import (
    ContentGenerationContext,
    MessageItem,
    MessageResponse,
    MessageGenerationInstructions
)
from dhisana.utils.generate_structured_output_internal import (
    get_structured_output_internal,
    get_structured_output_with_assistant_and_vector_store
)
from dhisana.utils.assistant_tool_tag import assistant_tool
import datetime

# ---------------------------------------------------------------------------------------
# MODEL
# ---------------------------------------------------------------------------------------
class LinkedInTriageResponse(BaseModel):
    """
    Model representing the structured response for a LinkedIn conversation triage.
    - triage_status: "AUTOMATIC" or "REQUIRES_APPROVAL"
    - triage_reason: Optional reason text if triage_status == "REQUIRES_APPROVAL"
    - response_action_to_take: The recommended next action (e.g., SEND_REPLY, WAIT_TO_SEND, STOP_SENDING, etc.)
    - response_message: The actual message (body) to be sent or used for approval.
    """
    triage_status: str  # "AUTOMATIC" or "REQUIRES_APPROVAL"
    triage_reason: Optional[str]
    response_action_to_take: str
    response_message: str


# ---------------------------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------------------------
def cleanup_reply_linkedin_context(linkedin_context: ContentGenerationContext) -> ContentGenerationContext:
    """
    Create a copy of the context and remove unneeded or sensitive fields.
    """
    clone_context = linkedin_context.copy(deep=True)
    
    # Example: removing tasks or statuses that are not needed for triage
    clone_context.lead_info.task_ids = None
    clone_context.lead_info.research_status = None
    clone_context.lead_info.email_validation_status = None
    clone_context.lead_info.linkedin_validation_status = None
    clone_context.lead_info.enchrichment_status = None
    
    return clone_context


async def generate_linkedin_response_message_copy(
    linkedin_context: ContentGenerationContext,
    variation: str,
    tool_config: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Generates a single variation of a triaged LinkedIn response using the provided context.
    Returns a structured result conforming to LinkedInTriageResponse.
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
        "OTHER"
    ]
    
    cleaned_context = cleanup_reply_linkedin_context(linkedin_context)
    
    # Safely handle the current_conversation_context if it exists.
    if cleaned_context.current_conversation_context:
        if not cleaned_context.current_conversation_context.current_email_thread:
            cleaned_context.current_conversation_context.current_email_thread = []
        
        if not cleaned_context.current_conversation_context.current_linkedin_thread:
            cleaned_context.current_conversation_context.current_linkedin_thread = []
        
        # Safely extract the conversation thread for prompt formatting.
        conversation_thread_dump = [
            thread_item.model_dump()
            for thread_item in cleaned_context.current_conversation_context.current_linkedin_thread
        ]
    else:
        # If current_conversation_context is None, use an empty thread.
        conversation_thread_dump = []
    
    current_date_iso = datetime.datetime.now().isoformat()
    prompt = f"""
    You are a specialized LinkedIn assistant.

    Your task:
      1. Analyze the current LinkedIn conversation.
      2. Inspect the user (lead) info, outreach campaign context, and any additional instructions.
      3. Decide whether to automatically send a reply or if human approval is needed (triage).
      4. If approval is needed, provide the reason.
      5. Choose one recommended next action from: {allowed_actions}.
      6. Provide a short LinkedIn message body that addresses the lead's conversation.
      MAKE SURE the message is less than 300 words.

    Use the following instructions to generate message: 
    {variation}

    1. Understand the conversation thread:
       {conversation_thread_dump}

    2. User & Company (Lead) Info:
       {cleaned_context.model_dump()}

    3. Triage Guidelines:
       {cleaned_context.campaign_context.linkedin_triage_guidelines}
       - If the request is standard, simple, or obviously handled by standard processes,
         set triage_status to "AUTOMATIC".
       - If the request is complex, sensitive, or needs special input,
         set triage_status to "END_COVERSATION" and provide triage_reason.

    4. Choose one action from this list: {allowed_actions}

    Todays date is : {current_date_iso}
    === IMPORTANT ANTI-SPAM AND RESPECT RULES ===
    1. If we have sent a message to the user within the past 24 hours and the user has not responded,
       do NOT send another message right now. Instead, triage with "END_COVERSATION".
    2. If we have sent more than 3 messages in total without any user response, do NOT send another message.
       Instead, triage with "END_COVERSATION".
    3. If the user explicitly says "don't reply", "not interested", or any equivalent,
       do NOT continue the thread. Triage with "END_COVERSATION".
    4. If the user has requested a meeting, triage as "AUTOMATIC" or "END_COVERSATION" 
       (depending on complexity), and set response_action_to_take to "SCHEDULE_MEETING".
    Craft a helpful response for scheduling.

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
    If the user is interested in a meeting, and you have not already asked for time check for a sutiable time/location to meet as appropriate.
    Keep the message response short, less than 150 words.
    Make sure the signature in body has the sender_first_name is correct and in the format user has specified.
    Check for UNSUBSCRIBE or NOT_INTERESTED first before checking for other tirage rules.
    
    === OUTPUT FORMAT ===
    Your final output must be valid JSON in this exact format:
    {{
      "triage_status": "AUTOMATIC" or "END_COVERSATION",
      "triage_reason": "<reason if END_COVERSATION; else empty or null>",
      "response_action_to_take": "<one of {allowed_actions}>",
      "response_message": "<the new or reply message>"
    }}
    """

    # Decide if we use a vector store
    if (
        cleaned_context.external_known_data 
        and cleaned_context.external_known_data.external_openai_vector_store_id
    ):
        initial_response, status = await get_structured_output_with_assistant_and_vector_store(
            prompt=prompt,
            response_format=LinkedInTriageResponse,
            vector_store_id=cleaned_context.external_known_data.external_openai_vector_store_id,
            tool_config=tool_config
        )
    else:
        initial_response, status = await get_structured_output_internal(
            prompt,
            LinkedInTriageResponse,
            tool_config=tool_config
        )

    if status != 'SUCCESS':
        raise Exception("Error in generating the triaged LinkedIn message.")
    
    response_item = MessageItem(
        message_id="",  # or generate one if appropriate
        thread_id="",
        sender_name=linkedin_context.sender_info.sender_full_name or "",
        sender_email=linkedin_context.sender_info.sender_email or "",
        receiver_name=linkedin_context.lead_info.full_name or "",
        receiver_email=linkedin_context.lead_info.email or "",
        iso_datetime=datetime.datetime.utcnow().isoformat(),
        subject="",  # or set a triage subject if needed
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
# MAIN ENTRY POINT
# ---------------------------------------------------------------------------------------
@assistant_tool
async def get_linkedin_response_message_variations(
    linkedin_context: ContentGenerationContext,
    number_of_variations: int = 3,
    tool_config: Optional[List[Dict]] = None
) -> List[Dict[str, Any]]:
    """
    Generates multiple variations of a triaged LinkedIn message and returns them all.
    Each variation is a dict conforming to LinkedInTriageResponse with keys:
        - triage_status
        - triage_reason
        - response_action_to_take
        - response_message
    """
    variation_specs = [
        "Friendly, short response with empathetic tone.",
        "Direct response referencing user’s last message or question.",
        "Meeting-oriented approach if the user seems interested in a deeper discussion.",
        "Longer, more detailed approach – reference relevant success stories or context.",
        "Minimalistic approach focusing on primary CTA only."
    ]

    # Check if the user provided custom instructions
    message_instructions = linkedin_context.message_instructions or MessageGenerationInstructions()
    user_instructions = (message_instructions.instructions_to_generate_message or "").strip()
    user_instructions_exist = bool(user_instructions)

    triaged_responses = []
    for i in range(number_of_variations):
        try:
            # If user has instructions, use those for every variation
            if user_instructions_exist:
                variation_style = user_instructions
            else:
                # Otherwise, fallback to variation_specs
                variation_style = variation_specs[i % len(variation_specs)]

            triaged_response = await generate_linkedin_response_message_copy(
                linkedin_context=linkedin_context,
                variation=variation_style,
                tool_config=tool_config
            )
            triaged_responses.append(triaged_response)
        except Exception as e:
            # You may want to log or handle the error
            raise e

    return triaged_responses
