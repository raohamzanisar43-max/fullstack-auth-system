"""
CSV Builder Utilities
Handles building and exporting CSV files for download and delivery
"""

import csv
import io
import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import zipfile
from pathlib import Path

from app.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


@dataclass
class CSVExportConfig:
    """Configuration for CSV export"""
    filename: str
    headers: List[str]
    data: List[Dict[str, Any]]
    include_timestamp: bool = True
    encoding: str = 'utf-8'
    delimiter: str = ','
    quote_char: str = '"'
    escape_char: Optional[str] = None
    line_terminator: str = '\n'


class CSVBuilder:
    """
    Comprehensive CSV builder for creating export files
    """
    
    def __init__(self):
        self.supported_encodings = ['utf-8', 'utf-16', 'latin1', 'cp1252']
        self.max_rows_per_file = 50000  # Split large files
        
    def build_csv(self, config: CSVExportConfig) -> bytes:
        """
        Build CSV file from configuration
        
        Args:
            config: CSV export configuration
            
        Returns:
            CSV file content as bytes
        """
        try:
            # Validate configuration
            self._validate_config(config)
            
            # Create CSV content
            output = io.StringIO()
            
            # Create CSV writer
            writer = csv.writer(
                output,
                delimiter=config.delimiter,
                quotechar=config.quote_char,
                escapechar=config.escape_char,
                lineterminator=config.line_terminator,
                quoting=csv.QUOTE_MINIMAL
            )
            
            # Write headers
            headers = config.headers.copy()
            if config.include_timestamp:
                headers.append('export_timestamp')
            
            writer.writerow(headers)
            
            # Write data rows
            for row in config.data:
                csv_row = [row.get(header, '') for header in config.headers]
                
                if config.include_timestamp:
                    csv_row.append(datetime.utcnow().isoformat())
                
                writer.writerow(csv_row)
            
            # Get content
            csv_content = output.getvalue()
            output.close()
            
            # Encode to bytes
            return csv_content.encode(config.encoding)
            
        except Exception as e:
            logger.error(f"CSV building failed: {str(e)}")
            raise ValidationError(f"Failed to build CSV: {str(e)}")
    
    def build_skip_trace_csv(
        self,
        trace_results: List[Dict[str, Any]],
        include_metadata: bool = True
    ) -> bytes:
        """
        Build CSV for skip trace results
        
        Args:
            trace_results: List of trace result records
            include_metadata: Whether to include metadata columns
            
        Returns:
            CSV file content as bytes
        """
        try:
            if not trace_results:
                raise ValidationError("No trace results to export")
            
            # Define columns
            base_columns = [
                'first_name',
                'last_name',
                'address',
                'city',
                'state',
                'zip_code',
                'county',
                'property_type',
                'assessed_value',
                'last_sale_date',
                'last_sale_price'
            ]
            
            phone_columns = []
            email_columns = []
            
            # Add phone and email columns (up to 5 each)
            for i in range(1, 6):
                phone_columns.extend([f'phone_{i}', f'phone_{i}_type', f'phone_{i}_confidence'])
                email_columns.extend([f'email_{i}', f'email_{i}_type', f'email_{i}_confidence'])
            
            metadata_columns = []
            if include_metadata:
                metadata_columns = [
                    'trace_date',
                    'confidence_score',
                    'data_sources',
                    'processing_time_ms'
                ]
            
            all_columns = base_columns + phone_columns + email_columns + metadata_columns
            
            # Prepare data
            csv_data = []
            for result in trace_results:
                row = {}
                
                # Base data
                for col in base_columns:
                    row[col] = result.get(col, '')
                
                # Phone data
                phones = result.get('phones', [])
                for i in range(5):
                    if i < len(phones):
                        phone = phones[i]
                        row[f'phone_{i+1}'] = phone.get('number', '')
                        row[f'phone_{i+1}_type'] = phone.get('type', '')
                        row[f'phone_{i+1}_confidence'] = phone.get('confidence', '')
                    else:
                        row[f'phone_{i+1}'] = ''
                        row[f'phone_{i+1}_type'] = ''
                        row[f'phone_{i+1}_confidence'] = ''
                
                # Email data
                emails = result.get('emails', [])
                for i in range(5):
                    if i < len(emails):
                        email = emails[i]
                        row[f'email_{i+1}'] = email.get('address', '')
                        row[f'email_{i+1}_type'] = email.get('type', '')
                        row[f'email_{i+1}_confidence'] = email.get('confidence', '')
                    else:
                        row[f'email_{i+1}'] = ''
                        row[f'email_{i+1}_type'] = ''
                        row[f'email_{i+1}_confidence'] = ''
                
                # Metadata
                if include_metadata:
                    row['trace_date'] = result.get('created_at', '')
                    row['confidence_score'] = result.get('confidence_score', '')
                    row['data_sources'] = ','.join(result.get('data_sources', []))
                    row['processing_time_ms'] = result.get('processing_time_ms', '')
                
                csv_data.append(row)
            
            # Build CSV
            config = CSVExportConfig(
                filename="skip_trace_results.csv",
                headers=all_columns,
                data=csv_data,
                include_timestamp=True
            )
            
            return self.build_csv(config)
            
        except Exception as e:
            logger.error(f"Skip trace CSV building failed: {str(e)}")
            raise ValidationError(f"Failed to build skip trace CSV: {str(e)}")
    
    def build_dnc_scrub_csv(
        self,
        scrub_results: List[Dict[str, Any]],
        include_violations_only: bool = False
    ) -> bytes:
        """
        Build CSV for DNC scrub results
        
        Args:
            scrub_results: List of DNC scrub results
            include_violations_only: Only include numbers with violations
            
        Returns:
            CSV file content as bytes
        """
        try:
            if not scrub_results:
                raise ValidationError("No scrub results to export")
            
            # Filter results if needed
            if include_violations_only:
                scrub_results = [
                    r for r in scrub_results 
                    if not r.get('clean', True)
                ]
            
            # Define columns
            columns = [
                'phone',
                'original_phone',
                'first_name',
                'last_name',
                'campaign',
                'federal_dnc',
                'state_dnc',
                'dma_dnc',
                'tcpa_litigator',
                'clean',
                'risk_score',
                'scrub_date'
            ]
            
            # Prepare data
            csv_data = []
            for result in scrub_results:
                row = {
                    'phone': result.get('phone', ''),
                    'original_phone': result.get('original_phone', ''),
                    'first_name': result.get('first_name', ''),
                    'last_name': result.get('last_name', ''),
                    'campaign': result.get('campaign', ''),
                    'federal_dnc': 'Yes' if result.get('federal_dnc') else 'No',
                    'state_dnc': 'Yes' if result.get('state_dnc') else 'No',
                    'dma_dnc': 'Yes' if result.get('dma_dnc') else 'No',
                    'tcpa_litigator': 'Yes' if result.get('tcpa_litigator') else 'No',
                    'clean': 'Yes' if result.get('clean', True) else 'No',
                    'risk_score': result.get('risk_score', 0),
                    'scrub_date': result.get('scrub_date', '')
                }
                csv_data.append(row)
            
            # Build CSV
            config = CSVExportConfig(
                filename="dnc_scrub_results.csv",
                headers=columns,
                data=csv_data,
                include_timestamp=True
            )
            
            return self.build_csv(config)
            
        except Exception as e:
            logger.error(f"DNC scrub CSV building failed: {str(e)}")
            raise ValidationError(f"Failed to build DNC scrub CSV: {str(e)}")
    
    def build_analytics_csv(
        self,
        analytics_data: List[Dict[str, Any]],
        report_type: str = "general"
    ) -> bytes:
        """
        Build CSV for analytics reports
        
        Args:
            analytics_data: Analytics data
            report_type: Type of analytics report
            
        Returns:
            CSV file content as bytes
        """
        try:
            if not analytics_data:
                raise ValidationError("No analytics data to export")
            
            # Define columns based on report type
            if report_type == "usage":
                columns = [
                    'date',
                    'total_requests',
                    'successful_requests',
                    'failed_requests',
                    'credits_used',
                    'unique_users',
                    'avg_processing_time'
                ]
            elif report_type == "financial":
                columns = [
                    'date',
                    'revenue',
                    'credits_sold',
                    'active_subscriptions',
                    'new_customers',
                    'churn_rate'
                ]
            elif report_type == "performance":
                columns = [
                    'date',
                    'avg_response_time',
                    'success_rate',
                    'error_rate',
                    'throughput',
                    'concurrent_users'
                ]
            else:
                # General - use all keys from first record
                columns = list(analytics_data[0].keys())
            
            # Build CSV
            config = CSVExportConfig(
                filename=f"analytics_{report_type}_{datetime.now().strftime('%Y%m%d')}.csv",
                headers=columns,
                data=analytics_data,
                include_timestamp=True
            )
            
            return self.build_csv(config)
            
        except Exception as e:
            logger.error(f"Analytics CSV building failed: {str(e)}")
            raise ValidationError(f"Failed to build analytics CSV: {str(e)}")
    
    def build_multi_file_zip(
        self,
        files: Dict[str, bytes],
        zip_filename: str = "export.zip"
    ) -> bytes:
        """
        Build ZIP file containing multiple CSV files
        
        Args:
            files: Dictionary of filename -> file content
            zip_filename: Name of the ZIP file
            
        Returns:
            ZIP file content as bytes
        """
        try:
            if not files:
                raise ValidationError("No files to include in ZIP")
            
            # Create ZIP file in memory
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for filename, content in files.items():
                    zip_file.writestr(filename, content)
            
            zip_buffer.seek(0)
            return zip_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"ZIP building failed: {str(e)}")
            raise ValidationError(f"Failed to build ZIP file: {str(e)}")
    
    def split_large_csv(
        self,
        config: CSVExportConfig,
        max_rows: Optional[int] = None
    ) -> List[bytes]:
        """
        Split large CSV into multiple files
        
        Args:
            config: CSV export configuration
            max_rows: Maximum rows per file
            
        Returns:
            List of CSV file contents as bytes
        """
        try:
            max_rows = max_rows or self.max_rows_per_file
            
            if len(config.data) <= max_rows:
                return [self.build_csv(config)]
            
            # Split data into chunks
            chunks = []
            for i in range(0, len(config.data), max_rows):
                chunk_data = config.data[i:i + max_rows]
                
                chunk_config = CSVExportConfig(
                    filename=f"{config.filename}_part{i//max_rows + 1}.csv",
                    headers=config.headers,
                    data=chunk_data,
                    include_timestamp=config.include_timestamp,
                    encoding=config.encoding,
                    delimiter=config.delimiter,
                    quote_char=config.quote_char,
                    escape_char=config.escape_char,
                    line_terminator=config.line_terminator
                )
                
                chunks.append(self.build_csv(chunk_config))
            
            logger.info(f"Split CSV into {len(chunks)} files")
            return chunks
            
        except Exception as e:
            logger.error(f"CSV splitting failed: {str(e)}")
            raise ValidationError(f"Failed to split CSV: {str(e)}")
    
    def _validate_config(self, config: CSVExportConfig):
        """Validate CSV export configuration"""
        if not config.filename:
            raise ValidationError("Filename is required")
        
        if not config.headers:
            raise ValidationError("Headers are required")
        
        if not config.data:
            raise ValidationError("Data is required")
        
        if config.encoding not in self.supported_encodings:
            raise ValidationError(f"Unsupported encoding: {config.encoding}")
        
        # Validate data structure
        for i, row in enumerate(config.data):
            if not isinstance(row, dict):
                raise ValidationError(f"Row {i+1} is not a dictionary")
    
    def get_file_info(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Get information about generated file"""
        return {
            "filename": filename,
            "size_bytes": len(content),
            "size_mb": round(len(content) / (1024 * 1024), 2),
            "estimated_rows": len(content.split(b'\n')) - 2,  # Approximate
            "encoding": 'utf-8',  # Default assumption
            "created_at": datetime.utcnow().isoformat()
        }


# Singleton instance
csv_builder = CSVBuilder()
