import re

def conversation_to_structure(conversation_history: str, user_input: str) -> list[dict]:
    """Converts a formatted conversation string to a structured message format.
    
    Parses a conversation history string containing role-prefixed messages and combines it
    with the latest user input to create a list of message dictionaries in a standardized
    structure format.

    Args
    ----
        conversation_history (str): Formatted conversation string where each message is
                                   prefixed with **role**: (e.g., "**user**: Hello").
                                   Can be None or empty.
        user_input (str): The latest user input to be added to the structure.
                         Can be None or empty.

    Returns
    -------
        list: A list of message dictionaries where each contains:
            - role (str): Message originator ('user' or 'assistant')
            - content (list): List of content dictionaries with:
                - text (str): The message content

    Notes
    -----
        - Uses regex to parse the conversation history, looking for patterns like:
          "**user**: [message]" or "**assistant**: [message]"
        - Handles None/empty inputs gracefully
        - Strips whitespace from all message content
        - The user_input is always added as the last element when present

    Examples
    --------
        >>> conversation_to_structure(
        ...     "**user**: Hi\\n**assistant**: Hello!",
        ...     "How are you?"
        ... )
        [
            {'role': 'user', 'content': [{'text': 'Hi'}]},
            {'role': 'assistant', 'content': [{'text': 'Hello!'}]},
            {'role': 'user', 'content': [{'text': 'How are you?'}]}
        ]

        >>> conversation_to_structure(None, "Hello")
        [
            {'role': 'user', 'content': [{'text': 'Hello'}]}
        ]
    """
    structure = []
    
    # If there is history, process it first
    if conversation_history and isinstance(conversation_history, str):
        pattern = r'\*\*(user|assistant)\*\*:\s*(.*?)(?=\s*\*\*(user|assistant)\*\*:|$)'
        matches = re.findall(pattern, conversation_history, re.DOTALL)
        
        for match in matches:
            role = match[0]
            content = match[1].strip()
            structure.append({
                'role': role,
                'content': [{'text': content}]
            })
    
    # Add the last user input
    if user_input and isinstance(user_input, str):
        structure.append({
            'role': 'user',
            'content': [{'text': user_input.strip()}]
        })
    
    return structure

def update_conversation_history(conversation_history: str, user_input: str, response: str) -> str:
    """Updates conversation history with new user input and assistant response.
    
    Formats and appends the new interaction to the existing conversation history.
    If the history is empty, starts a new conversation thread.

    Args
    ----
        conversation_history (str): The existing conversation history as a string.
                                  Empty string indicates a new conversation.
        user_input (str): The latest user message to be added to the history.
        response (str): The assistant's response to be added to the history.

    Returns
    -------
        str: The updated conversation history string with the new interaction
             formatted as:
             
             **user**: [user_input]
             **assistant**: [response]
             
             Subsequent interactions are appended with newlines.

    Examples
    --------
        >>> update_conversation_history('', 'Hello', 'Hi there!')
        '**user**: Hello\\n**assistant**: Hi there!'
        
        >>> update_conversation_history('**user**: Hello\\n**assistant**: Hi there!', 
        ...                          'How are you?', 
        ...                          'I\\'m good!')
        '**user**: Hello\\n**assistant**: Hi there!\\n**user**: How are you?\\n**assistant**: I\\'m good!'
    """
    if conversation_history == '':
        return f"**user**: {user_input}\n**assistant**: {response}"
    return f"{conversation_history}\n**user**: {user_input}\n**assistant**: {response}"

def extract_sql(text: str) -> str:
    """Extracts SQL query from text enclosed in <sql> tags.
    
    Searches for SQL code blocks delimited by <sql> and </sql> tags in the input text
    and returns the first matching SQL query found. Returns an empty string if no SQL
    tags are found.

    Args
    ----
        text (str): The input text potentially containing SQL code within <sql> tags.
                   Can be a multi-line string.

    Returns
    -------
        str: The extracted SQL query as a string, stripped of surrounding whitespace.
             Returns empty string if no <sql> tags are found.

    Notes
    -----
        - Only extracts the first occurrence if multiple SQL blocks exist
        - Uses DOTALL flag in regex to match across multiple lines
        - Returns the content between tags with leading/trailing whitespace removed
        - Case-sensitive to the <sql> and </sql> tags

    Examples
    --------
        >>> extract_sql("Some text <sql>SELECT * FROM users</sql> more text")
        'SELECT * FROM users'

        >>> extract_sql("No SQL here")
        ''

        >>> extract_sql("<sql>\\n  SELECT *\\n  FROM table\\n</sql>")
        'SELECT *\\n  FROM table'

        >>> extract_sql("<sql>SELECT 1</sql><sql>SELECT 2</sql>")
        'SELECT 1'
    """
    delimiter = r"<sql>(.*?)</sql>"
    match = re.search(delimiter, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""