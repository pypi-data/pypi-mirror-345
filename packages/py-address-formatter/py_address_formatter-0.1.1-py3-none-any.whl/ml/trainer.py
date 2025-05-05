"""
Utilities for training machine learning models for address parsing.
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union

import spacy
from spacy.tokens import DocBin
from spacy.training import Example

from pyaddress.ml.predictor import AddressComponentPredictor


class AddressModelTrainer:
    """
    Trainer for address parsing models.
    Handles dataset preparation, training, and model evaluation.
    """
    
    def __init__(self, model_dir: str = "models", base_model: str = "en_core_web_sm"):
        """
        Initialize the model trainer.
        
        Args:
            model_dir: Directory to save trained models
            base_model: Base spaCy model to start from
        """
        self.model_dir = Path(model_dir)
        self.base_model = base_model
        self.model_dir.mkdir(exist_ok=True, parents=True)
    
    def prepare_training_data(self, 
                             addresses: List[Dict[str, str]], 
                             output_path: Optional[str] = None) -> Path:
        """
        Convert address dictionaries to spaCy training data.
        
        Args:
            addresses: List of address dictionaries with components and original text
            output_path: Optional path to save the training data
            
        Returns:
            Path object pointing to the saved training data
        """
        if output_path is None:
            output_path = self.model_dir / "training_data.spacy"
        else:
            output_path = Path(output_path)
        
        # Load the model for tokenization
        nlp = spacy.load(self.base_model)
        
        # Create a DocBin to store the training data
        doc_bin = DocBin()
        
        for address in addresses:
            if "text" not in address:
                continue
                
            text = address["text"]
            doc = nlp.make_doc(text)
            
            # Map components to entity spans
            ents = self._create_entity_spans(doc, address)
            
            # Set entities in the document
            doc.ents = ents
            
            # Add to DocBin
            doc_bin.add(doc)
        
        # Save to disk
        doc_bin.to_disk(output_path)
        return output_path
    
    def _create_entity_spans(self, doc, address: Dict[str, str]) -> List[Any]:
        """
        Create entity spans for a document based on address components.
        
        Args:
            doc: spaCy Doc object
            address: Address dictionary with components
            
        Returns:
            List of entity spans
        """
        from spacy.tokens import Span
        
        ents = []
        text = doc.text
        
        # Component to entity type mapping
        component_mapping = {
            "street_number": "NUMBER",
            "street_name": "STREET",
            "city": "GPE",
            "state": "GPE",
            "postal_code": "NUMBER",
            "unit": "NUMBER",
            "country": "GPE"
        }
        
        # Create spans for each component
        for component, value in address.items():
            if component == "text" or not value:
                continue
                
            # Find all occurrences in the text
            start_idx = 0
            while start_idx < len(text):
                start_pos = text.find(value, start_idx)
                if start_pos == -1:
                    break
                
                end_pos = start_pos + len(value)
                
                # Find token span
                start_token = None
                end_token = None
                
                for i, token in enumerate(doc):
                    token_start = token.idx
                    token_end = token.idx + len(token.text)
                    
                    if token_start <= start_pos < token_end and start_token is None:
                        start_token = i
                    
                    if token_start <= end_pos <= token_end and end_token is None:
                        end_token = i + 1
                        break
                
                if start_token is not None and end_token is not None:
                    # Create entity span
                    entity_type = component_mapping.get(component, "MISC")
                    ent = Span(doc, start_token, end_token, label=entity_type)
                    ents.append(ent)
                
                start_idx = end_pos
        
        return ents
    
    def train_model(self, 
                   training_data_path: Union[str, Path], 
                   output_dir: Optional[str] = None, 
                   n_iter: int = 30) -> Path:
        """
        Train a spaCy model for address parsing.
        
        Args:
            training_data_path: Path to the training data
            output_dir: Directory to save the trained model
            n_iter: Number of training iterations
            
        Returns:
            Path to the trained model directory
        """
        if output_dir is None:
            output_dir = self.model_dir / "address_model"
        else:
            output_dir = Path(output_dir)
        
        # Create output directory
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Create training config
        config = {
            "paths": {
                "train": str(training_data_path),
                "dev": str(training_data_path)  # Using same data for validation (in practice, should be separate)
            },
            "system": {
                "gpu_allocator": None
            },
            "nlp": {
                "lang": "en",
                "pipeline": ["ner"],
                "batch_size": 128
            },
            "components": {
                "ner": {
                    "factory": "ner",
                    "moves": None,
                    "update_with_oracle_cut_size": 100
                }
            },
            "training": {
                "dev_corpus": "corpora.dev",
                "train_corpus": "corpora.train",
                "seed": 1,
                "gpu_allocator": None,
                "dropout": 0.1,
                "accumulate_gradient": 1,
                "patience": 1600,
                "max_steps": 20000,
                "eval_frequency": 200,
                "frozen_components": [],
                "annotating_components": [],
                "before_to_disk": None
            },
            "corpora": {
                "dev": {
                    "path": str(training_data_path),
                    "max_length": 0,
                    "limit": 0
                },
                "train": {
                    "path": str(training_data_path),
                    "max_length": 0,
                    "limit": 0
                }
            }
        }
        
        # Save config
        config_path = output_dir / "config.json"
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        
        # Run training
        import subprocess
        
        # Initialize model with base model
        subprocess.run([
            "python", "-m", "spacy", "init", "fill-config", 
            str(config_path), str(output_dir / "config.cfg"),
            "--base-model", self.base_model
        ], check=True)
        
        # Train model
        subprocess.run([
            "python", "-m", "spacy", "train",
            str(output_dir / "config.cfg"),
            "--output", str(output_dir),
            "--paths.train", str(training_data_path),
            "--paths.dev", str(training_data_path),
            "--n-iter", str(n_iter)
        ], check=True)
        
        return output_dir
    
    def evaluate_model(self, model_path: Union[str, Path], test_data: List[Dict[str, str]]) -> Dict[str, float]:
        """
        Evaluate the trained model on test data.
        
        Args:
            model_path: Path to the trained model
            test_data: List of address dictionaries for testing
            
        Returns:
            Dictionary with evaluation metrics
        """
        model_path = Path(model_path)
        
        # Load the trained model
        nlp = spacy.load(model_path)
        predictor = AddressComponentPredictor(model=str(model_path))
        
        # Evaluate on test data
        correct = 0
        total = 0
        component_metrics = {}
        
        for address in test_data:
            if "text" not in address:
                continue
                
            # Ground truth components
            true_components = {k: v for k, v in address.items() if k != "text"}
            
            # Predicted components
            text = address["text"]
            pred_components = predictor.extract_components(text)
            
            # Count correct predictions
            for component, true_value in true_components.items():
                if component not in component_metrics:
                    component_metrics[component] = {"correct": 0, "total": 0}
                
                component_metrics[component]["total"] += 1
                total += 1
                
                if component in pred_components and pred_components[component] == true_value:
                    component_metrics[component]["correct"] += 1
                    correct += 1
        
        # Calculate overall accuracy
        accuracy = correct / total if total > 0 else 0
        
        # Calculate component-wise accuracy
        results = {"overall_accuracy": accuracy}
        
        for component, metrics in component_metrics.items():
            comp_accuracy = metrics["correct"] / metrics["total"] if metrics["total"] > 0 else 0
            results[f"{component}_accuracy"] = comp_accuracy
        
        return results
    
    def load_training_data_from_json(self, json_path: Union[str, Path]) -> List[Dict[str, str]]:
        """
        Load training data from a JSON file.
        
        Args:
            json_path: Path to the JSON file
            
        Returns:
            List of address dictionaries
        """
        json_path = Path(json_path)
        
        with open(json_path, "r") as f:
            data = json.load(f)
        
        # Ensure the data has the expected format
        if isinstance(data, list):
            return data
        else:
            # Try to extract addresses from a different format
            if "addresses" in data:
                return data["addresses"]
            else:
                raise ValueError("Invalid JSON format for training data")
    
    def save_model_metadata(self, model_path: Union[str, Path], metadata: Dict[str, Any]) -> None:
        """
        Save metadata for a trained model.
        
        Args:
            model_path: Path to the model directory
            metadata: Dictionary with model metadata
        """
        model_path = Path(model_path)
        
        # Save metadata
        metadata_path = model_path / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)


def create_training_data_from_addresses(addresses: List[str], components: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Create training data from raw addresses and their parsed components.
    
    Args:
        addresses: List of address strings
        components: List of component dictionaries for each address
        
    Returns:
        List of training data entries
    """
    training_data = []
    
    for i, address in enumerate(addresses):
        if i >= len(components):
            break
        
        entry = components[i].copy()
        entry["text"] = address
        training_data.append(entry)
    
    return training_data 