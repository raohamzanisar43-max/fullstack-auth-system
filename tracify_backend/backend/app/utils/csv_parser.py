"""
CSV Parser Utilities
Handles parsing and validation of CSV files for upload and processing
"""

import csv
import io
import logging
from typing import List, Dict, Any, Optional, Tuple, Iterator
from dataclasses import dataclass
from enum import Enum
import chardet
import pandas as pd

from app.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class ColumnType(Enum):
    """Supported column types for CSV parsing"""
    TEXT = "text"
    NUMBER = "number"
    EMAIL = "email"
    PHONE = "phone"
    ADDRESS = "address"
    DATE = "date"
    BOOLEAN = "boolean"


@dataclass
class CSVColumn:
    """CSV column definition"""
    name: str
    type: ColumnType
    required: bool = True
    validation_pattern: Optional[str] = None
    description: Optional[str] = None


@dataclass
class CSVParseResult:
    """Result of CSV parsing operation"""
    success: bool
    total_rows: int
    valid_rows: int
    invalid_rows: int
    headers: List[str]
    data: List[Dict[str, Any]]
    errors: List[str]
    warnings: List[str]
    sample_data: List[Dict[str, Any]]


class CSVParser:
    """
    Comprehensive CSV parser with validation and error handling
    """
    
    def __init__(self):
        self.supported_encodings = ['utf-8', 'utf-16', 'latin1', 'cp1252']
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.max_rows = 100000  # 100k rows max
        
    def parse_file(
        self,
        file_content: bytes,
        expected_columns: Optional[List[CSVColumn]] = None,
        delimiter: str = ",",
        has_header: bool = True
    ) -> CSVParseResult:
        """
        Parse CSV file content with validation
        
        Args:
            file_content: Raw file content as bytes
            expected_columns: Expected column definitions
            delimiter: CSV delimiter
            has_header: Whether CSV has header row
            
        Returns:
            CSVParseResult with parsed data and validation info
        """
        try:
            # Validate file size
            if len(file_content) > self.max_file_size:
                raise ValidationError(f"File size exceeds maximum allowed size of {self.max_file_size / (1024*1024):.1f}MB")
            
            # Detect encoding
            encoding = self._detect_encoding(file_content)
            
            # Decode content
            try:
                text_content = file_content.decode(encoding)
            except UnicodeDecodeError as e:
                raise ValidationError(f"Failed to decode file with detected encoding {encoding}: {str(e)}")
            
            # Parse CSV
            csv_data = self._parse_csv_text(text_content, delimiter, has_header)
            
            # Validate structure
            if expected_columns:
                validation_result = self._validate_columns(csv_data, expected_columns)
                if not validation_result['valid']:
                    raise ValidationError(f"Column validation failed: {validation_result['errors']}")
            
            # Validate and clean data
            cleaned_data, errors, warnings = self._validate_and_clean_data(
                csv_data, expected_columns
            )
            
            # Create result
            total_rows = len(cleaned_data) + len(errors)
            valid_rows = len(cleaned_data)
            invalid_rows = len(errors)
            
            result = CSVParseResult(
                success=True,
                total_rows=total_rows,
                valid_rows=valid_rows,
                invalid_rows=invalid_rows,
                headers=csv_data[0].keys() if csv_data else [],
                data=cleaned_data,
                errors=errors,
                warnings=warnings,
                sample_data=cleaned_data[:5]  # First 5 rows as sample
            )
            
            logger.info(f"CSV parsing completed: {valid_rows} valid, {invalid_rows} invalid rows")
            return result
            
        except Exception as e:
            logger.error(f"CSV parsing failed: {str(e)}")
            return CSVParseResult(
                success=False,
                total_rows=0,
                valid_rows=0,
                invalid_rows=0,
                headers=[],
                data=[],
                errors=[str(e)],
                warnings=[],
                sample_data=[]
            )
    
    def _detect_encoding(self, file_content: bytes) -> str:
        """Detect file encoding"""
        try:
            result = chardet.detect(file_content[:10000])  # Sample first 10KB
            encoding = result['encoding']
            confidence = result['confidence']
            
            if encoding and confidence > 0.7:
                return encoding
            
            # Fall back to common encodings
            for enc in self.supported_encodings:
                try:
                    file_content.decode(enc)
                    return enc
                except UnicodeDecodeError:
                    continue
            
            return 'utf-8'  # Default fallback
            
        except Exception as e:
            logger.warning(f"Encoding detection failed: {str(e)}")
            return 'utf-8'
    
    def _parse_csv_text(self, text_content: str, delimiter: str, has_header: bool) -> List[Dict[str, Any]]:
        """Parse CSV text into list of dictionaries"""
        try:
            # Use pandas for robust CSV parsing
            df = pd.read_csv(
                io.StringIO(text_content),
                delimiter=delimiter,
                header=0 if has_header else None,
                skipinitialspace=True,
                dtype=str,
                na_filter=False,
                keep_default_na=False
            )
            
            # Convert to list of dictionaries
            data = df.to_dict('records')
            
            # Limit rows
            if len(data) > self.max_rows:
                logger.warning(f"CSV has {len(data)} rows, limiting to {self.max_rows}")
                data = data[:self.max_rows]
            
            return data
            
        except Exception as e:
            # Fallback to standard csv parser
            try:
                reader = csv.DictReader(io.StringIO(text_content), delimiter=delimiter)
                data = list(reader)
                
                if len(data) > self.max_rows:
                    data = data[:self.max_rows]
                
                return data
                
            except Exception as e2:
                raise ValidationError(f"Failed to parse CSV: {str(e2)}")
    
    def _validate_columns(
        self,
        csv_data: List[Dict[str, Any]],
        expected_columns: List[CSVColumn]
    ) -> Dict[str, Any]:
        """Validate CSV columns against expected structure"""
        if not csv_data:
            return {"valid": False, "errors": ["CSV file is empty"]}
        
        actual_headers = set(csv_data[0].keys())
        expected_headers = {col.name for col in expected_columns}
        
        errors = []
        warnings = []
        
        # Check missing required columns
        missing_required = []
        for col in expected_columns:
            if col.required and col.name not in actual_headers:
                missing_required.append(col.name)
        
        if missing_required:
            errors.append(f"Missing required columns: {', '.join(missing_required)}")
        
        # Check for unexpected columns
        unexpected = actual_headers - expected_headers
        if unexpected:
            warnings.append(f"Unexpected columns found: {', '.join(unexpected)}")
        
        # Check case sensitivity
        for col in expected_columns:
            if col.name not in actual_headers:
                # Try case-insensitive match
                case_matches = [h for h in actual_headers if h.lower() == col.name.lower()]
                if case_matches:
                    warnings.append(f"Column '{col.name}' found as '{case_matches[0]}' (case mismatch)")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _validate_and_clean_data(
        self,
        csv_data: List[Dict[str, Any]],
        expected_columns: Optional[List[CSVColumn]] = None
    ) -> Tuple[List[Dict[str, Any]], List[str], List[str]]:
        """Validate and clean CSV data row by row"""
        cleaned_data = []
        errors = []
        warnings = []
        
        for row_index, row in enumerate(csv_data, 1):
            row_errors = []
            row_warnings = []
            cleaned_row = {}
            
            # Process each column
            for key, value in row.items():
                try:
                    # Clean value
                    cleaned_value = self._clean_cell_value(value)
                    
                    # Validate if column definition exists
                    if expected_columns:
                        col_def = next((c for c in expected_columns if c.name == key), None)
                        if col_def:
                            validation_result = self._validate_cell_value(
                                cleaned_value, col_def, row_index, key
                            )
                            if not validation_result['valid']:
                                row_errors.extend(validation_result['errors'])
                            row_warnings.extend(validation_result['warnings'])
                            cleaned_value = validation_result['value']
                    
                    cleaned_row[key] = cleaned_value
                    
                except Exception as e:
                    row_errors.append(f"Row {row_index}, Column '{key}': {str(e)}")
                    cleaned_row[key] = row.get(key, '')  # Keep original value on error
            
            # Add row to results
            if row_errors:
                errors.extend(row_errors)
            else:
                cleaned_data.append(cleaned_row)
            
            warnings.extend(row_warnings)
        
        return cleaned_data, errors, warnings
    
    def _clean_cell_value(self, value: Any) -> str:
        """Clean individual cell value"""
        if value is None or value == '':
            return ''
        
        # Convert to string and strip whitespace
        cleaned = str(value).strip()
        
        # Remove extra whitespace
        cleaned = ' '.join(cleaned.split())
        
        return cleaned
    
    def _validate_cell_value(
        self,
        value: str,
        column_def: CSVColumn,
        row_index: int,
        column_name: str
    ) -> Dict[str, Any]:
        """Validate individual cell value against column definition"""
        errors = []
        warnings = []
        valid_value = value
        
        # Check required fields
        if column_def.required and not value:
            errors.append(f"Row {row_index}, Column '{column_name}': Required field is empty")
        
        # Skip validation if empty and not required
        if not value and not column_def.required:
            return {"valid": True, "value": value, "errors": [], "warnings": []}
        
        # Type-specific validation
        if column_def.type == ColumnType.EMAIL:
            if not self._is_valid_email(value):
                errors.append(f"Row {row_index}, Column '{column_name}': Invalid email format")
        
        elif column_def.type == ColumnType.PHONE:
            phone = self._normalize_phone(value)
            if not self._is_valid_phone(phone):
                errors.append(f"Row {row_index}, Column '{column_name}': Invalid phone format")
            else:
                valid_value = phone
        
        elif column_def.type == ColumnType.NUMBER:
            if not self._is_valid_number(value):
                errors.append(f"Row {row_index}, Column '{column_name}': Invalid number format")
            else:
                valid_value = value
        
        elif column_def.type == ColumnType.DATE:
            if not self._is_valid_date(value):
                warnings.append(f"Row {row_index}, Column '{column_name}': Unusual date format")
        
        # Custom pattern validation
        if column_def.validation_pattern:
            import re
            if not re.match(column_def.validation_pattern, value):
                errors.append(f"Row {row_index}, Column '{column_name}': Does not match required pattern")
        
        return {
            "valid": len(errors) == 0,
            "value": valid_value,
            "errors": errors,
            "warnings": warnings
        }
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _is_valid_phone(self, phone: str) -> bool:
        """Validate phone format"""
        import re
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        return len(digits) >= 10 and len(digits) <= 15
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number format"""
        import re
        digits = re.sub(r'\D', '', phone)
        
        if len(digits) == 11 and digits.startswith('1'):
            digits = digits[1:]  # Remove US country code
        
        return digits
    
    def _is_valid_number(self, value: str) -> bool:
        """Validate number format"""
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def _is_valid_date(self, value: str) -> bool:
        """Validate date format"""
        from datetime import datetime
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
                datetime.strptime(value, fmt)
                return True
            except ValueError:
                continue
        
        return False
    
    def get_column_preview(self, file_content: bytes, max_rows: int = 5) -> Dict[str, Any]:
        """Get preview of CSV columns without full parsing"""
        try:
            encoding = self._detect_encoding(file_content)
            text_content = file_content.decode(encoding)
            
            df = pd.read_csv(
                io.StringIO(text_content),
                nrows=max_rows,
                dtype=str,
                na_filter=False,
                keep_default_na=False
            )
            
            return {
                "success": True,
                "columns": list(df.columns),
                "sample_data": df.to_dict('records'),
                "total_columns": len(df.columns),
                "encoding": encoding
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "columns": [],
                "sample_data": [],
                "total_columns": 0,
                "encoding": None
            }


# Predefined column sets for common use cases
SKIP_TRACE_COLUMNS = [
    CSVColumn("first_name", ColumnType.TEXT, required=True, description="Property owner first name"),
    CSVColumn("last_name", ColumnType.TEXT, required=True, description="Property owner last name"),
    CSVColumn("address", ColumnType.ADDRESS, required=True, description="Property address"),
    CSVColumn("city", ColumnType.TEXT, required=True, description="Property city"),
    CSVColumn("state", ColumnType.TEXT, required=True, description="Property state"),
    CSVColumn("zip_code", ColumnType.TEXT, required=False, description="Property ZIP code"),
    CSVColumn("phone", ColumnType.PHONE, required=False, description="Phone number"),
    CSVColumn("email", ColumnType.EMAIL, required=False, description="Email address"),
]

DNC_SCRUB_COLUMNS = [
    CSVColumn("phone", ColumnType.PHONE, required=True, description="Phone number to scrub"),
    CSVColumn("name", ColumnType.TEXT, required=False, description="Contact name"),
    CSVColumn("campaign", ColumnType.TEXT, required=False, description="Campaign name"),
]

# Singleton instance
csv_parser = CSVParser()
