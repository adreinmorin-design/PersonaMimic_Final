# DreNodeMicroSaaS
Powered by PersonaMimic Autonomous SaaS Architect.## Getting Started
1. Install dependencies: `pip install -r requirements.txt`
2. Run the application: `uvicorn main:app --reload`
3. Access the API documentation at http://localhost:8000/docs
## Using the Image Optimizer
To use the image optimizer, send a POST request to `/process_image` with an image path and operation. Ensure that the file type is supported by PIL (common formats like .png, .jpg, .jpeg).
Example:
```
curl -X POST 'http://localhost:8000/process_image' -H 'Content-Type: application/json' -d '{"image_path": "/path/to/image.jpg", "operation": "resize"}'
```
## Important Files
- **prompt_bank.json**: Contains the prompt templates used by the application. Ensure this file is present and correctly formatted.
- **LICENSE**: Provides details on the software's licensing terms.