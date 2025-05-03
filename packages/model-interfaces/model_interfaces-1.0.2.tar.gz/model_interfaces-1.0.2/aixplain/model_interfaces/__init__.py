from aixplain.model_interfaces.schemas.function.function_input import (
    APIInput,
    AudioEncoding,
    AudioConfig,
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
    SubtitleTranslationInput,
    SegmentationInput
)

from aixplain.model_interfaces.schemas.function.function_output import(
    APIOutput,
    WordDetails,
    TextSegmentDetails,
    Label,
    TranslationOutput,
    SpeechRecognitionOutput,
    DiacritizationOutput,
    ClassificationOutput,
    SpeechEnhancementOutput,
    TextToImageGenerationOutput,
    TextGenerationOutput,
    TextSummarizationOutput,
    SearchOutput,
    TextReconstructionOutput,
    FillTextMaskOutput,
    SubtitleTranslationOutput,
    SegmentationOutput
)

from aixplain.model_interfaces.schemas.metric.metric_input import(
    MetricInput,
    MetricAggregate,
    TextGenerationSettings,
    AudioGenerationSettings,
    TextGenerationMetricInput,
    ReferencelessTextGenerationMetricInput,
    AudioGenerationMetricInput,
    ReferencelessAudioGenerationMetricInput,
    ClassificationMetricInput,
    NamedEntityRecognitionElement,
    NamedEntityRecognitionMetricInput
)

from aixplain.model_interfaces.schemas.metric.metric_output import(
    MetricOutput,
    TextGenerationMetricOutput,
    ReferencelessTextGenerationMetricOutput,
    AudioGenerationMetricOutput,
    ReferencelessAudioGenerationMetricOutput,
    ClassificationMetricOutput,
    NamedEntityRecognitionMetricOutput
)

from aixplain.model_interfaces.schemas.script.script_input import(
    ScriptInput
)

from aixplain.model_interfaces.schemas.script.script_output import(
    ScriptOutput
)

from aixplain.model_interfaces.interfaces.function_models import(
    TranslationModel,
    SpeechRecognitionModel,
    DiacritizationModel,
    ClassificationModel,
    SpeechEnhancementModel,
    SpeechSynthesis,
    TextToImageGeneration,
    TextGenerationModel,
    TextGenerationChatModel,
    TextSummarizationModel,
    SearchModel,
    TextReconstructionModel,
    FillTextMaskModel,
    SubtitleTranslationModel,
    SegmentationModel
)

from aixplain.model_interfaces.interfaces.metric_models import(
    TextGenerationMetric,
    ReferencelessTextGenerationMetric,
    ClassificationMetric,
    AudioGenerationMetric,
    ReferencelessAudioGenerationMetric,
    NamedEntityRecognitionMetric
)

from aixplain.model_interfaces.interfaces.project_node import(
    ProjectNode
)

function_classes = [
    TranslationModel,
    SpeechRecognitionModel,
    DiacritizationModel,
    ClassificationModel,
    SpeechEnhancementModel,
    SpeechSynthesis,
    TextToImageGeneration,
    TextGenerationModel,
    TextGenerationChatModel,
    TextSummarizationModel,
    SearchModel,
    TextReconstructionModel,
    FillTextMaskModel,
    SubtitleTranslationModel,
    SegmentationModel
]

function_classes_input = [
    APIInput,
    AudioEncoding,
    AudioConfig,
    TranslationInput,
    SpeechRecognitionInput,
    DiacritizationInput,
    ClassificationInput,
    SpeechEnhancementInput,
    SpeechSynthesisInput,
    TextToImageGenerationInput,
    TextGenerationInput,
    SegmentationInput
]

metric_classes_input = [
    MetricInput,
    MetricAggregate,
    TextGenerationSettings,
    AudioGenerationSettings,
    TextGenerationMetricInput,
    ReferencelessTextGenerationMetricInput,
    AudioGenerationMetricInput,
    ReferencelessAudioGenerationMetricInput,
    ClassificationMetricInput,
    NamedEntityRecognitionElement,
    NamedEntityRecognitionMetricInput
]

metric_classes = [
    TextGenerationMetric,
    ReferencelessTextGenerationMetric,
    ClassificationMetric,
    AudioGenerationMetric,
    ReferencelessAudioGenerationMetric,
    NamedEntityRecognitionMetric
]

script_classes_input = [
    ScriptInput
]

script_classes = [
    ProjectNode
]

function_input_interface_map = {clazz.__name__.replace("Input", ""): clazz for clazz in function_classes_input}
metric_input_interface_map = {clazz.__name__.replace("Input", ""): clazz for clazz in metric_classes_input}
script_input_interface_map = {clazz.__name__.replace("Input", ""): clazz for clazz in script_classes_input}
function_interface_map = {clazz.__name__: clazz for clazz in function_classes}
metric_interface_map = {clazz.__name__: clazz for clazz in metric_classes}
script_interface_map = {clazz.__name__: clazz for clazz in script_classes}