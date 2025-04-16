import streamlit as st
from output_generator import generate_post
from reference_posts import ReferencePosts
from llm_helper import llm

# Initializing ReferencePosts
few_shot_provider = ReferencePosts(file_path="data/pro_posts.json")
unique_tags = few_shot_provider.get_tags()

st.title("LinkedIn Post Generator")

# --- Defining Primary Categories and their Associated Tags ---
category_topic_mapping = {
    "Artificial Intelligence (AI) & Machine Learning (ML)": [
        'AI', 'Artificial Intelligence', 'ArtificialIntelligence', 'ai',
        'ML', 'Machine Learning', 'MachineLearning', 'machine learning', 'machine-learning', 'machine_learning', 'machinelearning',
        'Deep Learning', 'DeepLearning', 'deep learning', 'deep-learning', 'deep_learning', 'deeplearning',
        'NLP', 'Natural Language Processing', 'nlp',
        'Computer Vision', 'ComputerVision', 'computer vision', 'computer-vision', 'computervision', '3Dvision',
        'GenAI', 'AutonomousAgents', 'MultiAgentSystems', 'Multimodal', 'MultimodalLearning',
        'Recommendation System', 'recommendation system', 'ReinforcementLearning', 'TinyML',
        'Transformer', 'transformers', 'Vision Transformers', 'GANs', 'LLM', 'LLMs', 'BERT', 'LSTMs/GRUs',
        'Self-Attention', 'self-attention', 'Positional-encoding', 'RAG'
    ],
    "AI/ML Concepts & Techniques": [
        'Algorithms', 'ActivationFunctions', 'activationfunction', 'Embeddings',
        'Gradient Descent', 'GradientDescent', 'Hyperparameter tuning',
        'Neural Networks', 'NeuralNetworks', 'neuralnetworks', 'Optimization',
        'Overfitting', 'TransferLearning', 'XGBoost', 'YOLO', 'Clustering',
        'Dimensionality_reduction', 'Sequence', 'Stochasticity', 'Unsupervised_learning'
    ],
    "Data Science & Analytics": [
        'Data Science', 'DataScience', 'data science', 'data-science', 'datascience',
        'Data Analysis', 'Data Analytics', 'DataAnalysis', 'data science',
        'Data Visualization', 'Dashboards', 'Business Intelligence', 'SQL',
        'Statistics', 'Data Imputation', 'Data Quality', 'DataQuality',
        'Data Augmentation', 'DataAugmentation', 'data_augmentation',
        'Data Cleaning', 'DataPreprocessing', 'Data Transformation',
        'Feature Engineering', 'FeatureEngineering', 'featureengineering', 'Metrics', 'Observability'
    ],
    "Development & Deployment": [
        'Coding', 'coding', 'Programming Languages', 'ProgrammingLanguages', 'programming',
        'Software Development', 'software development', 'Full Stack Development', 'CI/CD',
        'Deployment', 'deploymentsuccess', 'DevOps', 'Docker', 'Edge AI',
        'Infrastructure as Code', 'Model Serving', 'Model Training', 'ModelTraining', 'Model_Training',
        'FastAPI', 'Open-source', 'PyTorch', 'Sklearn', 'Debugging', 'debugging', 'EnvironmentSeparation'
    ],
    "Career & Professional Growth": [
        'Career', 'career', 'CareerAdvice', 'career advice', 'career-advice', 'career_advice', 'careeradvice',
        'Career Development', 'career development', 'career_development', 'Job Search Tips', 'job_search',
        'Hiring', 'Internship', 'Leadership', 'leadership', 'Learning', 'learning', 'LearningStrategy',
        'Personal Development', 'Personal Growth', 'PersonalBranding', 'PersonalDevelopment', 'PersonalGrowth', 'personal_branding', 'personal_development',
        'Productivity', 'productivity', 'Self Improvement', 'Self-Improvement', 'self-improvement', 'self_improvement',
        'SoftSkills', 'Teamwork', 'teamwork', 'teammanagement', 'Time Management', 'TimeManagement', 'time management', 'time_management',
        'Coaching', 'Entrepreneurship', 'Freelancing', 'Interview', 'interview-prep', 'interviews',
        'Networking', 'ResumeBuilding', 'resume_building'
    ],
    "Ethics & Governance": [
        'AI governance', 'AI_trust', 'Ethics', 'EthicsInTech', 'RegulatoryCompliance',
        'ResponsibleAI', 'ModelExplainability', 'Model_Explainability', 'model_explainability', 'Explainability'
    ],
    "Personal Well-being & Mindset": [
        'Confidence', 'DigitalDetox', 'Focus', 'Inspiration', 'inspiration',
        'Meditation', 'MentalHealth', 'mindfulness', 'mindset', 'health', 'health',
        'Motivation', 'motivation', 'Simplicity', 'Simplification', 'Wellness'
    ],
    "Applications & Domains": [
        'Agriculture', 'Airbnb', 'airbnb', 'Finance', 'Fraud Detection', 'Gaming',
        'Healthcare', 'healthcare', 'Neuroscience', 'ProductManagement', 'productmanagement',
        'Startup', 'UXDesign'
    ],
    "Humor & Miscellaneous": [
        'Humor', 'humor', 'Programmer humor', 'Storytelling', 'storytelling',
        'Academia', 'Simulation'
    ]
}

# --- Primary Category Selection ---
primary_categories = list(category_topic_mapping.keys())
selected_category = st.selectbox("Select a Broad Category:", primary_categories)

# --- Secondary Topic Selection (Dynamic based on Primary Category) ---
available_topics = sorted(list(set(category_topic_mapping.get(selected_category, unique_tags))))

if available_topics:
    topic = st.selectbox(f"Select a Specific Topic within '{selected_category}':", available_topics)
else:
    topic = st.text_input("Enter a Specific Topic:") # Fallback if no topics in the category

length = st.selectbox("Select the desired length:", ["Short", "Medium", "Long"])
style = st.selectbox("Select the formatting style:", ["Auto", "Use Emojis", "Plain Text"])

num_examples = st.slider("Number of Engaging Examples to Use:", min_value=0, max_value=5, value=2)
st.write("Indicate the number of past successful posts (0 to 5) to use as inspiration for the generated content's style. More examples can lead to a more aligned output.")

if st.button("Generate Post"):
    if topic:
        if few_shot_provider:
            examples = few_shot_provider.get_top_engaging_posts(length, topic, n=num_examples)
            generated_post = generate_post(length, topic, formatting_style=style, reference_post_examples=examples)
            st.subheader("Generated Post:")
            st.write(generated_post)
        else:
            st.warning("Reference-post examples are not available.")
    else:
        st.warning("Please select or enter a topic.")
