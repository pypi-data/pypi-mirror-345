"""
Claude API Integration for getting detailed solutions
"""
from typing import Optional
import os
import json

import anthropic

def get_solution_from_claude(
    api_key: str,
    issue_type: str,
    code_snippet: str,
    message: str,
    severity: str = "medium",
) -> Optional[str]:
    """
    Get a detailed solution from Claude for an SSR issue
    
    Args:
        api_key: Anthropic API key
        issue_type: Type of SSR issue
        code_snippet: Problematic code
        message: Description of the issue
        severity: Issue severity (critical, major, medium, minor)
    """
    if not api_key:
        return None
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        # Add severity information to the prompt
        severity_descriptions = {
            "critical": "This is a critical issue that will completely break SSR functionality",
            "major": "This is a major issue that will likely cause SSR rendering failures",
            "medium": "This is a medium severity issue that may cause inconsistent SSR behavior",
            "minor": "This is a minor issue that could cause subtle differences between SSR and client rendering"
        }
        
        severity_info = severity_descriptions.get(
            severity, 
            "This issue may affect SSR compatibility"
        )
        
        prompt = f"""
        I'm working on a Laravel + Inertia.js + Vue 3 application and trying to make it compatible with Server-Side Rendering (SSR).
        
        I have identified the following issue in my code:
        
        Issue Type: {issue_type}
        Severity: {severity.upper()}
        Problem: {message}
        
        {severity_info}.
        
        Here is the code snippet:
        ```
        {code_snippet}
        ```
        
        Please provide a specific, concrete solution to make this code compatible with SSR. Include example code and explain why your solution works. Focus on Vue 3 and Inertia.js SSR best practices.
        
        For critical issues, provide detailed explanations and multiple solution approaches if relevant.
        
        Your response should be:
        1. Concise (3-5 sentences) but thorough
        2. Include specific code examples
        3. Explain why the solution works
        4. Focus on Laravel/Inertia.js/Vue 3 SSR best practices
        """
        
        # Adjust model and parameters based on issue severity
        model = "claude-3-7-sonnet-20250219"
        max_tokens = 400 if severity in ["critical", "major"] else 300
        temperature = 0.1
        
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system="You are an expert in Laravel, Inertia.js, and Vue.js Server-Side Rendering. Provide brief, specific solutions to SSR compatibility issues. Focus on practical code examples and concrete solutions.",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        return message.content[0].text
    except Exception as e:
        return f"Error getting solution from Claude: {str(e)}"