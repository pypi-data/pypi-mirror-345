import time
import uuid

def generate_id():
    return f"chatcmpl-{uuid.uuid4().hex}"

def format_non_streaming_response(
    generated_text,
    model="custom-model",
    id=None,
    created=None,
    usage=None,
    finish_reason="stop",
):
    if id is None:
        id = generate_id()
    if created is None:
        created = int(time.time())
    
    response = {
        "id": id,
        "object": "chat.completion",
        "created": created,
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": generated_text,
                },
                "finish_reason": finish_reason,
                "logprobs": None,
            }
        ],
    }
    
    if usage is not None:
        response["usage"] = usage
    
    return response

def format_streaming_response(
    generated_chunks,
    model="custom-model",
    id=None,
    created=None,
    finish_reason="stop",
):
    if id is None:
        id = generate_id()
    if created is None:
        created = int(time.time())
    
    for chunk in generated_chunks:
        yield {
            "id": id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "delta": {
                        "content": chunk,
                    },
                    "finish_reason": None,
                    "logprobs": None,
                }
            ],
        }
    
    # Final chunk indicating completion
    yield {
        "id": id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": model,
        "choices": [
            {
                "index": 0,
                "delta": {},
                "finish_reason": finish_reason,
                "logprobs": None,
            }
        ],
    }
