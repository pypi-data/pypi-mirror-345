"""
Machine learning component for address prediction and extraction.
"""
import re
from typing import Dict, List, Optional, Any, Tuple

import spacy
from spacy.language import Language
from spacy.tokens import Doc, Span

class AddressComponentPredictor:
    """
    Machine learning based component for extracting and predicting address components.
    Uses spaCy for NLP-based extraction of address components.
    """
    
    def __init__(self, model: str = "en_core_web_sm", confidence_threshold: float = 0.7):
        """
        Initialize the component predictor with a spaCy model.
        
        Args:
            model: The spaCy model to use for NLP processing
            confidence_threshold: Minimum confidence score for component predictions
        """
        self.confidence_threshold = confidence_threshold
        try:
            self.nlp = spacy.load(model)
        except OSError:
            # If model isn't available, download it
            import subprocess
            subprocess.run([
                "python", "-m", "spacy", "download", model
            ], check=True)
            self.nlp = spacy.load(model)
        
        # Register custom components
        if not Language.has_factory("address_parser"):
            Language.factory("address_parser", func=self._create_address_parser)
            self.nlp.add_pipe("address_parser", last=True)
    
    def _create_address_parser(self, nlp: Language, name: str) -> Any:
        """
        Creates a custom address parser component for spaCy pipeline.
        
        Args:
            nlp: The spaCy Language object
            name: The component name
            
        Returns:
            A callable component that adds address entities to Doc objects
        """
        return AddressParser(nlp)
    
    def extract_components(self, address_text: str) -> Dict[str, str]:
        """
        Extract structured components from an address string.
        
        Args:
            address_text: The address text to process
            
        Returns:
            Dictionary of address components and their values
        """
        doc = self.nlp(address_text)
        components = {}
        
        # Extract entities from the document
        for ent in doc.ents:
            if ent.label_ in ['GPE', 'STREET', 'NUMBER', 'ORG', 'FAC', 'LOC'] and ent._.confidence > self.confidence_threshold:
                component_type = self._map_entity_to_component(ent)
                components[component_type] = ent.text
        
        # Extract additional components using patterns
        components.update(self._extract_patterns(address_text))
        
        return components
    
    def _map_entity_to_component(self, entity: Span) -> str:
        """
        Maps spaCy entity types to address component names.
        
        Args:
            entity: A spaCy entity span
            
        Returns:
            The corresponding address component name
        """
        entity_mapping = {
            'GPE': self._classify_gpe,
            'STREET': lambda ent: 'street_name',
            'NUMBER': self._classify_number,
            'ORG': lambda ent: 'organization',
            'FAC': lambda ent: 'building',
            'LOC': lambda ent: 'place',
        }
        
        if entity.label_ in entity_mapping:
            return entity_mapping[entity.label_](entity)
        return 'unknown'
    
    def _classify_gpe(self, entity: Span) -> str:
        """
        Classifies a GPE (Geo-Political Entity) as city, state, or country.
        
        Args:
            entity: A spaCy entity span
            
        Returns:
            The specific component type (city, state, country)
        """
        # Simple classification based on token count and position
        text = entity.text.lower()
        
        # Check country patterns
        if len(text.split()) <= 2 and entity.root.is_title:
            # Check country database
            if self._is_known_country(text):
                return 'country'
        
        # Check state patterns
        if len(text.split()) <= 3:
            if self._is_known_state(text):
                return 'state'
        
        # Default to city if nothing else matches
        return 'city'
    
    def _classify_number(self, entity: Span) -> str:
        """
        Classifies a number as street_number, unit, or postal_code.
        
        Args:
            entity: A spaCy entity span
            
        Returns:
            The specific component type for the number
        """
        text = entity.text
        
        # Check for postal code patterns
        postal_pattern = r'^\d{5}(-\d{4})?$'
        if re.match(postal_pattern, text):
            return 'postal_code'
        
        # Check for unit patterns
        unit_pattern = r'^#?\d+[a-zA-Z]?$'
        if re.match(unit_pattern, text) and self._is_preceded_by_unit_indicator(entity):
            return 'unit'
        
        # Default to street_number
        return 'street_number'
    
    def _is_preceded_by_unit_indicator(self, entity: Span) -> bool:
        """
        Check if a number entity is preceded by a unit indicator like 'apt', 'unit', etc.
        
        Args:
            entity: A spaCy entity span
            
        Returns:
            Boolean indicating if the entity is preceded by a unit indicator
        """
        if entity.start > 0:
            prev_token = entity.doc[entity.start - 1]
            unit_indicators = ['apt', 'apartment', 'unit', 'suite', 'ste', '#']
            return prev_token.text.lower().rstrip('.') in unit_indicators
        return False
    
    def _is_known_country(self, text: str) -> bool:
        """
        Check if text matches a known country name.
        
        Args:
            text: The text to check
            
        Returns:
            Boolean indicating if text is a known country
        """
        # This should be replaced with a proper country database
        common_countries = ['usa', 'united states', 'canada', 'mexico', 'uk', 'united kingdom']
        return text.lower() in common_countries
    
    def _is_known_state(self, text: str) -> bool:
        """
        Check if text matches a known state name.
        
        Args:
            text: The text to check
            
        Returns:
            Boolean indicating if text is a known state
        """
        # This should be replaced with a proper state database
        us_states = ['alabama', 'alaska', 'arizona', 'california', 'new york', 'texas']
        state_abbrs = ['al', 'ak', 'az', 'ca', 'ny', 'tx']
        return text.lower() in us_states or text.lower() in state_abbrs
    
    def _extract_patterns(self, text: str) -> Dict[str, str]:
        """
        Extract address components using regex patterns.
        
        Args:
            text: The address text
            
        Returns:
            Dictionary of components extracted using patterns
        """
        components = {}
        
        # Extract postal codes
        postal_match = re.search(r'\b\d{5}(?:-\d{4})?\b', text)
        if postal_match:
            components['postal_code'] = postal_match.group(0)
        
        # Extract unit numbers
        unit_match = re.search(r'\b(?:apt|apartment|unit|suite|ste|#)[.\s]*(\d+[a-zA-Z]?)\b', text, re.IGNORECASE)
        if unit_match:
            components['unit'] = unit_match.group(1)
        
        return components
    
    def predict_missing_components(self, components: Dict[str, str]) -> Dict[str, str]:
        """
        Predict missing components based on existing components.
        
        Args:
            components: Dictionary of existing address components
            
        Returns:
            Dictionary with additional predicted components
        """
        result = components.copy()
        
        # Implement prediction logic for missing components
        # This would ideally use a trained model, but we'll use heuristics for now
        
        # Example: If we have city and state but no country, predict country
        if 'city' in result and 'state' in result and 'country' not in result:
            state = result['state'].lower()
            if state in ['california', 'new york', 'texas'] or state in ['ca', 'ny', 'tx']:
                result['country'] = 'USA'
        
        return result
    
    def train(self, training_data: List[Tuple[str, Dict[str, str]]]) -> None:
        """
        Train the component predictor on labeled address data.
        
        Args:
            training_data: List of (address_text, components) pairs
        """
        # This is a placeholder for actual model training
        # In a real implementation, this would:
        # 1. Prepare training examples from the data
        # 2. Update the spaCy model with new entity examples
        # 3. Train custom classifiers for component prediction
        pass


class AddressParser:
    """
    Custom spaCy pipeline component for parsing addresses.
    """
    
    def __init__(self, nlp: Language):
        """
        Initialize the address parser component.
        
        Args:
            nlp: The spaCy Language object
        """
        # Register extension attributes
        if not Span.has_extension("confidence"):
            Span.set_extension("confidence", default=0.0)
        if not Span.has_extension("component_type"):
            Span.set_extension("component_type", default="")
    
    def __call__(self, doc: Doc) -> Doc:
        """
        Process a document to identify address components.
        
        Args:
            doc: The spaCy Doc object
            
        Returns:
            The processed Doc with enhanced address entities
        """
        # Add information to entities
        for ent in doc.ents:
            # Set confidence scores based on entity characteristics
            if ent.label_ in ['GPE', 'STREET', 'NUMBER', 'ORG', 'FAC', 'LOC']:
                confidence = self._calculate_confidence(ent)
                ent._.confidence = confidence
        
        # Look for additional address patterns not caught by standard NER
        self._find_address_patterns(doc)
        
        return doc
    
    def _calculate_confidence(self, entity: Span) -> float:
        """
        Calculate a confidence score for an entity.
        
        Args:
            entity: A spaCy entity span
            
        Returns:
            Confidence score between 0 and 1
        """
        # Basic confidence scoring based on entity characteristics
        base_score = 0.7  # Start with a reasonable base score
        
        # Adjust based on entity label
        label_scores = {
            'GPE': 0.2,      # Higher confidence for geo-political entities
            'STREET': 0.15,  # Good confidence for street names
            'NUMBER': 0.1,   # Slightly lower for numbers (could be ambiguous)
            'ORG': 0.0,      # Base score for organizations
            'FAC': 0.05,     # Slight boost for facilities
            'LOC': 0.1       # Boost for locations
        }
        
        score = base_score + label_scores.get(entity.label_, 0)
        
        # Penalize very short entities that might be spurious
        if len(entity.text) < 2:
            score -= 0.2
        
        # Cap between 0 and 1
        return max(0.0, min(1.0, score))
    
    def _find_address_patterns(self, doc: Doc) -> None:
        """
        Find address-specific patterns not caught by standard NER.
        
        Args:
            doc: The spaCy Doc object
        """
        # This would implement pattern matching for address components
        # For example, finding street suffixes, unit designators, etc.
        # For a full implementation, this would add new entities to doc.ents
        pass 