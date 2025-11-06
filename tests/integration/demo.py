from toolfront import Application

app = Application(
    "https://env-caf85393-b80e-4494-b96c-1fc7d1f844b0.fly.dev/README.md",
    param={"Authorization": "Bearer 8sVolWHIqvgMvSfQ4jsEIyUQmY6XKFVt"},
)

result = app.ask("Is the service up? what's the response? what files are available?", model="openai:gpt-4o-mini")

print(result)
# Answer: yes
