                                

import re
from typing import Any, Dict, List, Tuple, Optional, Union
from ..logging.logger import CoreLogger

logger = CoreLogger()


class ValidationHelpers:
                                            
    
                              
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
                                   
    PHONE_PATTERN = re.compile(r'^\+?[\d\s\-\(\)]{10,}$')
    
                 
    URL_PATTERN = re.compile(
        r'^https?://'                       
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'             
        r'localhost|'                
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'            
        r'(?::\d+)?'                 
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    @staticmethod
    def validate_email(email: str) -> bool:
\
\
\
\
\
\
\
\
           
        if not email or not isinstance(email, str):
            return False
        
        return bool(ValidationHelpers.EMAIL_PATTERN.match(email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
\
\
\
\
\
\
\
\
           
        if not phone or not isinstance(phone, str):
            return False
        
        return bool(ValidationHelpers.PHONE_PATTERN.match(phone))
    
    @staticmethod
    def validate_url(url: str) -> bool:
\
\
\
\
\
\
\
\
           
        if not url or not isinstance(url, str):
            return False
        
        return bool(ValidationHelpers.URL_PATTERN.match(url))
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, List[str]]:
\
\
\
\
\
\
\
\
\
           
        if not isinstance(data, dict):
            return False, required_fields
        
        missing = []
        for field in required_fields:
            if field not in data or data[field] is None or str(data[field]).strip() == '':
                missing.append(field)
        
        return len(missing) == 0, missing
    
    @staticmethod
    def validate_field_types(data: Dict[str, Any], field_types: Dict[str, type]) -> Tuple[bool, List[str]]:
\
\
\
\
\
\
\
\
\
           
        if not isinstance(data, dict):
            return False, list(field_types.keys())
        
        invalid = []
        for field, expected_type in field_types.items():
            if field in data and data[field] is not None:
                if not isinstance(data[field], expected_type):
                                                       
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
\
\
\
\
\
\
\
\
\
           
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
\
\
\
\
\
\
\
\
\
           
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
\
\
\
\
\
\
\
\
\
           
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
\
\
\
\
\
\
\
\
\
\
\
           
        if not isinstance(text, str):
            text = str(text)
        
                                       
        if remove_html:
            text = re.sub(r'<[^>]+>', '', text)
        
                                                
        if remove_special_chars:
            text = re.sub(r'[<>"\'&]', '', text)
        
                                                 
        dangerous_chars = ['\x00', '\x01', '\x02', '\x03', '\x04', '\x05']
        for char in dangerous_chars:
            text = text.replace(char, '')
        
                         
        text = text.strip()
        
                                       
        if max_length and len(text) > max_length:
            text = text[:max_length]
        
        return text
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
\
\
\
\
\
\
\
\
           
        if not isinstance(filename, str):
            filename = str(filename)
        
                                        
        filename = filename.replace('..', '').replace('/', '').replace('\\', '')
        
                                     
        dangerous_chars = [':', '*', '?', '"', '<', '>', '|']
        for char in dangerous_chars:
            filename = filename.replace(char, '')
        
                                   
        filename = re.sub(r'[\x00-\x1f\x7f]', '', filename)
        
                               
        if not filename.strip():
            filename = 'unnamed_file'
        
        return filename.strip()
    
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
\
\
\
\
\
\
\
\
           
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
\
\
\
\
\
\
\
\
\
           
        errors = []
        
        if not isinstance(data, dict):
            errors.append("Data must be a JSON object")
            return False, errors
        
                               
        required_fields = schema.get('required', [])
        is_valid, missing = ValidationHelpers.validate_required_fields(data, required_fields)
        if not is_valid:
            errors.extend([f"Missing required field: {field}" for field in missing])
        
                           
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
\
\
\
\
\
\
\
\
           
        import uuid
        
        try:
            uuid.UUID(uuid_string)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_ip_address(ip_string: str) -> bool:
\
\
\
\
\
\
\
\
           
        import ipaddress
        
        try:
            ipaddress.ip_address(ip_string)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_credit_card(card_number: str) -> bool:
\
\
\
\
\
\
\
\
           
                                  
        card_number = card_number.replace(' ', '').replace('-', '')
        
                                                            
        if not card_number.isdigit() or len(card_number) < 13 or len(card_number) > 19:
            return False
        
                        
        total = 0
        reverse_digits = card_number[::-1]
        
        for i, digit in enumerate(reverse_digits):
            n = int(digit)
            if i % 2 == 1:                                                                   
                n *= 2
                if n > 9:
                    n -= 9
            total += n
        
        return total % 10 == 0


class ValidationRule:
                                          
    
    def __init__(self, field_name: str, message: str = None):
\
\
\
\
\
\
           
        self.field_name = field_name
        self.message = message or f"Validation failed for field {field_name}"
    
    def validate(self, data: Dict[str, Any]) -> bool:
\
\
\
\
\
\
\
\
           
        raise NotImplementedError
    
    def get_error_message(self) -> str:
                                                  
        return self.message


class RequiredRule(ValidationRule):
                                  
    
    def validate(self, data: Dict[str, Any]) -> bool:
        return (self.field_name in data and 
                data[self.field_name] is not None and 
                str(data[self.field_name]).strip() != '')


class LengthRule(ValidationRule):
                                        
    
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
                                        
    
    def validate(self, data: Dict[str, Any]) -> bool:
        if self.field_name not in data or data[self.field_name] is None:
            return True
        
        return ValidationHelpers.validate_email(str(data[self.field_name]))


class Validator:
                                                                      
    
    def __init__(self):
                                       
        self.rules: Dict[str, List[ValidationRule]] = {}
    
    def add_rule(self, rule: ValidationRule):
\
\
\
\
\
           
        if rule.field_name not in self.rules:
            self.rules[rule.field_name] = []
        self.rules[rule.field_name].append(rule)
    
    def validate(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, List[str]]]:
\
\
\
\
\
\
\
\
           
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
