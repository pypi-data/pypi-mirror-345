class EnduraAgent:
    def __init__(self, model_path: str):
        self.model_meta = self.get_model_metadata(model_path)

    def get_model_metadata(self, filepath: str):
        return {
            "name": "pytorch.pt",
            "version": "1.0.0",
            "framework": "pytorch",
            "hash": "fake_hash"
        }