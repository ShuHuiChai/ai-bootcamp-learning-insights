# airbase-streamlit-app

## Local Development

### Setup
```bash
# Create venv (only on initial setup)
python3 -m venv venv

# Activate venv
source venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt

# Start local app
streamlit run main.py
```

## Deployment

### App Password

Specify the following environment variable if you wish to password protect the entire application.

```bash
PASSWORD=
```

Note that if the environment variable is empty, the check is not enforced.

In your python3 file, include the following to enforce password checks:

```python3
if not check_password():
    st.stop()
```
