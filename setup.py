from setuptools import setup, find_packages

setup(
    name="humanizeai-pro",
    version="1.0.0",
    description="Multi-agent swarm humanizer for HumanizeAI.pro bypassing 200-word free tier limits",
    author="Antigravity Team",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        "playwright>=1.40.0",
        "rich>=13.0.0",
        "python-docx>=1.0.0",
        "pypdf>=3.0.0",
        "pdfplumber>=0.10.0",
        "reportlab>=4.0.0",
    ],
    entry_points={
        "console_scripts": [
            "humanizeai-pro=humanizeai_pro.cli:main",
        ],
    },
    python_requires=">=3.8",
)
