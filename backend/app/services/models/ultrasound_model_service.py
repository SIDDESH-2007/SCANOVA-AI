class DummyModelService:
    def __init__(self, name):
        self.name = name

    def load_model(self):
        pass

    def analyze(self, image_path: str):
        return {"error": f"{self.name} AI model is not available. Please contact the administrator."}

ultrasound_model = DummyModelService("Ultrasound")

