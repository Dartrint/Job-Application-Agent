"""Shared sample data for demo and testing"""


def load_sample_data() -> tuple[str, str]:
    """Load sample job description and CV text."""
    sample_job = """
Senior AI/ML Engineer - San Francisco

Company: TechCorp AI
Location: San Francisco, CA
Employment Type: Full-time
Salary: $180K - $250K + equity

About the role:
We're looking for a Senior AI/ML Engineer to join our core platform team. You'll be responsible for building and scaling our LLM-based recommendation engine that powers our product for millions of users.

Key Responsibilities:
- Design and implement machine learning pipelines using LangChain and LangGraph
- Develop and optimize RAG (Retrieval-Augmented Generation) systems
- Build and maintain production LLM applications
- Collaborate with data engineers to create efficient data pipelines
- Mentor junior engineers on AI/ML best practices
- Contribute to open-source ML projects

Required Skills:
- 5+ years of experience in ML/AI engineering
- Strong Python expertise
- Experience with LLMs and prompt engineering
- Knowledge of LangChain, LangGraph, or similar frameworks
- Understanding of vector databases and embeddings
- System design and distributed systems knowledge
- Experience with deployment (Docker, Kubernetes)

Nice to Have:
- Contributions to open-source ML projects
- Experience with fine-tuning large language models
- Knowledge of agent frameworks
- Experience with cloud platforms (AWS, GCP, Azure)
- Published research or technical writing

We offer:
- Competitive compensation with equity
- Remote/Hybrid work flexibility
- Professional development budget
- Health insurance and benefits
"""

    sample_cv = """
John Doe
San Francisco, CA | john.doe@email.com | github.com/johndoe | linkedin.com/in/johndoe

PROFESSIONAL SUMMARY
Experienced AI/ML Engineer with 6+ years building production ML systems and LLM applications.
Expertise in building scalable machine learning pipelines, working with large language models,
and leading technical initiatives.

EXPERIENCE

Senior ML Engineer | DataSystems Inc. (2022 - Present)
- Led development of LLM-powered chatbot using LangChain, reducing customer support costs by 40%
- Designed and implemented RAG system for knowledge base retrieval, achieving 95% accuracy
- Architected ML pipeline processing 1M+ documents daily using Spark and Kubernetes
- Mentored team of 3 junior engineers on ML best practices and production deployment

ML Engineer | CloudAI Corp. (2020 - 2022)
- Built recommendation engine using collaborative filtering, serving 5M+ users
- Implemented prompt engineering strategies for GPT-3 integration
- Created vector database infrastructure using Pinecone and ChromaDB
- Optimized model inference reducing latency by 60%

Python Developer | StartupXYZ (2018 - 2020)
- Developed backend services in Python for data processing
- Built data pipelines using Apache Airflow
- Implemented caching strategies using Redis

EDUCATION
BS Computer Science, UC Berkeley (2018)
Relevant Coursework: Machine Learning, Natural Language Processing, Distributed Systems

TECHNICAL SKILLS
Languages: Python, SQL, JavaScript
ML/AI: LangChain, LangGraph, TensorFlow, PyTorch, scikit-learn, Hugging Face
Databases: PostgreSQL, MongoDB, Redis, Pinecone, ChromaDB
Cloud: AWS (EC2, S3, SageMaker), Docker, Kubernetes
Tools: Git, Jupyter, Airflow, Grafana, Prometheus

PROJECTS & ACHIEVEMENTS
- Open Source Contributor: LangChain community (100+ merged PRs)
- Technical Writer: Published 5 articles on Medium about LLM applications
- Conference Speaker: Talks on RAG systems at ML conferences
"""
    return sample_job, sample_cv
