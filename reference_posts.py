import pandas as pd
import json
import os

os.makedirs("data", exist_ok=True)

class FewShotPosts:
    def __init__(self, file_path="data/pro_posts.json"):
        """
        Initializes the FewShotPosts class by loading and processing posts.

        Args:
            file_path (str): Path to the processed posts JSON file.
        """
        self.df = None
        self.unique_tags = []
        try:
            self.load_posts(file_path)
            if self.unique_tags:
                print(f"Loaded {len(self.unique_tags)} unique tags. Sample: {self.unique_tags[:10]}")
            else:
                print("No unique tags found in the processed data.")
        except FileNotFoundError:
            print(f"Warning: Processed posts file not found at {file_path}. Few-shot examples and tag list will be unavailable.")
            # Initializing empty dataframe and tags list to avoid errors later
            self.df = pd.DataFrame(columns=['text', 'line_count', 'tags', 'language', 'length', 'engagement'])
            self.unique_tags = []
        except Exception as e:
            print(f"Error loading or processing posts from {file_path}: {e}")
            self.df = pd.DataFrame(columns=['text', 'line_count', 'tags', 'language', 'length', 'engagement'])
            self.unique_tags = []


    def load_posts(self, file_path):
        """
        Loads posts from a JSON file, normalizes them into a DataFrame,
        categorizes their length, and extracts unique tags. Assumes posts are English.

        Args:
            file_path (str): Path to the processed posts JSON file.
        """
        with open(file_path, encoding="utf-8") as f:
            try:
                posts = json.load(f)
            except json.JSONDecodeError:
                print(f"Error: Could not decode JSON from {file_path}")
                posts = [] # Treat as empty if invalid JSON

            if not posts: # Handle empty file or decode error
                print(f"Warning: File {file_path} is empty or invalid. No posts loaded.")
                self.df = pd.DataFrame(columns=['text', 'line_count', 'tags', 'language', 'length', 'engagement'])
                self.unique_tags = []
                return

            self.df = pd.json_normalize(posts)
            print(f"Loaded {len(self.df)} posts into DataFrame.")

            # --- Data Cleaning and Column Handling ---
            # Line Count and Length Category
            if 'line_count' not in self.df.columns:
                print("Warning: 'line_count' column missing. Setting length to 'Unknown'.")
                self.df['line_count'] = pd.NA # Using pandas NA for missing integers
                self.df['length'] = "Unknown"
            else:
                # Ensure line_count is numeric, coercing errors to NA
                self.df['line_count'] = pd.to_numeric(self.df['line_count'], errors='coerce')
                # Categorizing length, handling NA values
                self.df['length'] = self.df['line_count'].apply(self.categorize_length)

            # Tags
            if 'tags' not in self.df.columns:
                print("Warning: 'tags' column missing. Tags will be empty.")
                self.df['tags'] = [[] for _ in range(len(self.df))] # Add empty list for tags
                self.unique_tags = []
            else:
                # Ensuring tags are lists, for handling potential NaNs or non-list entries gracefully
                self.df['tags'] = self.df['tags'].apply(lambda x: x if isinstance(x, list) else [])
                # Flatten the list of tags and to get unique ones
                try:
                    all_tags = [tag for sublist in self.df['tags'] for tag in sublist if isinstance(tag, str)]
                    self.unique_tags = sorted(list(set(all_tags))) # Sort for consistency
                except Exception as e:
                    print(f"Error processing tags column: {e}")
                    self.unique_tags = []

            # Language
            if 'language' not in self.df.columns:
                print("Warning: 'language' column missing. Assuming 'English'.")
                self.df['language'] = "English"
            else:
                self.df['language'] = self.df['language'].fillna("English")

            # Text
            if 'text' not in self.df.columns:
                print("Warning: 'text' column missing. Setting to empty string.")
                self.df['text'] = ""

            # Engagement
            if 'engagement' not in self.df.columns:
                print("Warning: 'engagement' column missing. Setting to 0.")
                self.df['engagement'] = 0
            else:
                self.df['engagement'] = pd.to_numeric(self.df['engagement'], errors='coerce').fillna(0).astype(int)


    def get_filtered_posts(self, length, tag):
        """
        Filters posts based on length category and tag, assuming English language.

        Args:
            length (str): The desired length category ("Short", "Medium", "Long").
            tag (str): The tag to filter by.

        Returns:
            list: A list of dictionaries representing the filtered posts.
                 Returns empty list if df is None, empty, or filtering fails.
        """
        if self.df is None or self.df.empty:
            return []

        # Ensuring required columns exist before filtering
        required_cols = ['tags', 'language', 'length', 'text', 'engagement']
        if not all(col in self.df.columns for col in required_cols):
            print("Warning: DataFrame is missing required columns for filtering.")
            return []

        try:
            df_filtered = self.df[
                (self.df['tags'].apply(lambda tags: isinstance(tags, list) and tag in tags)) &
                (self.df['language'].astype(str).str.lower() == 'english') &
                (self.df['length'] == length)
            ]
            return df_filtered[['text', 'tags', 'length', 'engagement']].to_dict(orient='records')
        except Exception as e:
            print(f"Error during filtering: {e}")
            return []

    def get_top_engaging_posts(self, length, tag, n=2):
        """
        Returns the top N most engaging posts for a given length and tag.

        Args:
            length (str): The desired length category ("Short", "Medium", "Long").
            tag (str): The tag to filter by.
            n (int): The number of top engaging posts to return (default is 2).

        Returns:
            list: A list of dictionaries representing the top N engaging posts,
                  sorted by engagement in descending order. Returns an empty list
                  if no matching posts are found or if 'engagement' column is missing.
        """
        if self.df is None or self.df.empty or 'engagement' not in self.df.columns:
            return []

        filtered_posts = self.get_filtered_posts(length, tag)
        if not filtered_posts:
            return []

        # Sort by engagement in descending order
        sorted_posts = sorted(filtered_posts, key=lambda x: x.get('engagement', 0), reverse=True)

        return sorted_posts[:n]


    def categorize_length(self, line_count):
        """
        Categorizes posts into "Short", "Medium", or "Long" based on line count.

        Args:
            line_count (int or float or pd.NA): The number of lines in the post.

        Returns:
            str: The length category ("Short", "Medium", "Long", "Unknown").
        """
        if pd.isna(line_count):
            return "Unknown"
        try:
            count = int(line_count) # Ensuring it's an integer for comparison
            if count < 5:
                return "Short"
            elif 5 <= count <= 10:
                return "Medium"
            else: # 11 or more lines
                return "Long"
        except (ValueError, TypeError):
            return "Unknown" # Handle cases where conversion fails


    def get_tags(self):
        """
        Returns the list of unique tags found in the loaded posts.
        This now reflects all unique tags after the (potentially) unrestricted
        extraction and the subsequent unification process.

        Returns:
            list: A list of unique tags.
        """
        return self.unique_tags


if __name__ == "__main__":
    print("Initializing FewShotPosts...")
    # Instantiate the class (loads data)
    fs = FewShotPosts(file_path="data/pro_posts.json")

    # Get available tags (all unique unified tags)
    available_tags = fs.get_tags()
    if available_tags:
        print("\nAvailable tags (all unique unified tags):", available_tags)

        # Get filtered posts (original method)
        if available_tags:
            example_tag = available_tags[0]
            print(f"\nGetting examples for 'Medium' length and tag: {example_tag} (using get_filtered_posts)")
            example_posts = fs.get_filtered_posts("Medium", example_tag)
            if example_posts:
                print("Found examples:")
                for i, post in enumerate(example_posts[:2]): # Print max 2 examples
                    print(f"--- Example {i+1} ---")
                    print(post['text'])
                    print(f"Engagement: {post.get('engagement', 'N/A')}")
                    print("-" * 20)
            else:
                print("No matching examples found for this criteria (using get_filtered_posts).")

            # Get top engaging posts
            print(f"\nGetting top 2 engaging posts for 'Medium' length and tag: {example_tag} (using get_top_engaging_posts)")
            top_engaging_posts = fs.get_top_engaging_posts("Medium", example_tag, n=2)
            if top_engaging_posts:
                print("Top engaging examples:")
                for i, post in enumerate(top_engaging_posts):
                    print(f"--- Top Engaging Example {i+1} ---")
                    print(post['text'])
                    print(f"Engagement: {post.get('engagement', 'N/A')}")
                    print("-" * 20)
            else:
                print("No matching posts found for this criteria (using get_top_engaging_posts).")
        else:
            print("\nNo tags available to filter examples.")
    else:
        print("\nNo tags loaded from FewShotPosts.")

    print("\nFewShotPosts script finished.")