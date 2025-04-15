from llm_helper import llm
from reference_posts import ReferencePosts  # Importing the class from the other file
import random
import os

os.makedirs("data", exist_ok=True)

# This instance will hold the processed posts for few-shot examples
print("Initializing ReferencePosts for post generation...")
try:
    reference_post_provider = ReferencePosts(file_path="data/pro_posts.json")
except Exception as e:
    print(f"Error initializing ReferencePosts: {e}. Few-shot examples might be unavailable.")
    reference_post_provider = None  # Set to None to handle gracefully later

def get_length_str(length):
    """Converts length category to a string description for the prompt."""
    if length == "Short":
        return "1 to 4 lines"  # Adjusted to match categorize_length logic
    if length == "Medium":
        return "5 to 10 lines"
    if length == "Long":
        return "11 lines or more"
    return "any length"  # Fallback


def get_prompt(length, tag, formatting_style="Auto", reference_post_examples=None):
    """
    Builds the LLM prompt for generating an English LinkedIn post.

    Args:
        length (str): Desired post length ("Short", "Medium", "Long").
        tag (str): The unified topic tag for the post.
        formatting_style (str): Desired formatting ("Auto", "Use Emojis",
                                        "Use Bullet Points", "Plain Text").
        few_shot_examples (list, optional): A list of example post dictionaries
                                             to guide the generation. Defaults to None.

    Returns:
        str: The fully constructed prompt for the LLM.
    """
    length_str = get_length_str(length)
    language = "English"

    prompt = f'''
Generate a LinkedIn post using the below information. Write only the post content, no preamble or explanation before it.

1) Topic: {tag}
2) Length: {length_str}
3) Language: {language}

Instructions: Write a compelling LinkedIn post in {language} about "{tag}". Aim for a **professional, insightful, and engaging tone** that encourages interaction. The post should provide **practical value or a fresh perspective** for the reader. Use clear and concise language, avoiding overly technical jargon unless the topic specifically requires it and is clearly explained.

Structure of the Post:
(a) Hook: Start with a **strong opening that grabs attention immediately**. This could be a thought-provoking question, a surprising statistic, a bold statement related to '{tag}', or a relatable observation about the professional world concerning '{tag}'.
(b) Main Idea: Clearly and concisely explain the core concept, trend, or insight related to '{tag}'. Break down complex ideas into digestible points if necessary.
(c) Examples/Analogies (Optional): If helpful for understanding '{tag}', briefly include a real-world example or an analogy. Keep it concise and directly relevant.
(d) Actionable Takeaway/Conclusion: End with a **clear takeaway, practical tip, or a thought-provoking question** that encourages readers to share their own experiences or opinions on '{tag}' in the comments.

**Focus on providing value to the reader and sparking conversation.** Avoid generic statements or overly promotional content.
'''

    if formatting_style == "Use Emojis":
        prompt += "\n4) Formatting: Incorporate relevant emojis naturally within the text to enhance readability and tone. Do not use bullet points."
    elif formatting_style == "Plain Text":
        prompt += "\n4) Formatting: Do not use any emojis or bullet points. Write in plain paragraphs only."
    elif formatting_style == "Auto":
        # Randomly choose a style for Auto
        style_instruction = random.choice([
            "\n4) Formatting: Write in plain paragraphs. You may use emojis sparingly if appropriate.",
            "\n4) Formatting: Incorporate relevant emojis naturally where they add value.",
            "\n4) Formatting: Use bullet points (using '-' or '*') for key points or lists if it improves clarity.",
            "\n4) Formatting: Feel free to use both emojis and bullet points where appropriate to enhance readability and engagement.",
            "\n4) Formatting: Write primarily in paragraphs, but you can use bullet points for lists if needed. Emojis are optional."
        ])
        prompt += style_instruction
    else:  # Default to plain text if style is unrecognized
        prompt += "\n4) Formatting: Write in plain paragraphs only."

    if reference_post_examples:
        prompt += "\n\n5) Writing Style Examples: Emulate the style, tone, and structure of the following English examples, but generate new content for the requested topic."
        for i, post_data in enumerate(reference_post_examples[:2]):  # Use a maximum of 2 examples
            post_text = post_data.get('text', 'Example text not available.')
            prompt += f'\n\n--- Top Engaging Example {i+1} ---\n{post_text}\n--- End Top Engaging Example {i+1} ---'
    else:
        prompt += "\n\n5) Writing Style Examples: No specific examples provided for this combination. Use your general knowledge of professional LinkedIn posts."

    prompt += "\n\nGenerated Post:"  # Marker for the LLM to start writing

    return prompt

def generate_post(length, tag, formatting_style="Auto", reference_post_examples=None):
    """
    Generates an English LinkedIn post using the LLM based on specified parameters
    and optional few-shot examples.

    Args:
        length (str): Desired post length ("Short", "Medium", "Long").
        tag (str): The unified topic tag for the post.
        formatting_style (str): Desired formatting ("Auto", "Use Emojis",
                                        "Use Bullet Points", "Plain Text").
        reference_post_examples (list, optional): A list of example posts to guide generation.

    Returns:
        str: The generated post content, or an error message.
    """
    print(f"\nGenerating post for Tag='{tag}', Length='{length}', Style='{formatting_style}'...")

    try:
        prompt = get_prompt(length, tag, formatting_style, reference_post_examples)
        response = llm.invoke(prompt)
        generated_content = response.content
        print("  -> LLM invocation successful.")
        return generated_content.strip()  # Remove leading/trailing whitespace
    except Exception as e:
        print(f"Error generating post: {e}")
        return f"Error: Could not generate post content. Details: {e}"


if __name__ == "__main__":
    print("\nRunning post generator script...")

    chosen_tag = "AI"  # Default example tag (can be any tag now)
    available_tags = []
    if reference_post_provider:
        available_tags = reference_post_provider.get_tags()
        if available_tags:
            # Choose a random tag from the available ones for variety
            chosen_tag = random.choice(available_tags)
        else:
            print("No tags loaded from ReferencePosts. Using default example tag.")
    else:
        print("ReferencePosts provider not initialized. Using default example tag.")

    # Define desired parameters
    post_length = "Medium"
    post_style = "Auto"  # Try different styles
    example_posts_for_test = [{"text": "Test example post 1."}, {"text": "Test example post 2."}]

    # Generate the post WITH few-shot examples for testing
    generated_post_content = generate_post(post_length, chosen_tag, formatting_style=post_style, reference_post_examples=example_posts_for_test)

    # Print the result
    print("\n--- Generated LinkedIn Post ---")
    print(generated_post_content)
    print("--- End Generated Post ---")

    print("\nPost generator script finished.")