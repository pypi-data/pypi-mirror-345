# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Union, Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel
from .prediction_output import PredictionOutput

__all__ = ["Prediction", "URLs"]


class URLs(BaseModel):
    cancel: str
    """Cancel the prediction"""

    get: str
    """Retrieve the latest state of the prediction"""

    stream: Optional[str] = None
    """An event source to stream the output of the prediction"""


class Prediction(BaseModel):
    id: str

    created_at: datetime
    """The time that the prediction was created"""

    data_removed: bool
    """Whether the prediction output has been deleted"""

    error: Optional[str] = None
    """An error string if the model status is `"failed"`"""

    input: Dict[str, object]
    """The prediction input"""

    model: str
    """The name of the model that created the prediction"""

    output: PredictionOutput

    status: Literal["starting", "processing", "succeeded", "failed", "canceled"]

    urls: URLs
    """API endpoints for working with the prediction"""

    version: Union[str, Literal["hidden"]]
    """The ID of the model version that created the prediction"""

    completed_at: Optional[datetime] = None
    """The time that the model completed the prediction and all outputs were uploaded"""

    deployment: Optional[str] = None
    """The name of the deployment that created the prediction"""

    logs: Optional[str] = None
    """The log output from the model"""

    metrics: Optional[Dict[str, object]] = None
    """Additional metrics associated with the prediction"""

    started_at: Optional[datetime] = None
    """The time that the model began the prediction"""
