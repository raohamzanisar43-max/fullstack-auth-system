"""
Validation Utilities
Common validation functions for data validation and sanitization
"""

import re
import logging
from typing import Any, Optional, List, Dict, Union
from dataclasses import dataclass
from enum import Enum
import phonenumbers
from datetime import datetime, date
from email_validator import validate_email, EmailNotValidError

from app.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class ValidationType(Enum):
    """Supported validation types"""
    TEXT = "text"
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"
    NUMBER = "number"
    INTEGER = "integer"
    FLOAT = "float"
    DATE = "date"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    UUID = "uuid"
    ZIP_CODE = "zip_code"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"


@dataclass
class ValidationRule:
    """Validation rule definition"""
    name: str
    type: ValidationType
    required: bool = True
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None
    allowed_values: Optional[List[Any]] = None
    custom_validator: Optional[callable] = None
    error_message: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of validation operation"""
    is_valid: bool
    value: Any
    errors: List[str]
    warnings: List[str]


class Validator:
    """
    Comprehensive validation utilities
    """
    
    def __init__(self):
        self.us_states = [
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
            'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
            'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
            'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
            'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
        ]
        
        # Common regex patterns
        self.patterns = {
            'name': r'^[a-zA-Z\s\-\'\.]+$',
            'address': r'^[a-zA-Z0-9\s\-\.\,\#]+$',
            'city': r'^[a-zA-Z\s\-\'\.]+$',
            'zip_code': r'^\d{5}(-\d{4})?$',
            'ssn': r'^\d{3}-\d{2}-\d{4}$',
            'uuid': r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
            'credit_card': r'^\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}$',
            'url': r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
        }
    
    def validate(self, value: Any, rule: ValidationRule) -> ValidationResult:
        """
        Validate a value against a validation rule
        
        Args:
            value: Value to validate
            rule: Validation rule to apply
            
        Returns:
            ValidationResult with validation details
        """
        errors = []
        warnings = []
        validated_value = value
        
        try:
            # Check required fields
            if rule.required and (value is None or value == ''):
                errors.append(rule.error_message or f"{rule.name} is required")
                return ValidationResult(False, value, errors, warnings)
            
            # Skip validation if not required and empty
            if not rule.required and (value is None or value == ''):
                return ValidationResult(True, value, errors, warnings)
            
            # Type-specific validation
            if rule.type == ValidationType.TEXT:
                validated_value, type_errors, type_warnings = self._validate_text(value, rule)
            elif rule.type == ValidationType.EMAIL:
                validated_value, type_errors, type_warnings = self._validate_email(value, rule)
            elif rule.type == ValidationType.PHONE:
                validated_value, type_errors, type_warnings = self._validate_phone(value, rule)
            elif rule.type == ValidationType.URL:
                validated_value, type_errors, type_warnings = self._validate_url(value, rule)
            elif rule.type == ValidationType.NUMBER:
                validated_value, type_errors, type_warnings = self._validate_number(value, rule)
            elif rule.type == ValidationType.INTEGER:
                validated_value, type_errors, type_warnings = self._validate_integer(value, rule)
            elif rule.type == ValidationType.FLOAT:
                validated_value, type_errors, type_warnings = self._validate_float(value, rule)
            elif rule.type == ValidationType.DATE:
                validated_value, type_errors, type_warnings = self._validate_date(value, rule)
            elif rule.type == ValidationType.DATETIME:
                validated_value, type_errors, type_warnings = self._validate_datetime(value, rule)
            elif rule.type == ValidationType.BOOLEAN:
                validated_value, type_errors, type_warnings = self._validate_boolean(value, rule)
            elif rule.type == ValidationType.UUID:
                validated_value, type_errors, type_warnings = self._validate_uuid(value, rule)
            elif rule.type == ValidationType.ZIP_CODE:
                validated_value, type_errors, type_warnings = self._validate_zip_code(value, rule)
            elif rule.type == ValidationType.SSN:
                validated_value, type_errors, type_warnings = self._validate_ssn(value, rule)
            elif rule.type == ValidationType.CREDIT_CARD:
                validated_value, type_errors, type_warnings = self._validate_credit_card(value, rule)
            else:
                type_errors, type_warnings = [], []
            
            errors.extend(type_errors)
            warnings.extend(type_warnings)
            
            # Custom validation
            if rule.custom_validator and not errors:
                try:
                    custom_result = rule.custom_validator(validated_value)
                    if isinstance(custom_result, tuple):
                        custom_valid, custom_errors = custom_result
                        if not custom_valid:
                            errors.extend(custom_errors if isinstance(custom_errors, list) else [custom_errors])
                    elif not custom_result:
                        errors.append(f"Custom validation failed for {rule.name}")
                except Exception as e:
                    errors.append(f"Custom validation error for {rule.name}: {str(e)}")
            
            is_valid = len(errors) == 0
            return ValidationResult(is_valid, validated_value, errors, warnings)
            
        except Exception as e:
            logger.error(f"Validation error for {rule.name}: {str(e)}")
            errors.append(f"Validation failed: {str(e)}")
            return ValidationResult(False, value, errors, warnings)
    
    def validate_dict(self, data: Dict[str, Any], rules: Dict[str, ValidationRule]) -> Dict[str, ValidationResult]:
        """
        Validate a dictionary of values against validation rules
        
        Args:
            data: Dictionary of values to validate
            rules: Dictionary of validation rules
            
        Returns:
            Dictionary of validation results
        """
        results = {}
        
        for field_name, rule in rules.items():
            value = data.get(field_name)
            results[field_name] = self.validate(value, rule)
        
        return results
    
    def _validate_text(self, value: Any, rule: ValidationRule) -> tuple:
        """Validate text field"""
        errors = []
        warnings = []
        
        # Convert to string
        text_value = str(value).strip()
        
        # Length validation
        if rule.min_length and len(text_value) < rule.min_length:
            errors.append(f"{rule.name} must be at least {rule.min_length} characters")
        
        if rule.max_length and len(text_value) > rule.max_length:
            errors.append(f"{rule.name} must not exceed {rule.max_length} characters")
        
        # Pattern validation
        if rule.pattern:
            if not re.match(rule.pattern, text_value, re.IGNORECASE):
                errors.append(f"{rule.name} format is invalid")
        
        # Allowed values validation
        if rule.allowed_values and text_value not in rule.allowed_values:
            errors.append(f"{rule.name} must be one of: {', '.join(map(str, rule.allowed_values))}")
        
        return text_value, errors, warnings
    
    def _validate_email(self, value: Any, rule: ValidationRule) -> tuple:
        """Validate email field"""
        errors = []
        warnings = []
        
        try:
            email_value = str(value).strip().lower()
            validation = validate_email(email_value)
            return validation.email, errors, warnings
        except EmailNotValidError as e:
            errors.append(f"{rule.name} is not a valid email address: {str(e)}")
            return value, errors, warnings
        except Exception as e:
            errors.append(f"Email validation failed: {str(e)}")
            return value, errors, warnings
    
    def _validate_phone(self, value: Any, rule: ValidationRule) -> tuple:
        """Validate phone field"""
        errors = []
        warnings = []
        
        try:
            phone_value = str(value).strip()
            
            # Remove all non-digit characters
            digits = re.sub(r'\D', '', phone_value)
            
            # Basic length check
            if len(digits) < 10:
                errors.append(f"{rule.name} must have at least 10 digits")
                return value, errors, warnings
            
            if len(digits) > 15:
                errors.append(f"{rule.name} has too many digits")
                return value, errors, warnings
            
            # Try to parse with phonenumbers library
            try:
                parsed = phonenumbers.parse(phone_value, "US")
                if not phonenumbers.is_valid_number(parsed):
                    warnings.append(f"{rule.name} may not be a valid phone number")
                
                # Format to E.164
                formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
                return formatted, errors, warnings
                
            except:
                # Fallback to basic formatting
                if len(digits) == 11 and digits.startswith('1'):
                    formatted = f"+{digits}"
                elif len(digits) == 10:
                    formatted = f"+1{digits}"
                else:
                    formatted = f"+{digits}"
                
                return formatted, errors, warnings
                
        except Exception as e:
            errors.append(f"Phone validation failed: {str(e)}")
            return value, errors, warnings
    
    def _validate_url(self, value: Any, rule: ValidationRule) -> tuple:
        """Validate URL field"""
        errors = []
        warnings = []
        
        try:
            url_value = str(value).strip()
            
            if not re.match(self.patterns['url'], url_value):
                errors.append(f"{rule.name} is not a valid URL")
            
            return url_value, errors, warnings
            
        except Exception as e:
            errors.append(f"URL validation failed: {str(e)}")
            return value, errors, warnings
    
    def _validate_number(self, value: Any, rule: ValidationRule) -> tuple:
        """Validate number field"""
        errors = []
        warnings = []
        
        try:
            if isinstance(value, (int, float)):
                num_value = float(value)
            else:
                num_value = float(str(value))
            
            # Range validation
            if rule.min_value is not None and num_value < rule.min_value:
                errors.append(f"{rule.name} must be at least {rule.min_value}")
            
            if rule.max_value is not None and num_value > rule.max_value:
                errors.append(f"{rule.name} must not exceed {rule.max_value}")
            
            return num_value, errors, warnings
            
        except (ValueError, TypeError):
            errors.append(f"{rule.name} must be a valid number")
            return value, errors, warnings
    
    def _validate_integer(self, value: Any, rule: ValidationRule) -> tuple:
        """Validate integer field"""
        errors = []
        warnings = []
        
        try:
            int_value = int(float(str(value)))
            
            # Range validation
            if rule.min_value is not None and int_value < rule.min_value:
                errors.append(f"{rule.name} must be at least {rule.min_value}")
            
            if rule.max_value is not None and int_value > rule.max_value:
                errors.append(f"{rule.name} must not exceed {rule.max_value}")
            
            return int_value, errors, warnings
            
        except (ValueError, TypeError):
            errors.append(f"{rule.name} must be a valid integer")
            return value, errors, warnings
    
    def _validate_float(self, value: Any, rule: ValidationRule) -> tuple:
        """Validate float field"""
        errors = []
        warnings = []
        
        try:
            float_value = float(str(value))
            
            # Range validation
            if rule.min_value is not None and float_value < rule.min_value:
                errors.append(f"{rule.name} must be at least {rule.min_value}")
            
            if rule.max_value is not None and float_value > rule.max_value:
                errors.append(f"{rule.name} must not exceed {rule.max_value}")
            
            return float_value, errors, warnings
            
        except (ValueError, TypeError):
            errors.append(f"{rule.name} must be a valid number")
            return value, errors, warnings
    
    def _validate_date(self, value: Any, rule: ValidationRule) -> tuple:
        """Validate date field"""
        errors = []
        warnings = []
        
        try:
            if isinstance(value, date):
                return value, errors, warnings
            
            date_str = str(value).strip()
            
            # Try common date formats
            date_formats = [
                '%Y-%m-%d',
                '%m/%d/%Y',
                '%d/%m/%Y',
                '%Y/%m/%d',
                '%m-%d-%Y',
                '%d-%m-%Y'
            ]
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt).date()
                    return parsed_date, errors, warnings
                except ValueError:
                    continue
            
            errors.append(f"{rule.name} is not a valid date")
            return value, errors, warnings
            
        except Exception as e:
            errors.append(f"Date validation failed: {str(e)}")
            return value, errors, warnings
    
    def _validate_datetime(self, value: Any, rule: ValidationRule) -> tuple:
        """Validate datetime field"""
        errors = []
        warnings = []
        
        try:
            if isinstance(value, datetime):
                return value, errors, warnings
            
            datetime_str = str(value).strip()
            
            # Try ISO format first
            try:
                parsed_datetime = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                return parsed_datetime, errors, warnings
            except ValueError:
                pass
            
            # Try common datetime formats
            datetime_formats = [
                '%Y-%m-%d %H:%M:%S',
                '%m/%d/%Y %H:%M:%S',
                '%d/%m/%Y %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d %H:%M:%S.%f'
            ]
            
            for fmt in datetime_formats:
                try:
                    parsed_datetime = datetime.strptime(datetime_str, fmt)
                    return parsed_datetime, errors, warnings
                except ValueError:
                    continue
            
            errors.append(f"{rule.name} is not a valid datetime")
            return value, errors, warnings
            
        except Exception as e:
            errors.append(f"Datetime validation failed: {str(e)}")
            return value, errors, warnings
    
    def _validate_boolean(self, value: Any, rule: ValidationRule) -> tuple:
        """Validate boolean field"""
        errors = []
        warnings = []
        
        try:
            if isinstance(value, bool):
                return value, errors, warnings
            
            bool_str = str(value).strip().lower()
            
            if bool_str in ['true', '1', 'yes', 'on']:
                return True, errors, warnings
            elif bool_str in ['false', '0', 'no', 'off']:
                return False, errors, warnings
            else:
                errors.append(f"{rule.name} must be a boolean value")
                return value, errors, warnings
                
        except Exception as e:
            errors.append(f"Boolean validation failed: {str(e)}")
            return value, errors, warnings
    
    def _validate_uuid(self, value: Any, rule: ValidationRule) -> tuple:
        """Validate UUID field"""
        errors = []
        warnings = []
        
        try:
            import uuid
            uuid_str = str(value).strip()
            
            # Try to parse as UUID
            parsed_uuid = uuid.UUID(uuid_str)
            return str(parsed_uuid), errors, warnings
            
        except ValueError:
            errors.append(f"{rule.name} is not a valid UUID")
            return value, errors, warnings
        except Exception as e:
            errors.append(f"UUID validation failed: {str(e)}")
            return value, errors, warnings
    
    def _validate_zip_code(self, value: Any, rule: ValidationRule) -> tuple:
        """Validate ZIP code field"""
        errors = []
        warnings = []
        
        try:
            zip_value = str(value).strip()
            
            if not re.match(self.patterns['zip_code'], zip_value):
                errors.append(f"{rule.name} is not a valid ZIP code")
            
            return zip_value, errors, warnings
            
        except Exception as e:
            errors.append(f"ZIP code validation failed: {str(e)}")
            return value, errors, warnings
    
    def _validate_ssn(self, value: Any, rule: ValidationRule) -> tuple:
        """Validate SSN field"""
        errors = []
        warnings = []
        
        try:
            ssn_value = str(value).strip()
            
            if not re.match(self.patterns['ssn'], ssn_value):
                errors.append(f"{rule.name} is not a valid SSN format")
            
            return ssn_value, errors, warnings
            
        except Exception as e:
            errors.append(f"SSN validation failed: {str(e)}")
            return value, errors, warnings
    
    def _validate_credit_card(self, value: Any, rule: ValidationRule) -> tuple:
        """Validate credit card field"""
        errors = []
        warnings = []
        
        try:
            cc_value = str(value).strip()
            
            # Basic pattern check
            if not re.match(self.patterns['credit_card'], cc_value):
                errors.append(f"{rule.name} is not a valid credit card format")
                return value, errors, warnings
            
            # Luhn algorithm check
            digits = re.sub(r'\D', '', cc_value)
            if not self._luhn_check(digits):
                errors.append(f"{rule.name} fails credit card validation")
            
            return cc_value, errors, warnings
            
        except Exception as e:
            errors.append(f"Credit card validation failed: {str(e)}")
            return value, errors, warnings
    
    def _luhn_check(self, card_number: str) -> bool:
        """Luhn algorithm for credit card validation"""
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
    
    def sanitize_string(self, value: str, allow_html: bool = False) -> str:
        """Sanitize string input"""
        if not value:
            return ""
        
        # Remove potentially dangerous characters
        sanitized = value.strip()
        
        if not allow_html:
            # Remove HTML tags
            sanitized = re.sub(r'<[^>]+>', '', sanitized)
        
        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')
        
        return sanitized
    
    def is_valid_us_state(self, state_code: str) -> bool:
        """Check if state code is valid US state"""
        return state_code.upper() in self.us_states


# Singleton instance
validator = Validator()
