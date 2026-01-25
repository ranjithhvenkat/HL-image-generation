import os

def load_template(template_name: str) -> str:
    """
    Reads a template file from the 'templates' directory.
    """
    # Construct absolute path to avoid 'file not found' errors relative to main.py
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_path = os.path.join(base_dir, "templates", template_name)
    
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found: {template_path}")
        
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()