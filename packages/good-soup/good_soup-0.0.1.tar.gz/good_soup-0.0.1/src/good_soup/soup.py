"""Main module for Good Soup."""

from typing import List, Literal


class Soup:
    """A class for creating soup from multiple model weights."""

    def __init__(
        self,
        models: List[str],
        method: Literal["uniform", "greedy", "ties", "dare"] = "uniform",
        output_dir: str = "output",
        dtype: str = "float16",
        device: str = "cpu",
    ) -> None:
        """Initialize the Soup object."""
        # Validate the input
        if not models:
            raise ValueError("models must be a list of model paths")
        if method not in ["uniform", "greedy", "ties", "dare"]:
            raise ValueError("method must be one of: uniform, greedy, ties, dare")

        # Initialize the attributes
        self.models = models
        self.method = method
        self.output_dir = output_dir
        self.dtype = dtype
        self.device = device

    def merge(self) -> None:
        """Merge the models."""
        pass