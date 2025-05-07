"""
Content type detection and validation service.
"""
import json
import mimetypes
import xml.etree.ElementTree as ET
from typing import Any, Dict, Tuple, Union

class ValidationError(Exception):
    """Exception raised for validation errors."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class ContentTypeInterpreter:
    """Service for content type detection and validation."""

    SIGNATURES: Dict[bytes, str] = {
        # Images
        b'\x89PNG\r\n\x1a\n': 'image/png',
        b'\xff\xd8\xff': 'image/jpeg',
        b'GIF87a': 'image/gif',
        b'GIF89a': 'image/gif',
        b'BM': 'image/bmp',
        b'\x00\x00\x01\x00': 'image/x-icon',
        b'\x00\x00\x02\x00': 'image/x-icon',
        b'RIFF': 'image/webp',  # WebP file signature
        b'WEBP': 'image/webp',  # Alternative WebP signature
        
        # Documents
        b'%PDF': 'application/pdf',
        b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1': 'application/msword',  # DOC
        b'PK\x03\x04\x14\x00\x06\x00': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # DOCX
        b'PK\x03\x04\x14\x00\x08\x00': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # XLSX
        b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1': 'application/vnd.ms-excel',  # XLS
        b'PK\x03\x04\x14\x00\x06\x00': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',  # PPTX
        b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1': 'application/vnd.ms-powerpoint',  # PPT
        
        # Archives
        b'PK\x03\x04': 'application/zip',
        b'\x1f\x8b\x08': 'application/gzip',
        b'Rar!\x1a\x07\x00': 'application/x-rar-compressed',
        b'7z\xbc\xaf\x27\x1c': 'application/x-7z-compressed',
        
        # Database
        b'SQLite format 3\x00': 'application/x-sqlite3',
        
        # Other
        b'AT&TFORM': 'image/djvu',  # DjVu
        b'PAR1': 'application/x-parquet',  # Parquet files
    }

    TEXT_MIME_TYPES = {
        # Basic text formats
        'text/plain',
        'text/html',
        'text/xml',
        'text/csv',
        'text/css',
        'text/javascript',
        'text/markdown',
        'text/x-python',
        'text/x-java',
        'text/x-c',
        'text/x-sql',
        
        # Application text formats
        'application/json',
        'application/xml',
        'application/x-yaml',
        'application/javascript',
        'application/x-httpd-php',
        'application/x-sh',
        'application/x-tex',
        
        # Diagram formats
        'text/vnd.graphviz',
        'text/x-mermaid',
        'text/x-plantuml',
        
        # Configuration formats
        'application/x-properties',
        'application/toml',
        'application/x-yaml',
    }

    @staticmethod
    def _detect_by_signature(content: bytes) -> str:
        """Detect MIME type using file signatures."""
        # Check for known file signatures
        for signature, mime_type in ContentTypeInterpreter.SIGNATURES.items():
            if content.startswith(signature):
                return mime_type
        
        # Check for XML or SVG content
        if content.startswith(b'<?xml') or content.lstrip(b' \t\n\r').startswith(b'<'):
            return ContentTypeInterpreter._detect_xml_or_svg(content)
        
        return 'application/octet-stream'  # Default MIME type for unknown content

    @staticmethod
    def _detect_xml_or_svg(content: bytes) -> str:
        """Detect if content is XML or SVG."""
        try:
            text_content = content.decode('utf-8', errors='ignore')
            if ContentTypeInterpreter.is_svg_content(text_content):
                return 'image/svg+xml'
            # Validate XML structure
            ET.fromstring(content)
            return 'application/xml'
        except (ET.ParseError, UnicodeDecodeError):
            return 'application/octet-stream'

    @staticmethod
    def detect_content_type(content: Union[str, bytes]) -> Tuple[str, str]:
        """
        Detect content type and suggested extension.
        Returns tuple of (mime_type, extension).
        """
        if isinstance(content, str):
            # Try to parse as JSON
            try:
                json.loads(content)
                return 'application/json', 'json'
            except json.JSONDecodeError:
                pass
            
            # Try to parse as XML
            try:
                # Convert string to bytes for consistent handling
                content_bytes = content.encode('utf-8')
                try:
                    ET.fromstring(content_bytes)
                    # Check if it's specifically an SVG
                    if ContentTypeInterpreter.is_svg_content(content):
                        return 'image/svg+xml', 'svg'
                    # Generic XML
                    return 'application/xml', 'xml'
                except ET.ParseError:
                    pass
            except Exception:
                pass
            
            # Default to text/plain for strings
            return 'text/plain', 'txt'
        
        elif isinstance(content, bytes):
            # First try to detect XML content
            if content.startswith(b'<?xml') or content.lstrip(b' \t\n\r').startswith(b'<'):
                try:
                    text_content = content.decode('utf-8')
                    try:
                        ET.fromstring(content)
                        if ContentTypeInterpreter.is_svg_content(text_content):
                            return 'image/svg+xml', 'svg'
                        return 'application/xml', 'xml'
                    except ET.ParseError:
                        # Invalid XML should be treated as text
                        return 'text/plain', 'txt'
                except UnicodeDecodeError:
                    pass

            # Then check for binary signatures at the start
            for signature, mime_type in ContentTypeInterpreter.SIGNATURES.items():
                if content.startswith(signature):
                    return mime_type, ContentTypeInterpreter.get_extension(mime_type)

            # If no specific binary format detected, check for text formats
            try:
                text_content = content.decode('utf-8')
                text_content = text_content.strip()
                
                # Check for JSON
                if text_content.startswith('{') and text_content.endswith('}'):
                    try:
                        # Check for comments
                        lines = text_content.split('\n')
                        if any(line.strip().startswith('//') for line in lines):
                            return 'text/plain', 'txt'
                        json.loads(text_content)
                        return 'application/json', 'json'
                    except json.JSONDecodeError:
                        return 'text/plain', 'txt'
                
                # Default to text/plain for decodeable content
                return 'text/plain', 'txt'
            except UnicodeDecodeError:
                pass
            
            # Check for mixed content
            if content.startswith(b'<?xml'):
                return 'application/xml', 'xml'
            
            return 'application/octet-stream', ''

        raise ValidationError("Content must be string or bytes")

    def validate_content(self, content: Union[str, bytes]) -> None:
        """Validate content based on its detected type."""
        print(f"Validating content: {content}")  # Debug statement
        if not content:
            raise ValidationError("Empty content")

        # Ensure that the content is not just random bytes
        if isinstance(content, bytes) and not content.strip():
            raise ValidationError("Invalid content: empty byte array")

        try:
            mime_type, _ = self.detect_content_type(content)
            print(f"Detected MIME type: {mime_type}")  # Debug statement
            print(f"Validation started for {mime_type} content.")  # Debug statement

            # For text content, validate that it's proper UTF-8 and meaningful content
            if mime_type == 'text/plain':
                if isinstance(content, bytes):
                    try:
                        text_content = content.decode('utf-8')
                    except UnicodeDecodeError:
                        raise ValidationError("Invalid content: not valid UTF-8")
                else:
                    text_content = content

                # Check if content is just random bytes, invalid characters, or too short
                if not text_content.strip():
                    raise ValidationError("Invalid content: empty text")
                if len(text_content.strip()) < 3:  # Require at least 3 meaningful characters
                    raise ValidationError("Invalid content: too short")
                if all(ord(c) < 32 for c in text_content.strip()):
                    raise ValidationError("Invalid content: contains only control characters")

                # Validate text content structure
                lines = text_content.strip().split('\n')
                if len(lines) < 1:
                    raise ValidationError("Invalid content: no lines")
                
                # Check for meaningful content structure
                has_valid_structure = False
                
                # Try JSON validation
                if text_content.strip().startswith('{') and text_content.strip().endswith('}'):
                    try:
                        json.loads(text_content)
                        print(f"JSON content validated successfully.")
                        has_valid_structure = True
                    except json.JSONDecodeError:
                        raise ValidationError("Invalid JSON content")

                # Try XML validation
                elif text_content.strip().startswith('<'):
                    try:
                        ET.fromstring(text_content)
                        print(f"XML content validated successfully.")
                        has_valid_structure = True
                    except ET.ParseError:
                        raise ValidationError("Invalid XML content")

                # For plain text, ensure it contains meaningful content
                if not has_valid_structure:
                    # Check if content looks like a valid text document
                    words = text_content.strip().split()
                    if len(words) < 2:  # Require at least 2 words for meaningful text
                        raise ValidationError("Invalid content: insufficient text content")
                    
                    # Check if content has a reasonable distribution of characters
                    char_counts = {}
                    total_chars = 0
                    for c in text_content:
                        if c.isprintable():
                            char_counts[c] = char_counts.get(c, 0) + 1
                            total_chars += 1
                    
                    if total_chars == 0:
                        raise ValidationError("Invalid content: no printable characters")
                    
                    # Check character distribution (no single character should dominate)
                    for count in char_counts.values():
                        if count / total_chars > 0.5:  # No character should be more than 50% of content
                            raise ValidationError("Invalid content: suspicious character distribution")

                    # Check for reasonable text patterns
                    if not any(c.isspace() for c in text_content):
                        raise ValidationError("Invalid content: no whitespace found")
                    if not any(c.isalpha() for c in text_content):
                        raise ValidationError("Invalid content: no letters found")
                    
                    # Check for proper sentence structure
                    sentences = [s.strip() for s in text_content.split('.') if s.strip()]
                    if not sentences:
                        raise ValidationError("Invalid content: no proper sentences found")
                    
                    # Each sentence should:
                    # 1. Start with an uppercase letter
                    # 2. Have at least 2 words
                    # 3. End with proper punctuation
                    for sentence in sentences:
                        if not sentence[0].isupper():
                            raise ValidationError("Invalid content: sentence must start with uppercase letter")
                        words = sentence.split()
                        if len(words) < 2:
                            raise ValidationError("Invalid content: sentence must have at least 2 words")
                        if not any(sentence.strip().endswith(p) for p in ['.', '!', '?']):
                            raise ValidationError("Invalid content: sentence must end with proper punctuation")

            # Handle text-based content types
            elif mime_type == 'application/json':
                if isinstance(content, bytes):
                    content = content.decode('utf-8')
                try:
                    # Check for comments before attempting to parse
                    lines = content.split('\n')
                    if any(line.strip().startswith('//') for line in lines):
                        raise ValidationError("Invalid JSON content")
                    json.loads(content)
                    print(f"JSON content validated successfully.")  # Debug statement
                except (json.JSONDecodeError, UnicodeDecodeError):
                    raise ValidationError("Invalid JSON content")
                # Add a check for invalid content
                if not content:
                    raise ValidationError("Invalid content: empty content")

            elif mime_type == 'application/xml' or mime_type == 'image/svg+xml':
                if isinstance(content, bytes):
                    content = content.decode('utf-8')
                try:
                    ET.fromstring(content)
                    print(f"XML content validated successfully.")  # Debug statement
                except (ET.ParseError, UnicodeDecodeError):
                    raise ValidationError("Invalid XML content")
                # Check for mixed content (XML + binary)
                if isinstance(content, str):
                    content = content.encode('utf-8')
                for signature in ContentTypeInterpreter.SIGNATURES:
                    if signature in content and not content.startswith(signature):
                        raise ValidationError("Invalid XML content")

            # Handle binary content types
            elif mime_type.startswith('image/'):
                # Basic validation for image formats
                if mime_type == 'image/png' and len(content) <= 8:  # PNG header is 8 bytes
                    raise ValidationError("Invalid content: truncated PNG file")
                elif mime_type == 'image/jpeg' and len(content) <= 3:  # JPEG header is 3 bytes
                    raise ValidationError("Invalid content: truncated JPEG file")
                elif mime_type == 'image/gif' and len(content) <= 6:  # GIF header is 6 bytes
                    raise ValidationError("Invalid content: truncated GIF file")
                elif not any(content.startswith(sig) for sig in [sig for sig, mime in ContentTypeInterpreter.SIGNATURES.items() if mime == mime_type]):
                    raise ValidationError(f"Invalid {mime_type} content: missing proper header")
                print(f"Image content validated successfully.")  # Debug statement

            elif mime_type == 'application/pdf':
                if not content.startswith(b'%PDF-'):
                    raise ValidationError("Invalid PDF content")
                print(f"PDF content validated successfully.")  # Debug statement

            elif mime_type == 'application/zip':
                if len(content) <= 4:  # ZIP header is 4 bytes
                    raise ValidationError("Invalid ZIP content")
                print(f"ZIP content validated successfully.")  # Debug statement

            print(f"Validation completed for {mime_type} content.")  # Debug statement

        except ValidationError as e:
            raise e
        except Exception as e:
            raise ValidationError(f"Validation failed: {str(e)}")

    @staticmethod
    def is_binary_content(content: Union[str, bytes]) -> bool:
        """
        Determine if content should be treated as binary.
        
        This method uses multiple heuristics:
        1. If content is already a string, it's not binary
        2. For bytes content:
           - Check for known binary signatures
           - Try UTF-8 decoding
           - Analyze content patterns
        """
        if isinstance(content, str):
            return False
        
        if not isinstance(content, (bytes, bytearray)):
            raise ValidationError("Content must be string or bytes")

        # Check for known binary signatures
        mime_type = ContentTypeInterpreter._detect_by_signature(content)
        if mime_type != 'application/octet-stream':
            return mime_type not in ContentTypeInterpreter.TEXT_MIME_TYPES
        
        # Try to decode as UTF-8
        try:
            content.decode('utf-8')
            # Check for binary patterns
            # Look at first 1024 bytes for null bytes or high number of non-ASCII chars
            sample = content[:1024]
            if not sample:  # Handle empty content
                return False
                
            null_count = sample.count(b'\x00')
            non_ascii = sum(1 for b in sample if b > 0x7F)
            
            # If more than 30% non-ASCII or contains null bytes, likely binary
            return (null_count > 0) or (non_ascii / len(sample) > 0.3)
        except UnicodeDecodeError:
            return True

    @staticmethod
    def is_xml_content(content: Union[str, bytes]) -> bool:
        """Check if content is valid XML."""
        print(f"Checking if content is XML: {content}")  # Debug statement
        try:
            if isinstance(content, str):
                content = content.encode('utf-8')

            # Try to parse the XML without requiring XML declaration
            ET.fromstring(content)
            print(f"Valid XML content detected.")  # Debug statement
            return True
        except Exception as e:
            print(f"Invalid XML content detected: {str(e)}")  # Debug statement
            return False

    @staticmethod
    def is_svg_content(content: Union[str, bytes]) -> bool:
        """Check if content is SVG."""
        if isinstance(content, bytes):
            content = content.decode('utf-8', errors='ignore')
        
        # First check if it's valid XML
        if not ContentTypeInterpreter.is_xml_content(content):
            return False
        
        try:
            # Parse XML and check for SVG namespace
            tree = ET.fromstring(content)
            return (
                tree.tag == 'svg' or
                tree.tag.endswith('}svg') or
                any(attr.endswith('xmlns') and 'svg' in value
                    for attr, value in tree.attrib.items())
            )
        except Exception:
            return False

    @staticmethod
    def is_mermaid_content(content: str) -> bool:
        """Check if content is Mermaid diagram."""
        content = content.strip().lower()
        mermaid_keywords = [
            'graph ', 'sequencediagram', 'classDiagram',
            'stateDiagram', 'erDiagram', 'gantt',
            'pie', 'flowchart', 'journey'
        ]
        return any(content.startswith(keyword.lower()) for keyword in mermaid_keywords)

    @staticmethod
    def is_diagram_content(content: str) -> bool:
        """Check if content is a diagram format."""
        content = content.strip().lower()
        # Check for PlantUML
        if content.startswith('@startuml') and content.endswith('@enduml'):
            return True
        # Check for Graphviz
        if content.startswith(('digraph', 'graph', 'strict')):
            return True
        # Check for Mermaid
        return ContentTypeInterpreter.is_mermaid_content(content)

    @staticmethod
    def get_extension(mime_type: str) -> str:
        """Get file extension from MIME type."""
        extension = {
            # Images
            'image/png': 'png',
            'image/jpeg': 'jpg',
            'image/gif': 'gif',
            'image/bmp': 'bmp',
            'image/x-icon': 'ico',
            'image/svg+xml': 'svg',
            'image/djvu': 'djvu',
            'image/webp': 'webp',
            
            # Documents
            'application/pdf': 'pdf',
            'application/msword': 'doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
            'application/vnd.ms-excel': 'xls',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
            'application/vnd.ms-powerpoint': 'ppt',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'pptx',
            
            # Archives
            'application/zip': 'zip',
            'application/gzip': 'gz',
            'application/x-rar-compressed': 'rar',
            'application/x-7z-compressed': '7z',
            
            # Database
            'application/x-sqlite3': 'db',
            'application/x-parquet': 'parquet',
            
            # Text formats
            'text/plain': 'txt',
            'text/html': 'html',
            'text/xml': 'xml',
            'text/csv': 'csv',
            'text/css': 'css',
            'text/javascript': 'js',
            'text/markdown': 'md',
            'text/x-python': 'py',
            'text/x-java': 'java',
            'text/x-c': 'c',
            'text/x-sql': 'sql',
            
            # Application formats
            'application/json': 'json',
            'application/xml': 'xml',
            'application/x-yaml': 'yaml',
            'application/javascript': 'js',
            'application/x-httpd-php': 'php',
            'application/x-sh': 'sh',
            'application/x-tex': 'tex',
            
            # Diagram formats
            'text/vnd.graphviz': 'dot',
            'text/x-mermaid': 'mmd',
            'text/x-plantuml': 'puml',
            
            # Configuration formats
            'application/x-properties': 'properties',
            'application/toml': 'toml',
            'application/x-yaml': 'yaml',
        }.get(mime_type, '')
        
        return extension

    @staticmethod
    def get_default_extension(mime_type: str) -> str:
        """
        Return the default file extension for a given MIME type.
        """
        mime_to_extension = {
            'application/pdf': 'pdf',
            'text/plain': 'txt',
            'image/png': 'png',
            'image/jpeg': 'jpg',
            'video/quicktime': 'mov',
            'application/x-tex': 'tex',
            'application/3d-obj': 'obj',
            'image/svg+xml': 'svg',
            'text/x-mermaid': 'mmd',
            'image/vnd.djvu': 'djv',
            'image/vnd.dxf': 'dxf',
            # Add more mappings as needed
        }
        return mime_to_extension.get(mime_type, '')
