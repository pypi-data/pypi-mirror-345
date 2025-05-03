# TBH Secure Agents

<img width="618" alt="Main" src="https://github.com/user-attachments/assets/dbbf5a4f-7b0b-4f43-9b37-ef77dc761ff1" />

A secure multi-agent framework by TBH.AI with enhanced security features, guardrails, and protection against AI attacks.

## Key Features

- **Enhanced Security**: Built-in protection against prompt injection, data leakage, and other AI security threats
- **Guardrails**: Dynamic control of expert behavior through template variables and conditional formatting
- **Security Profiles**: Predefined security configurations for different use cases
- **Multi-Agent Collaboration**: Coordinate multiple AI experts to solve complex problems
- **Structured Outputs**: Ensure consistent and reliable results

## Installation

```bash
pip install tbh-secure-agents
```

## Documentation

Full documentation, including installation instructions, usage guides, and details on the security features, can be found in the `docs/` directory:

*   **[Installation Guide](./docs/installation.md)**
*   **[Usage Guide](./docs/usage_guide.md)**
*   **[Security Features](./docs/security_features_comprehensive.md)**
*   **[Guardrails Guide](./docs/guardrails_comprehensive.md)**
*   **[Security Profiles](./docs/security_profiles_guide.md)**
*   **[Version Changes](./docs/version_changes.md)**

## Quick Start

```python
from tbh_secure_agents import Expert, Operation, Squad
import os

# Set your API key
api_key = os.environ.get('GOOGLE_API_KEY')

# Create experts with security profiles
researcher = Expert(
    specialty="Research Expert specializing in {topic_area}",
    objective="Research and analyze information about {specific_topic}",
    background="You have extensive knowledge in {topic_area} research.",
    security_profile="high_security",
    api_key=api_key
)

writer = Expert(
    specialty="Content Writer",
    objective="Create engaging content based on research findings",
    background="You excel at creating clear, concise content.",
    security_profile="medium_security",
    api_key=api_key
)

# Create operations with template variables
research_operation = Operation(
    instructions="""
    Research the topic of {specific_topic} within the field of {topic_area}.
    Focus on recent developments and key concepts.

    {depth, select,
      basic:Provide a high-level overview suitable for beginners.|
      intermediate:Include more detailed information for those with some knowledge.|
      advanced:Provide in-depth analysis for experts in the field.
    }
    """,
    output_format="A comprehensive research summary with key findings",
    expert=researcher
)

writing_operation = Operation(
    instructions="""
    Based on the research findings, create a {content_type} about {specific_topic}.

    {tone, select,
      formal:Use a professional, academic tone.|
      conversational:Use a friendly, approachable tone.|
      technical:Use precise technical language.
    }

    The content should be suitable for a {audience_level} audience.
    """,
    output_format="A well-structured {content_type} with clear sections",
    expert=writer
)

# Create a squad with the experts and operations
research_squad = Squad(
    experts=[researcher, writer],
    operations=[research_operation, writing_operation],
    process="sequential",
    security_level="high"
)

# Define guardrail inputs
guardrail_inputs = {
    "topic_area": "artificial intelligence",
    "specific_topic": "large language models",
    "depth": "intermediate",
    "content_type": "blog post",
    "tone": "conversational",
    "audience_level": "general"
}

# Deploy the squad with guardrails
result = research_squad.deploy(guardrails=guardrail_inputs)
print(result)
```

## Contributing

Contributions are welcome! Please see the `CONTRIBUTING.md` file (to be created) and refer to the documentation in the `docs/` directory for project structure and goals.

## License

This project is licensed under the Apache License 2.0 - see the `LICENSE` file for details.

## Contact

TBH.AI
Saish - saish.shinde15@gmail.com
