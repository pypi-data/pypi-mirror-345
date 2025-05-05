
# **Endura SDK**

The **Endura SDK** provides a trust layer for edge AI models, allowing you to securely log telemetry, capture model metadata, and validate data at the edge.

---

## **Installation**

### **1. Install via Docker (Recommended for Edge Devices)**

For devices with Docker support, you can run the SDK inside a Docker container. This is useful for systems that may not support Python natively.

1. **Build the Docker image**:
   ```bash
   docker build -t endura-sdk .
   ```

2. **Run the Docker container** (this will install the package and run the main script):
   ```bash
   docker run --rm endura-sdk
   ```

### **2. Install Locally (for Development or Python Users)**

If you’re running this on a device with Python installed, you can install the package directly.

1. **Clone or download the repository**:
   ```bash
   git clone https://github.com/yourusername/endura-sdk.git
   cd endura-sdk
   ```

2. **Install dependencies** (make sure to use a virtual environment):
   ```bash
   pip install -r requirements.txt
   ```

3. **Install the SDK locally**:
   ```bash
   pip install .
   ```

4. **Editable installation** (optional, if you're developing and want changes to reflect immediately):
   ```bash
   pip install -e .
   ```

---

## **Usage**

### **Using the SDK in Python**:

Once the SDK is installed, you can import and use it in your Python code:

```python
from endura import EnduraAgent

# Initialize with your model path
agent = EnduraAgent("path_to_model.pth")

# Log an inference event
agent.log_inference(input_data, output_data)
```

### **Using the SDK in Docker**:

To run the SDK via Docker, you can directly interact with the containerized version:

```bash
docker run --rm endura-sdk
```

This command runs the SDK inside the Docker container, using the `main.py` file inside the container as the entry point.

---

## **Development**

If you want to contribute or develop the SDK further:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/endura-sdk.git
   cd endura-sdk
   ```

2. **Install dependencies** in a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scriptsctivate`
   pip install -r requirements.txt
   ```

3. **Run tests** (using `pytest`):
   ```bash
   pytest
   ```

---

## License

This project is licensed under a custom license. See the LICENSE file for more details.
