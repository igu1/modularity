"""Data validation utilities."""

import re
from typing import Any, Dict, List, Tuple, Optional, Union
from ..logging.logger import CoreLogger

logger = CoreLogger()


class ValidationHelpers:
    """Data validation utility functions."""
    
    # Email validation pattern
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    # Phone number patterns (basic)
    PHONE_PATTERN = re.compile(r'^\+?[\d\s\-\(\)]{10,}$')
    
    # URL pattern
    URL_PATTERN = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email address format.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if email is valid
        """
        if not email or not isinstance(email, str):
            return False
        
        return bool(ValidationHelpers.EMAIL_PATTERN.match(email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        Validate phone number format.
        
        Args:
            phone: Phone number to validate
            
        Returns:
            True if phone number is valid
        """
        if not phone or not isinstance(phone, str):
            return False
        
        return bool(ValidationHelpers.PHONE_PATTERN.match(phone))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Validate URL format.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is valid
        """
        if not url or not isinstance(url, str):
            return False
        
        return bool(ValidationHelpers.URL_PATTERN.match(url))
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate that required fields are present and not empty.
        
        Args:
            data: Dictionary to validate
            required_fields: List of required field names
            
        Returns:
            Tuple of (is_valid, missing_fields)
        """
        if not isinstance(data, dict):
            return False, required_fields
        
        missing = []
        for field in required_fields:
            if field not in data or data[field] is None or str(data[field]).strip() == '':
                missing.append(field)
        
        return len(missing) == 0, missing
    
    @staticmethod
    def validate_field_types(data: Dict[str, Any], field_types: Dict[str, type]) -> Tuple[bool, List[str]]:
        """
        Validate field types.
        
        Args:
            data: Dictionary to validate
            field_types: Dictionary mapping field names to expected types
            
        Returns:
            Tuple of (is_valid, invalid_fields)
        """
        if not isinstance(data, dict):
            return False, list(field_types.keys())
        
        invalid = []
        for field, expected_type in field_types.items():
            if field in data and data[field] is not None:
                if not isinstance(data[field], expected_type):
                    # Allow string to number conversion
                    if expected_type in (int, float) and isinstance(data[field], str):
                        try:
                            expected_type(data[field])
                            continue
                        except ValueError:
                            pass
                    invalid.append(field)
        
        return len(invalid) == 0, invalid
    
    @staticmethod
    def validate_field_lengths(data: Dict[str, Any], field_lengths: Dict[str, int]) -> Tuple[bool, List[str]]:
        """
        Validate field maximum lengths.
        
        Args:
            data: Dictionary to validate
            field_lengths: Dictionary mapping field names to maximum lengths
            
        Returns:
            Tuple of (is_valid, invalid_fields)
        """
        if not isinstance(data, dict):
            return False, list(field_lengths.keys())
        
        invalid = []
        for field, max_length in field_lengths.items():
            if field in data and data[field] is not None:
                value = str(data[field])
                if len(value) > max_length:
                    invalid.append(field)
        
        return len(invalid) == 0, invalid
    
    @staticmethod
    def validate_numeric_range(data: Dict[str, Any], ranges: Dict[str, Tuple[Union[int, float], Union[int, float]]]) -> Tuple[bool, List[str]]:
        """
        Validate numeric field ranges.
        
        Args:
            data: Dictionary to validate
            ranges: Dictionary mapping field names to (min, max) tuples
            
        Returns:
            Tuple of (is_valid, invalid_fields)
        """
        if not isinstance(data, dict):
            return False, list(ranges.keys())
        
        invalid = []
        for field, (min_val, max_val) in ranges.items():
            if field in data and data[field] is not None:
                try:
                    value = float(data[field])
                    if not (min_val <= value <= max_val):
                        invalid.append(field)
                except (ValueError, TypeError):
                    invalid.append(field)
        
        return len(invalid) == 0, invalid
    
    @staticmethod
    def validate_regex_patterns(data: Dict[str, Any], patterns: Dict[str, str]) -> Tuple[bool, List[str]]:
        """
        Validate fields against regex patterns.
        
        Args:
            data: Dictionary to validate
            patterns: Dictionary mapping field names to regex patterns
            
        Returns:
            Tuple of (is_valid, invalid_fields)
        """
        if not isinstance(data, dict):
            return False, list(patterns.keys())
        
        invalid = []
        for field, pattern in patterns.items():
            if field in data and data[field] is not None:
                try:
                    regex = re.compile(pattern)
                    if not regex.match(str(data[field])):
                        invalid.append(field)
                except re.error:
                    invalid.append(field)
        
        return len(invalid) == 0, invalid
    
    @staticmethod
    def sanitize_string(text: str, max_length: Optional[int] = None, 
                       remove_html: bool = True, 
                       remove_special_chars: bool = False) -> str:
        """
        Sanitize string input.
        
        Args:
            text: String to sanitize
            max_length: Maximum length to allow
            remove_html: Whether to remove HTML tags
            remove_special_chars: Whether to remove special characters
            
        Returns:
            Sanitized string
        """
        if not isinstance(text, str):
            text = str(text)
        
        # Remove HTML tags if requested
        if remove_html:
            text = re.sub(r'<[^>]+>', '', text)
        
        # Remove special characters if requested
        if remove_special_chars:
            text = re.sub(r'[<>"\'&]', '', text)
        
        # Remove potentially dangerous characters
        dangerous_chars = ['\x00', '\x01', '\x02', '\x03', '\x04', '\x05']
        for char in dangerous_chars:
            text = text.replace(char, '')
        
        # Trim whitespace
        text = text.strip()
        
        # Apply max length if specified
        if max_length and len(text) > max_length:
            text = text[:max_length]
        
        return text
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename for safe storage.
        
        Args:
            filename: Filename to sanitize
            
        Returns:
            Sanitized filename
        """
        if not isinstance(filename, str):
            filename = str(filename)
        
        # Remove path traversal attempts
        filename = filename.replace('..', '').replace('/', '').replace('\\', '')
        
        # Remove dangerous characters
        dangerous_chars = [':', '*', '?', '"', '<', '>', '|']
        for char in dangerous_chars:
            filename = filename.replace(char, '')
        
        # Remove control characters
        filename = re.sub(r'[\x00-\x1f\x7f]', '', filename)
        
        # Ensure it's not empty
        if not filename.strip():
            filename = 'unnamed_file'
        
        return filename.strip()
    
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_strong, weakness_messages)
        """
        weaknesses = []
        
        if len(password) < 8:
            weaknesses.append("Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', password):
            weaknesses.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            weaknesses.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            weaknesses.append("Password must contain at least one digit")
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?]', password):
            weaknesses.append("Password must contain at least one special character")
        
        if re.search(r'(.)\1{2,}', password):
            weaknesses.append("Password should not contain repeated characters")
        
        return len(weaknesses) == 0, weaknesses
    
    @staticmethod
    def validate_json_structure(data: Any, schema: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate JSON data against a schema.
        
        Args:
            data: Data to validate
            schema: Schema definition (simplified JSON schema)
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        if not isinstance(data, dict):
            errors.append("Data must be a JSON object")
            return False, errors
        
        # Check required fields
        required_fields = schema.get('required', [])
        is_valid, missing = ValidationHelpers.validate_required_fields(data, required_fields)
        if not is_valid:
            errors.extend([f"Missing required field: {field}" for field in missing])
        
        # Check field types
        properties = schema.get('properties', {})
        field_types = {}
        for field, field_schema in properties.items():
            if 'type' in field_schema and field in data:
                type_map = {
                    'string': str,
                    'integer': int,
                    'number': (int, float),
                    'boolean': bool,
                    'array': list,
                    'object': dict
                }
                expected_type = type_map.get(field_schema['type'])
                if expected_type:
                    field_types[field] = expected_type
        
        if field_types:
            is_valid, invalid = ValidationHelpers.validate_field_types(data, field_types)
            if not is_valid:
                errors.extend([f"Invalid type for field: {field}" for field in invalid])
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_uuid(uuid_string: str) -> bool:
        """
        Validate UUID format.
        
        Args:
            uuid_string: UUID string to validate
            
        Returns:
            True if UUID is valid
        """
        import uuid
        
        try:
            uuid.UUID(uuid_string)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_ip_address(ip_string: str) -> bool:
        """
        Validate IP address format (IPv4 and IPv6).
        
        Args:
            ip_string: IP address string to validate
            
        Returns:
            True if IP address is valid
        """
        import ipaddress
        
        try:
            ipaddress.ip_address(ip_string)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_credit_card(card_number: str) -> bool:
        """
        Validate credit card number using Luhn algorithm.
        
        Args:
            card_number: Credit card number to validate
            
        Returns:
            True if credit card number is valid
        """
        # Remove spaces and dashes
        card_number = card_number.replace(' ', '').replace('-', '')
        
        # Check if it's all digits and has reasonable length
        if not card_number.isdigit() or len(card_number) < 13 or len(card_number) > 19:
            return False
        
        # Luhn algorithm
        total = 0
        reverse_digits = card_number[::-1]
        
        for i, digit in enumerate(reverse_digits):
            n = int(digit)
            if i % 2 == 1:  # Every second digit (starting from right, excluding check digit)
                n *= 2
                if n > 9:
                    n -= 9
            total += n
        
        return total % 10 == 0


class ValidationRule:
    """Base class for validation rules."""
    
    def __init__(self, field_name: str, message: str = None):
        """
        Initialize validation rule.
        
        Args:
            field_name: Name of the field to validate
            message: Custom error message
        """
        self.field_name = field_name
        self.message = message or f"Validation failed for field {field_name}"
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validate the rule against data.
        
        Args:
            data: Data to validate
            
        Returns:
            True if validation passes
        """
        raise NotImplementedError
    
    def get_error_message(self) -> str:
        """Get the error message for this rule."""
        return self.message


class RequiredRule(ValidationRule):
    """Rule to require a field."""
    
    def validate(self, data: Dict[str, Any]) -> bool:
        return (self.field_name in data and 
                data[self.field_name] is not None and 
                str(data[self.field_name]).strip() != '')


class LengthRule(ValidationRule):
    """Rule to validate field length."""
    
    def __init__(self, field_name: str, min_length: int = None, max_length: int = None, message: str = None):
        super().__init__(field_name, message)
        self.min_length = min_length
        self.max_length = max_length
        
        if not message:
            if min_length and max_length:
                self.message = f"Field {field_name} must be between {min_length} and {max_length} characters"
            elif min_length:
                self.message = f"Field {field_name} must be at least {min_length} characters"
            elif max_length:
                self.message = f"Field {field_name} must be at most {max_length} characters"
    
    def validate(self, data: Dict[str, Any]) -> bool:
        if self.field_name not in data or data[self.field_name] is None:
            return True
        
        length = len(str(data[self.field_name]))
        
        if self.min_length and length < self.min_length:
            return False
        
        if self.max_length and length > self.max_length:
            return False
        
        return True


class EmailRule(ValidationRule):
    """Rule to validate email format."""
    
    def validate(self, data: Dict[str, Any]) -> bool:
        if self.field_name not in data or data[self.field_name] is None:
            return True
        
        return ValidationHelpers.validate_email(str(data[self.field_name]))


class Validator:
    """Main validator class that manages multiple validation rules."""
    
    def __init__(self):
        """Initialize the validator."""
        self.rules: Dict[str, List[ValidationRule]] = {}
    
    def add_rule(self, rule: ValidationRule):
        """
        Add a validation rule.
        
        Args:
            rule: Validation rule to add
        """
        if rule.field_name not in self.rules:
            self.rules[rule.field_name] = []
        self.rules[rule.field_name].append(rule)
    
    def validate(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Validate data against all rules.
        
        Args:
            data: Data to validate
            
        Returns:
            Tuple of (is_valid, errors_by_field)
        """
        errors = {}
        is_valid = True
        
        for field_name, field_rules in self.rules.items():
            field_errors = []
            for rule in field_rules:
                if not rule.validate(data):
                    field_errors.append(rule.get_error_message())
                    is_valid = False
            
            if field_errors:
                errors[field_name] = field_errors
        
        return is_valid, errors
