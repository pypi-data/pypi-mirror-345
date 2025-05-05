# ai_article_generator

A Python library for generating articles using AI. This library provides tools and utilities to automate the creation of articles, leveraging machine learning and natural language processing techniques.

## Installation

Install the library from PyPI:

```bash
pip install ai-article-generator
```

Or, for development, clone the repository and install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Import and use the library in your Python code:

```python
from ai_article_generator.generator import ArticleGenerator
```

## Example Usage

```python
from ai_article_generator.generator import ArticleGenerator

# Example instructions for article sections
instructions = {
    "Article Header": {
        "instructions": "Write a header.",
        "response_format": {"title": "Title", "subtitle": "Subtitle"},
        "html_template": "<h1>{title}: {subtitle}</h1>",
    }
}

# Any additional data your sections might need
additional_data = {"keywords": ["AI", "journalism", "technology"]}

# Create the generator (article_type can be 'review', 'news', 'guide', 'feature', or 'generic')
generator = ArticleGenerator(
    instructions=instructions,
    additional_data=additional_data,
    article_type="feature"
    model="gpt-4o-mini"
)

# Generate the article sections as HTML
try:
    html_sections = generator.generate()
    for section, html in html_sections.items():
        print(f"Section: {section}\n{html}\n")
except Exception as e:
    print(f"Error generating article: {e}")
```

## Examples

See the example usage script:

```
lib/examples/article_generator_example.py
```

You can run it with:

```bash
python lib/examples/article_generator_example.py
```

## Project Structure

```
lib/
├── article_generator/   # Main library code
├── examples/            # Example scripts
├── tests/               # Unit tests
├── README.md            # Project documentation
├── pyproject.toml       # Build system and metadata
├── requirements.txt     # Development dependencies
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](LICENSE) 