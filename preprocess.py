import json
import os
from llm_helper import llm 
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException


os.makedirs("data", exist_ok=True)

def process_posts(raw_file_path, processed_file_path):
    """
    Reads raw posts, extracts metadata, unifies tags using an LLM,
    and saves the enriched posts.

    Args:
        raw_file_path (str): Path to the raw JSON posts file.
        processed_file_path (str): Path where the processed JSON file will be saved.
    """
    try:
        with open(raw_file_path, encoding='utf-8') as file:
            posts = json.load(file)
    except FileNotFoundError:
        print(f"Error: Raw posts file not found at {raw_file_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {raw_file_path}")
        return

    enriched_posts = []
    print(f"Starting metadata extraction for {len(posts)} posts...")
    for i, post in enumerate(posts):
        if 'text' not in post:
            print(f"Warning: Post {i} missing 'text' key. Skipping.")
            continue
        try:
            print(f"Processing post {i+1}/{len(posts)}...")
            metadata = extract_metadata(post['text'])
            # Merges post data with extracted metadata (Requires Python 3.9+)
            post_with_metadata = post | metadata
            enriched_posts.append(post_with_metadata)
            print(f"  -> Extracted metadata: {metadata}")
        except OutputParserException as e:
            print(f"Error parsing LLM response for post {i}: {e}. Skipping post.")
            
        except Exception as e:
            print(f"An unexpected error occurred processing post {i}: {e}. Skipping post.")

    if not enriched_posts:
        print("No posts were successfully enriched. Exiting.")
        return

    print("Starting tag unification...")
    try:
        unified_tags_map = get_unified_tags(enriched_posts)
        print(f"  -> Generated unified tag map for {len(unified_tags_map)} original tags.")
    except OutputParserException as e:
        print(f"Error parsing LLM response for tag unification: {e}. Cannot unify tags.")

        unified_tags_map = None
    except Exception as e:
        print(f"An unexpected error occurred during tag unification: {e}. Cannot unify tags.")
        unified_tags_map = None


    final_posts = []
    if unified_tags_map:
        print("Applying unified tags...")
        for post in enriched_posts:
            if 'tags' in post and isinstance(post['tags'], list):
                current_tags = post['tags']
                # Map tags safely, keeping original if not in map
                new_tags = {unified_tags_map.get(tag, tag) for tag in current_tags}
                post['tags'] = sorted(list(new_tags)) # Sort for consistency
            final_posts.append(post)
        print("  -> Unified tags applied.")
    else:
        print("Skipping tag unification step due to previous errors.")
        final_posts = enriched_posts # Use posts with original extracted tags


    try:
        with open(processed_file_path, encoding='utf-8', mode="w") as outfile:
            json.dump(final_posts, outfile, indent=4, ensure_ascii=False)
        print(f"Successfully processed and saved {len(final_posts)} posts to {processed_file_path}")
    except IOError as e:
        print(f"Error writing processed posts to {processed_file_path}: {e}")
    except TypeError as e:
         print(f"Error serializing final posts to JSON: {e}")


def extract_metadata(post_text):
    """
    Uses an LLM to extract line count and up to two relevant tags from post text.

    Args:
        post_text (str): The text content of the LinkedIn post.

    Returns:
        dict: A dictionary containing 'line_count' and 'tags'.

    Raises:
        OutputParserException: If the LLM response cannot be parsed as JSON.
    """
    template = '''
You are given the text content of a single LinkedIn post. Your task is to extract specific metadata.
Follow these instructions precisely:
1. Analyze the post text provided below the triple backticks.
2. Determine the number of lines in the post (count lines separated by newline characters '\\n'). Treat empty lines as lines.
3. **Identify the ONE or TWO MOST relevant tags that best describe the post's content.**
4. Format your entire response as a single, valid JSON object. Do NOT include any text before or after the JSON object (no preamble, no explanations, no markdown formatting like ```json).
5. The JSON object must contain exactly these two keys: "line_count" (integer) and "tags" (JSON array of strings, max 2 elements).

Post Text:
```{post}```
'''

    pt = PromptTemplate.from_template(template)
    chain = pt | llm
    try:
        response = chain.invoke(input={"post": post_text})
        content = response.content 
    except Exception as e:
        raise OutputParserException(f"LLM invocation failed: {e}")

    try:
        json_parser = JsonOutputParser()
        res = json_parser.parse(content)
        # Basic validation
        if not isinstance(res, dict) or "line_count" not in res or "tags" not in res:
            raise OutputParserException("Parsed JSON missing required keys 'line_count' or 'tags'.")
        # Validate line_count
        if not isinstance(res["line_count"], int) or res["line_count"] < 0:
            raise OutputParserException(f"Invalid 'line_count': {res['line_count']}. Must be a non-negative integer.")
        # Validate tags
        if isinstance(res["tags"], list):
            if len(res["tags"]) > 2:
                print(f"Warning: LLM returned {len(res['tags'])} tags, keeping only the first two.")
            res["tags"] = [tag.strip() for tag in res["tags"] if isinstance(tag, str) and tag.strip()][:2] # Clean and limit
        else:
            res["tags"] = [] # If not a list, treat as empty

    except (json.JSONDecodeError, OutputParserException) as e:
        error_message = f"Failed to parse LLM response into valid JSON metadata. Response content:\n---\n{content}\n---\nError: {e}"
        raise OutputParserException(error_message)
    return res


def get_unified_tags(posts_with_metadata):
    """
    Collects unique tags from posts and uses an LLM to create a unified mapping.

    Args:
        posts_with_metadata (list): List of post dictionaries, each with a 'tags' key.

    Returns:
        dict: A dictionary mapping original tags to unified tags.

    Raises:
        OutputParserException: If the LLM response cannot be parsed as JSON.
    """
    unique_tags = set()
    # Loop through each post and extract the tags safely
    for post in posts_with_metadata:
        if 'tags' in post and isinstance(post['tags'], list):
            unique_tags.update(tag for tag in post['tags'] if isinstance(tag, str)) # Ensure tags are strings

    if not unique_tags:
        print("No unique tags found to unify.")
        return {} # Return empty map if no tags

    unique_tags_list = sorted(list(unique_tags))
    tags_string = ','.join(unique_tags_list)

    template = '''I will give you a list of tags, separated by commas. Your goal is to act as a strict tag unification and generalization engine. Analyze the list and create a mapping where each original tag maps to a single, unified, and more general category tag. Aim to reduce the total number of unique tags to around 100, focusing on broader themes. Follow the rules and examples below carefully.

**Rules:**
1.  **Unify and Merge Aggressively:** Combine similar or related tags into significantly broader, consistent category tags. Prioritize higher-level concepts. Use Title Case for all final unified category tags (e.g., "AI Applications").
    * Example 1: "Jobseekers", "Job Hunting", "Placement Tips", "Resume Building", "Interview Prep", "Interview Tips" should merge to "Career Advice".
    * Example 2: "Motivation", "Inspiration", "Drive", "Mindfulness", "Wellness", "Mental Health", "Self Improvement", "Personal Growth", "Personal Development", "Morning Routine", "Productivity Hacks", "Time Management" should merge to "Personal & Professional Growth".
    * Example 3: Various specific AI/ML techniques and concepts like "Convolutional Neural Networks", "Recurrent Neural Networks", "Transformer Architecture", "Attention Mechanism", "Embeddings", "Backpropagation", "Gradient Descent", "Hyperparameter Tuning", "Regularization", "Optimization", "Activation Functions" should merge to broader categories like "Deep Learning Techniques", "Neural Network Fundamentals", or "Model Training & Optimization".
    * Example 4: Specific AI applications like "Computer Vision", "NLP", "Natural Language Processing", "Object Detection", "Image Processing", "Semantic Segmentation", "Speech Recognition" should merge to "AI Applications".
    * Example 5: Specific AI/ML tools and libraries like "Sklearn", "PyTorch", "TensorFlow", "OpenCV", "Transformers", "FastAPI", "MLflow" should merge to "AI/ML Tools & Frameworks".
    * Example 6: Different aspects of AI development and deployment like "AI Debugging", "AI Deployment", "AI Engineering", "AI Infrastructure", "AI Model Deployment", "AI Model Development", "AI Pipelines", "CI/CD", "Docker" should merge to "AI/ML Development & Deployment".
    * Example 7: Ethical and governance aspects like "AI Ethics", "AI Governance", "AI Regulation", "Responsible AI", "Bias Reduction", "Data Bias", "Model Bias", "Explainable AI" should merge to "AI Ethics & Governance".
    * **Crucial Example 8 (AI Humor):** Tags like "AI Humor", "Tech Lightheartedness", "Developer Jokes", "Coding Humor", "Career Humor", "Humor", "Developer Jokes", "Coding Frustration" should merge specifically to "AI/Tech Humor".

2.  **Aim for Around 100 Unified Tags:** Be aggressive in merging to achieve a significantly reduced set of broader categories. If very specific tags don't clearly fit into an existing broader category, consider creating a new, moderately general category. Ensure EVERY original tag provided in the list below is present as a key in your output JSON map.

3.  **Output Format:** Respond ONLY with a single, valid JSON object. Do not include any text before or after the JSON object. Start the response directly with `{`.

4.  **JSON Structure:** The JSON object MUST be a flat dictionary where each original tag is a key, and the value is the single unified category tag it maps to. Example: {"Original Tag 1": "Unified Category A", "Original Tag 2": "Unified Category B", ...}

List of Original Tags:
{tags}
'''
    pt = PromptTemplate.from_template(template)
    chain = pt | llm
    try:
        response = chain.invoke(input={"tags": tags_string})
        content = response.content 
    except Exception as e:
         raise OutputParserException(f"LLM invocation failed for tag unification: {e}")

    try:
        json_parser = JsonOutputParser()
        res = json_parser.parse(content)
        # Validation: Ensuring it's a dict and values are strings
        if not isinstance(res, dict):
            raise OutputParserException("Unified tag map is not a dictionary.")
        # Check if all original tags are keys in the response map
        missing_keys = unique_tags - set(res.keys())
        if missing_keys:
             print(f"Warning: LLM response for unified tags is missing keys for: {missing_keys}")
             # Add missing keys mapping to themselves to avoid errors later
             for key in missing_keys:
                 res[key] = key # Map missing tags to themselves

        for key, value in res.items():
            if not isinstance(value, str):
                print(f"Warning: Unified tag for '{key}' is not a string ('{value}'). Converting to string.")
                res[key] = str(value)

    except (json.JSONDecodeError, OutputParserException) as e:
        error_message = f"Failed to parse LLM response into valid JSON tag map. Response content:\n---\n{content}\n---\nError: {e}"
        raise OutputParserException(error_message)
    return res


if __name__ == "__main__":
    print("Running preprocessing script...")
    raw_posts_file = "data/raw_posts.json"
    processed_posts_file = "data/pro_posts.json"
    process_posts(raw_posts_file, processed_posts_file)
    print("Preprocessing finished.")