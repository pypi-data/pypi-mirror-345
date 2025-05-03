from kserve import ModelServer

class AixplainModelServer(ModelServer):

    def __init__(self, *args, **kwargs):
        """
        aiXplain Model Server is a tornado based web-server that follows
        the KServe protocol v2 for model serving.
        """
        super().__init__(*args, **kwargs)