<img src="https://github.com/user-attachments/assets/6f196672-1017-497b-8a68-11a3e5c902ca" width="300"/>


# LinkedIn Post Generator 🚀

An AI-powered web app built using Streamlit that helps users generate engaging, high-quality LinkedIn posts tailored to specific topics in AI, ML, Data Science, Career Development, and more.

![App Screenshot](https://github.com/user-attachments/assets/a53cceb3-e713-4e28-9acc-ecf03a32256b)

##  Features

- 🔧 Custom post generation based on selected topics
- 🧠 Uses few-shot learning with real LinkedIn post examples
- 🗂 Categories include:
  - Artificial Intelligence & Machine Learning
  - Data Science & Analytics
  - Career & Personal Growth
  - Development & Deployment
  - Ethics, Mindset, and more!
- 📏 Adjustable post length (Short, Medium, Long)
- ✨ Formatting styles: Plain, Emojis, or Auto

##  Preview

> "Looking to make your job search more visible on LinkedIn? Get AI-generated post drafts tailored to your niche and tone. Just pick a topic and go!"

![LinkedIn Post Generator Demo](https://github.com/user-attachments/assets/e6fce6e5-3002-44e7-806a-d5598c58f777)

##  Tech Stack

- `Python`
- `Streamlit`
- `OpenAI LLM` (via `llm_helper.py`)
- `Custom few-shot data` in JSON format
- Modular design for scalable topic/tag expansion

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- OpenAI API Key (set in your environment or `.env`)

### Installation

```bash
git clone https://github.com/SaidaMansoor/LinkedIn-Post-Generator.git
cd linkedin-post-generator
pip install -r requirements.txt
streamlit run main.py
```

## 💡 Inspiration

Writing a great LinkedIn post can be tough. This tool bridges the gap by combining real post examples and generative AI to craft personalized, professional content in seconds.

## 📌 Limitations

- 🌐 Currently supports English only
- 🧠 Model quality depends on prompt and data variety
- ❌ No grammar/spell correction (assumes LLM handles that)

## 🙌 Contributing

Want to add more categories or improve prompt design? PRs are welcome!

## 🙏 Acknowledgements

- This project was inspired by the YouTube tutorial by codebasics.
- Special thanks to them for sharing their approach to building an AI-powered LinkedIn post generator.
- I customized and extended the project by adding:
  - Custom category-topic mapping
  - Few-shot examples with curated LinkedIn posts
  - UI enhancements and personalization

Happy posting! 📝✨
