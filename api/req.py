import requests
while True:
    text = input("\nenter your message: ")

    response = requests.post(
        "http://localhost:8000/get_tags",
        params={"text": text}  # Send as query parameter
    )
    print(response.json())