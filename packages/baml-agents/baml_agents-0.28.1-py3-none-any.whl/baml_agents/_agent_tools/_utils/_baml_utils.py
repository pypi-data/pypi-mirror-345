from typing import TypeVar

from baml_agents._utils._sole import sole

T = TypeVar("T")


def get_prompt(request):
    messages = request.body.json()["messages"]
    prompt_parts = []
    for message in messages:
        content = sole(message["content"])
        if content["type"] != "text":
            raise ValueError(
                f"Expected content type 'text', but got '{content['type']}'",
            )
        prompt_parts.append(f"[{message['role']}]\n{content['text']}")
    return "\n\n".join(prompt_parts)


def display_prompt(request):
    escaped_prompt = (
        get_prompt(request).replace("<", "‹").replace(">", "›")  # noqa: RUF001
    )
    print(escaped_prompt)  # noqa: T201
