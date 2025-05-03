import tornado.web

from http import HTTPStatus
from typing import Dict, List, Union, Optional, Text
from enum import Enum
from pydantic import BaseModel, validate_call
from abc import abstractmethod

from aixplain.model_interfaces.schemas.function.function_input import (
    SegmentationInput,
    TranslationInput,
    SpeechRecognitionInput,
    DiacritizationInput,
    ClassificationInput,
    SpeechEnhancementInput,
    SpeechSynthesisInput,
    TextToImageGenerationInput,
    TextGenerationInput,
    TextSummarizationInput,
    SearchInput,
    TextReconstructionInput,
    FillTextMaskInput,
    SubtitleTranslationInput
)
from aixplain.model_interfaces.schemas.function.function_output import (
    SegmentationOutput,
    TranslationOutput,
    SpeechRecognitionOutput,
    DiacritizationOutput,
    ClassificationOutput,
    SpeechEnhancementOutput,
    SpeechSynthesisOutput,
    TextToImageGenerationOutput,
    TextGenerationOutput,
    TextSummarizationOutput,
    SearchOutput,
    TextReconstructionOutput,
    FillTextMaskOutput,
    SubtitleTranslationOutput
)
from aixplain.model_interfaces.schemas.modality.modality_input import TextInput, TextListInput
from aixplain.model_interfaces.schemas.modality.modality_output import TextListOutput
from aixplain.model_interfaces.interfaces.aixplain_model import AixplainModel

class TranslationPredictInput(BaseModel):
    instances: List[TranslationInput]

class TranslationModel(AixplainModel):

    @abstractmethod
    @validate_call
    def run_model(self, api_input: List[TranslationInput], headers: Dict[str, str] = None) -> List[TranslationOutput]:
        raise NotImplementedError

    @validate_call
    def predict(self, request: TranslationPredictInput, headers: Dict[str, str] = None) -> Dict:
        predict_output = {
                "predictions": self.run_model(request.instances, headers)
        }
        return predict_output

class SpeechRecognitionPredictInput(BaseModel):
    instances: List[SpeechRecognitionInput]

class SpeechRecognitionModel(AixplainModel):

    @abstractmethod
    @validate_call
    def run_model(self, api_input: List[SpeechRecognitionInput], headers: Dict[str, str] = None) -> List[SpeechRecognitionOutput]:
        pass

    @validate_call
    def predict(self, request: SpeechRecognitionPredictInput, headers: Dict[str, str] = None) -> Dict:
        predict_output = {
                "predictions": self.run_model(request.instances, headers)
        }
        return predict_output

class DiacritizationPredictInput(BaseModel):
    instances: List[DiacritizationInput]

class DiacritizationModel(AixplainModel):

    @abstractmethod
    @validate_call
    def run_model(self, api_input: List[DiacritizationInput], headers: Dict[str, str] = None) -> List[DiacritizationOutput]:
        pass

    @validate_call
    def predict(self, request: DiacritizationPredictInput, headers: Dict[str, str] = None) -> Dict:
        predict_output = {
                "predictions": self.run_model(request.instances, headers)
        }
        return predict_output

class ClassificationPredictInput(BaseModel):
    instances: List[ClassificationInput]

class ClassificationModel(AixplainModel):

    @abstractmethod
    @validate_call
    def run_model(self, api_input: List[ClassificationInput], headers: Dict[str, str] = None) -> List[ClassificationOutput]:
        raise NotImplementedError

    @validate_call
    def predict(self, request: ClassificationPredictInput, headers: Dict[str, str] = None) -> Dict:
        predict_output = {
                "predictions": self.run_model(request.instances, headers)
        }
        return predict_output

class SpeechEnhancementPredictInput(BaseModel):
    instances: List[SpeechEnhancementInput]

class SpeechEnhancementModel(AixplainModel):

    @abstractmethod
    @validate_call
    def run_model(self, api_input: List[SpeechEnhancementInput], headers: Dict[str, str] = None) -> List[SpeechEnhancementOutput]:
        pass

    @validate_call
    def predict(self, request: SpeechEnhancementPredictInput, headers: Dict[str, str] = None) -> Dict:
        predict_output = {
            "predictions": self.run_model(request.instances, headers)
        }
        return predict_output


class SpeechSynthesisPredictInput(BaseModel):
    instances: List[SpeechSynthesisInput]

class SpeechSynthesis(AixplainModel):

    @abstractmethod
    @validate_call
    def run_model(self, api_input: List[SpeechSynthesisInput], headers: Dict[str, str] = None) -> List[SpeechSynthesisOutput]:
        pass

    @validate_call
    def predict(self, request: SpeechSynthesisPredictInput, headers: Dict[str, str] = None) -> Dict:
        predict_output = {
            "predictions": self.run_model(request.instances, headers)
        }
        return predict_output

class TextToImageGenerationPredictInput(BaseModel):
    instances: List[TextToImageGenerationInput]

class TextToImageGeneration(AixplainModel):

    @abstractmethod
    @validate_call
    def run_model(self, api_input: List[TextToImageGenerationInput], headers: Dict[str, str] = None) -> List[TextToImageGenerationOutput]:
        pass

    @validate_call
    def predict(self, request: TextToImageGenerationPredictInput, headers: Dict[str, str] = None) -> Dict:
        predict_output = {
            "predictions": self.run_model(request.instances, headers)
        }
        return predict_output

class TextGenerationChatTemplatizeInput(BaseModel):
    data: List[Dict]

class TextGenerationPredictInput(BaseModel):
    instances: Union[List[TextGenerationInput], List[TextListInput], List[TextGenerationChatTemplatizeInput]]
    function: Optional[Text] = "PREDICT"

class TextGenerationRunModelOutput(BaseModel):
    predictions: List[TextGenerationOutput]

class TextGenerationTokenizeOutput(BaseModel):
    token_counts: List[List[int]]

class TextGenerationModel(AixplainModel):

    @validate_call
    def predict(self, request: TextGenerationPredictInput, headers: Dict[str, str] = None) -> Dict:
        instances = request.instances
        if request.function.upper() == "PREDICT":
            predict_output = {
                "predictions": self.run_model(instances, headers)
            }
            return predict_output
        elif request.function.upper() == "TOKENIZE":
            token_counts_output = {
                "token_counts": self.tokenize(instances, headers)
            }
            return token_counts_output
        else:
            raise ValueError("Invalid function.")

    @abstractmethod
    @validate_call
    def run_model(self, api_input: List[TextGenerationInput], headers: Dict[str, str] = None) -> List[TextGenerationOutput]:
        raise NotImplementedError

    @abstractmethod
    @validate_call    
    def tokenize(self, api_input: List[TextListInput], headers: Dict[str, str] = None) -> List[List[int]]:
        raise NotImplementedError
    
class TextGenerationChatModel(TextGenerationModel):

    @abstractmethod
    @validate_call
    def run_model(self, api_input: List[TextInput], headers: Dict[str, str] = None) -> List[TextGenerationOutput]:
        raise NotImplementedError
    
    @validate_call
    def predict(self, request: TextGenerationPredictInput, headers: Dict[str, str] = None) -> Dict:
        instances = request.instances
        if request.function.upper() == "PREDICT":
            predict_output = {
                "predictions": self.run_model(instances, headers)
            }
            return predict_output
        elif request.function.upper() == "TOKENIZE":
            token_counts_output = {
                "token_counts": self.tokenize(instances, headers)
            }
            return token_counts_output
        elif request.function.upper() == "TEMPLATIZE":
            templatize_output = {
                "prompts": self.templatize(instances, headers)
            }
            return templatize_output
        else:
            raise ValueError("Invalid function.")

    @abstractmethod
    @validate_call
    def templatize(self, api_input: List[TextGenerationChatTemplatizeInput], headers: Dict[str, str] = None) -> List[Text]:
        raise NotImplementedError

    # NOTE: TOKENIZE is inherited from TextGenerationModel and must also be 
    # implemented. See method signature above.

class TextSummarizationPredictInput(BaseModel):
    instances: List[TextSummarizationInput]

class TextSummarizationModel(AixplainModel):

    @abstractmethod
    @validate_call
    def run_model(self, api_input: List[TextSummarizationInput], headers: Dict[str, str] = None) -> List[TextSummarizationOutput]:
        raise NotImplementedError

    @validate_call
    def predict(self, request: TextSummarizationPredictInput, headers: Dict[str, str] = None) -> Dict:
        predict_output = {
            "predictions": self.run_model(request.instances, headers)
        }
        return predict_output
    
class SearchModelPredictInput(BaseModel):
    instances: List[SearchInput]

class SearchModel(AixplainModel):

    @abstractmethod
    @validate_call
    def run_model(self, api_input: List[SearchInput], headers: Dict[str, str] = None) -> List[SearchOutput]:
        pass

    @validate_call
    def predict(self, request: SearchModelPredictInput, headers: Dict[str, str] = None) -> Dict:
        predict_output = {
            "predictions": self.run_model(request.instances, headers)
        }
        return predict_output
    
class TextReconstructionPredictInput(BaseModel):
    instances: List[TextReconstructionInput]

class TextReconstructionModel(AixplainModel):

    @abstractmethod
    @validate_call
    def run_model(self, api_input: List[TextReconstructionInput], headers: Dict[str, str] = None) -> List[TextReconstructionInput]:
        raise NotImplementedError

    @validate_call
    def predict(self, request: TextReconstructionPredictInput, headers: Dict[str, str] = None) -> Dict:
        predict_output = {
            "predictions": self.run_model(request.instances, headers)
        }
        return predict_output

class FillTextMaskPredictInput(BaseModel):
    instances: List[FillTextMaskInput]

class FillTextMaskModel(AixplainModel):

    @abstractmethod
    @validate_call
    def run_model(self, api_input: List[FillTextMaskInput], headers: Dict[str, str] = None) -> List[FillTextMaskOutput]:
        raise NotImplementedError

    @validate_call
    def predict(self, request: FillTextMaskPredictInput, headers: Dict[str, str] = None) -> Dict:
        predict_output = {
            "predictions": self.run_model(request.instances, headers)
        }
        return predict_output
    
class SubtitleTranslationPredictInput(BaseModel):
    instances: List[SubtitleTranslationInput]

class SubtitleTranslationModel(AixplainModel):

    @abstractmethod
    @validate_call
    def run_model(self, api_input: List[SubtitleTranslationInput], headers: Dict[str, str] = None) -> List[SubtitleTranslationOutput]:
        raise NotImplementedError

    @validate_call
    def predict(self, request: SubtitleTranslationPredictInput, headers: Dict[str, str] = None) -> Dict:
        predict_output = {
            "predictions": self.run_model(request.instances, headers)
        }
        return predict_output

class SegmentationPredictInput(BaseModel):
    instances: List[SegmentationInput]

class SegmentationModel(AixplainModel):

    @abstractmethod
    @validate_call
    def run_model(
        self,
        api_input: List[SegmentationInput],
        headers: Dict[str, str] = None
    ) -> List[SegmentationOutput]:
        raise NotImplementedError

    @validate_call
    def predict(self, request: SegmentationPredictInput,
                headers: Dict[str, str] = None) -> dict:
        predict_output = {
            "predictions": self.run_model(request.instances, headers)
        }
        return predict_output