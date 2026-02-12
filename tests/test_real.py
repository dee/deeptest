import requests


# Read text file as string
with open("example1.rs", "r", encoding="utf-8") as f:
    file_content = f.read()


base_url = "http://127.0.0.1:8000"
response = requests.post(f"{base_url}/tests",
	json={"language": "Rust",
          "framework": "internal",
          "source": file_content})

# Expect 200 + item data
print(f"Status: {response.status_code}, Body: {response.json()}")
