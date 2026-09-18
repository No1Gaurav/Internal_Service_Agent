import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)


def generate_response(
    user_query,
    retrieved_chunks,
    conversation_history=None
):

    context_parts = []

    for chunk in retrieved_chunks:

        context_parts.append(
            f"SOURCE: {chunk['source']}\n"
            f"POLICY:\n{chunk['text']}"
        )

    context = "\n\n---\n\n".join(context_parts)

    # ---------------------------------------------------------
    # Conversation history
    # ---------------------------------------------------------

    history_text = ""

    if conversation_history:

        history_parts = []

        for message in conversation_history:

            role = message["role"].upper()

            history_parts.append(
                f"{role}: {message['content']}"
            )

        history_text = "\n".join(history_parts)

    else:

        history_text = "No previous conversation."

    # ---------------------------------------------------------
    # Prompt
    # ---------------------------------------------------------

    prompt = f"""
You are an internal IT support agent.

Your job is to help employees using ONLY the company
policies provided below.

You are participating in an ongoing conversation, so
you MUST consider the previous messages before answering
the employee's latest message.

STRICT RULES:

1. Use only the supplied company policies for company-specific
   procedures.

2. Do not invent company policies.

3. Do not invent procedures.

4. Do not invent approval requirements.

5. Do not invent contacts or email addresses.

6. Do not invent ticket information.

7. Do not claim that a ticket has been created unless the
   application actually creates one.

8. If the employee asks whether you can raise a ticket,
   explain that the assistant can create a ticket when the
   applicable policy requires one.

9. If the policy requires information before a ticket can
   be created, ask the employee for that information.

10. Remember information from earlier messages in the
    conversation.

11. If the employee's latest message is a follow-up such as
    "yes", "no", "still not working", "should I raise it",
    or "what about that", interpret it using the previous
    conversation.

12. If the policies do not contain enough information,
    clearly say that.

13. Do not expose similarity scores to the employee.

14. Do not mention internal retrieval details.

15. Give a concise but complete response.

PREVIOUS CONVERSATION:
{history_text}

LATEST EMPLOYEE MESSAGE:
{user_query}

RETRIEVED COMPANY POLICIES:
{context}

Return ONLY the response that should be shown to the employee.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=2000
        )
    )

    return response.text