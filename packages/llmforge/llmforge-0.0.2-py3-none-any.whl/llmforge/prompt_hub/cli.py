import argparse
import os


regular_prompt_template = """
version: 1.0
metadata:
    type: prompt # type of the prompt file, can be 'prompt' or 'model_prompt'
    name: your_prompt_file_name # name of the prompt file, should be unique
    description: Optional description of this prompt collection # optional description for readability
    tags: [example, test] # optional tags for categorization, not yet implemented
    project: your_project_id_or_name # optional project name or ID for categorization

prompts:
  - pid: example_prompt # Unique identifier for the prompt, should be unique within the file
    description: A description of the prompt. # Optional description for the prompt, useful for documentation
    # Optional input variables for the prompt, these are placeholders in the prompt text, not directly used in the prompt
    input_variables:
      - "input_variable_1"
      - "input_variable_2"
    # The prompt text itself
    prompt: | # '|' indicates a multi-line string in YAML
        This is where the actual prompt text goes, with placeholders 
        like {input_variable_1} and {input_variable_2}.

  - pid: example_prompt2
    description: A description of the prompt.
    input_variables: ["input_variable_1", "input_variable_2"]
    prompt: |
        This is where the actual prompt text goes, 
        with placeholders like {input_variable_1} and {input_variable_2}.
"""

model_prompt_template = """
version: 1.0
metadata:
    type: model_prompt # type of the prompt file, can be 'prompt' or 'model_prompt'
    name: your_model_prompt_file_name # name of the model prompt file, should be unique
    description: Optional description for the model-bound prompts # optional description for readability
    tags: [model, ai, output] # optional tags for categorization, not yet implemented
    project: your_project_id_or_name # optional project name or ID for categorization

prompts:
  - pid: example_model_prompt # Unique identifier for the model prompt, should be unique within the file
    description: A description of the model prompt. # Optional description for the model prompt, useful for documentation
    # Optional input variables for the model prompt, these are placeholders in the prompt text, not directly used in the prompt
    input_variables: 
      - "field_1"
      - "field_2"
    model_attribute_id: model_attribute_id # Unique identifier for the model attribute, this is used to bind prompt with pydantic model
    # Input instruction and output instruction are optional fields that can be used to provide additional context or instructions for the model prompt, used in LLMField
    # Atleast one of them should be provided, if both are provided, they will be used as input and output instructions respectively
    # Instruction for processing the model prompt input, can be used to guide LLM on how to interpret input variables
    input_instruction: | # '|' indicates a multi-line string in YAML
        Instruction for processing the model prompt input.
    # Instruction for processing the model prompt output, can be used to guide LLM what to output
    output_instruction: | # '|' indicates a multi-line string in YAML
        Instruction for processing the model prompt output. 

  - pid: example_model_prompt2
    description: A description of the model prompt.
    input_variables: ["field_1", "field_2"]
    model_attribute_id: model_attribute_id2
    input_instruction: "Instruction for processing the model prompt input."
    output_instruction: "Instruction for processing the model prompt output."
"""

def generate_template(prompt_type: str, output_path: str):
    """
    Generate a template YAML file based on the prompt type (regular or model prompt).
    """
    if prompt_type == "regular":
        template = regular_prompt_template
    elif prompt_type == "model_prompt":
        template = model_prompt_template
    else:
        print("Invalid prompt type. Please choose 'regular' or 'model_prompt'.")
        return
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Write the generated template to the specified file path
    with open(output_path, "w") as f:
        f.write(template)
    
    print(f"Template for '{prompt_type}' has been generated and saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate YAML templates for prompt files.")
    
    # Arguments
    parser.add_argument("prompt_type", choices=["regular", "model_prompt"], help="Type of the prompt template to generate.")
    parser.add_argument("output_path",nargs='?', help="Path where the template file will be saved.", default="./prompt_template.yaml")
    
    args = parser.parse_args()
    
    if not args.output_path.endswith(".yaml"):
        print("Warning: Output file does not have a .yaml extension.")
    
    # Generate the template based on the prompt type and output path
    generate_template(args.prompt_type, args.output_path)

if __name__ == "__main__":
    main()
