# VBI Evaluate Blogs

`vbi_evaluate_blogs` is a Python package designed to evaluate Vietnamese crypto blog content quality. It uses Azure OpenAI to analyze text quality, image relevance, and fact accuracy with a focus on Web3/DeFi content.

## Features

### 1. Text Content Evaluation (`check_text_module.py`)
- Analyzes article structure and organization
- Evaluates content quality and technical accuracy
- Checks grammar and writing style for Vietnamese crypto content
- Provides SEO optimization recommendations
- Generates comprehensive quality reports

### 2. Image Analysis (`check_image_module.py`) 
- Analyzes image relevance and quality
- Evaluates alt text and metadata
- Checks image-text alignment
- Provides visual accessibility recommendations
- Supports common image formats (jpg, png, webp, etc.)

### 3. Fact Checking (`check_fact_module.py`)
- Verifies claims using web search
- Analyzes source credibility
- Provides evidence-based verification
- Uses SearxNG for research
- Supports Vietnamese language validation

## Installation

```bash
pip install vbi-evaluate-blogs
playwright install
```

## Quick Start

1. Set up environment variables:

```properties
AZURE_OPENAI_API_KEY="your_api_key"
AZURE_OPENAI_ENDPOINT="your_endpoint"
SEARXNG_URL="your_searx_instance" # For fact checking
```

2. Basic usage:

```python
from vbi_evaluate_blogs import check_text, check_image, check_fact
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize models
text_llm = AzureChatOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    model="o3-mini",
    api_version="2024-12-01-preview"
)

image_llm = AzureChatOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    model="gpt-4o-mini", # Vision model required
    api_version="2024-08-01-preview",
    temperature=0.7,
    max_tokens=16000
)

# Example content
content = """
# Sample Vietnamese Crypto Blog
Content with ![](image.jpg) and technical claims...
"""

# Get comprehensive analysis
text_report = check_text(text_llm, content)
image_report = check_image(text_llm, image_llm, content)
fact_report = check_fact(text_llm, content)
```

## Module Details

### Text Analysis Module
```python
# Evaluate text content quality
result = check_text(text_llm, content)
print(result)
"""
Returns detailed report covering:
- Article structure analysis
- Content quality evaluation
- Grammar and style check
- SEO recommendations
"""
```

### Image Analysis Module
```python
# Analyze images in content
result = check_image(text_llm, image_llm, content)
print(result)
"""
Returns comprehensive report including:
- Image relevance scores
- Alt text evaluation
- Visual accessibility analysis
- Image-text alignment check
"""
```

### Fact Checking Module
```python
# Verify factual claims
result = check_fact(text_llm, content)
print(result)
"""
Returns fact check report with:
- Claim extraction
- Evidence analysis
- Source credibility
- Verification results
"""
```

## Advanced Configuration

### Custom Evaluation Criteria

You can customize the evaluation criteria by modifying the prompt templates in each module:

```python
from vbi_evaluate_blogs.check_text_module import check_article_structure

# Custom structure analysis
result = check_article_structure(
    llm=text_llm,
    text=content,
    custom_criteria="Your custom evaluation criteria..."
)
```

### Language Settings

The modules default to Vietnamese but support other languages:

```python
from vbi_evaluate_blogs.check_image_module import ImageAnalyzer

analyzer = ImageAnalyzer(
    text_llm=text_llm,
    image_llm=image_llm,
    language="en"  # Change output language
)
```

## Command Line Usage

Evaluate content directly from files:

```bash
# Full analysis 
python -m vbi_evaluate_blogs --file blog.md

# Specific checks
python -m vbi_evaluate_blogs --file blog.md --text --images
python -m vbi_evaluate_blogs --file blog.md --facts
```

## License

MIT License. See LICENSE file for details.