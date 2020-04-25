from typing import Dict, Any, Optional


class ConnectionMock:
    def __init__(self, data: Dict[str, Any], error: Optional[Exception] = None):
        self.cursor = self.CursorMock(data, error)

    class CursorMock:
        def __init__(self, data: Dict[str, Any], error: Optional[Exception] = None):
            self.data = data
            self.error = error

        def execute(self):
            if self.error:
                raise self.error
            else:
                return self.data

        def close(self):
            pass
