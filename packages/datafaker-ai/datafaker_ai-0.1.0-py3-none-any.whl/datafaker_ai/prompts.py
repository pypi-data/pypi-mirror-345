def build_prompt(description, num_samples):
    return (
        f"Generate exactly {num_samples} synthetic records for: {description}.\n"
        f"Output ONLY a valid JSON array. Do NOT include any explanation, markdown, or formatting.\n"
        f"Each item should be a JSON object with clear fields and values."
    )
