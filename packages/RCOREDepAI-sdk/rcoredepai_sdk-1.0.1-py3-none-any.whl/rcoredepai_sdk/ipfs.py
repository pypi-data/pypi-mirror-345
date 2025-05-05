from rcoredepai_sdk.storage import get_storage
storage = get_storage()
def pin_file(data, name="model.onnx"):
    return storage.pin_file(data, name)
def pin_json(obj):
    return storage.pin_json(obj)
