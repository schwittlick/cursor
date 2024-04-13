import openai

api_key = "".join(open("api_key.txt", "r").readlines())

# Initialize the client with your API key
client = openai.OpenAI(api_key=api_key)

client.images.create_variation()
response = openai.Image.create(
    model="text2img-1.0.0",
    prompt="an astronaut riding a horse",
    n=1,
    size="1024x1024"
)

print(response["data"][0]["url"])
