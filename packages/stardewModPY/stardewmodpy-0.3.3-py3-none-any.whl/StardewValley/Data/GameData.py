from .model import modelsData

class Season(modelsData):
    def __init__(self):
        pass
    
    def getJson(self):
        return "Spring"

    class Spring(modelsData):
        def __init__(self):
            pass
            
        def getJson() -> str:
            return "Spring"
    
    class Summer(modelsData):
        def __init__(self):
            pass

        def getJson() -> str:
            return "Summer"
    
    class Fall(modelsData):
        def __init__(self):
            pass
    
        def getJson() -> str:
            return "Fall"
    
    class Winter(modelsData):
        def __init__(self):
            pass

        def getJson() -> str:
            return "Winter"
