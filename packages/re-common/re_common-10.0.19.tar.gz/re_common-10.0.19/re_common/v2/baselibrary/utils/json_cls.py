import base64
import json


class BytesEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return base64.b64encode(obj).decode('utf-8')
        return super().default(obj)

# json.dumps(x, ensure_ascii=False, cls=BytesEncoder)