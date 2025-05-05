import pkg_resources

# List of packages to examine
packages = [
    "ruff==0.6.7",
    "pre-commit==3.8.0",
    "pytest==8.3.3",
    "pytest-asyncio==0.23.6",
    "pyautogui==0.9.54",
    "streamlit>=1.38.0",
    "anthropic[bedrock,vertex]>=0.37.1",
    "jsonschema==4.22.0",
    "boto3>=1.28.57",
    "google-auth<3,>=2",
    "gradio>=5.6.0",
    "screeninfo",
    "uiautomation",
    "pywinauto",
    "textdistance",
    "easyocr",
    "matplotlib",
    "litellm"
]

# Function to simulate checking dependencies (since we cannot access internet)
def check_torch_dependency(package_list):
    # Known packages that depend on torch
    torch_dependent_packages = []
    
    # Known from documentation or typical usage
    known_torch_deps = {
        'easyocr': 'Depends on torch for OCR functionalities.',
        'gradio': 'Optional torch dependency for deep learning models integration.',
        'litellm': 'May depend on torch for model serving in some configurations.',
    }
    
    for package in package_list:
        pkg_name = package.split('==')[0].split('>=')[0].split('<')[0]
        if pkg_name in known_torch_deps:
            torch_dependent_packages.append((pkg_name, known_torch_deps[pkg_name]))
    
    return torch_dependent_packages

torch_dependencies = check_torch_dependency(packages)
torch_dependencies
