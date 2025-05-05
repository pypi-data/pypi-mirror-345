import json
import re


class Section:
    def __init__(self, name, info, ai_client, data):
        self.name = name
        self.info = info
        self.data = data
        self.ai_client = ai_client

    def generate_html(self):
        # Compose the prompt
        prompt = f"""
            You are generating structured HTML-formatted content for the '{self.name}' section of an article.

            Instructions:
            {self.info['instructions']}

            Your response must be a JSON object with these fields and formats:
            {json.dumps(self.info['response_format'], indent=2)}

            The content will be inserted into this template:
            {self.info['html_template']}
        """
        if self.data:
            prompt += f"\nAdditional data to use:\n{json.dumps(self.data, indent=2)}"

        # Call the AI client
        response = self.ai_client.generate(prompt, response_format={"type": "json_object"}, temperature=0.3)

        # Parse the response as JSON
        try:
            content_json = json.loads(response)
        except Exception as e:
            raise ValueError(f"AI response is not valid JSON: {e}\nResponse: {response}")

        template_fields = re.findall(r"\{(\w+)\}", self.info["html_template"])
        missing_fields = [field for field in template_fields if field not in content_json]
        if missing_fields:
            raise ValueError(f"Missing fields in AI response for {self.name}: {missing_fields}")

        # Fill the template with the AI's response
        return self.info["html_template"].format(**content_json)


class SectionFactory:
    def __init__(self, ai_client):
        self.ai_client = ai_client

    def create(self, name, info, data):
        # For now, always return Section, but can be extended for custom logic
        return Section(name, info, self.ai_client, data)
