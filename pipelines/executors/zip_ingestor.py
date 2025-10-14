"""ZIP archive ingestor with table detection."""

import structlog
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from ingestion.chunkers import TokenAwareChunker
from ingestion.emitters import JSONLEmitter

logger = structlog.get_logger()


class ZIPIngestor:
    """Ingest ZIP archives containing regulatory tables."""
    
    def __init__(
        self,
        config: Dict[str, Any],
        chunker: TokenAwareChunker,
        emitter: JSONLEmitter,
    ):
        """
        Initialize ZIP ingestor.
        
        Args:
            config: Ingest configuration
            chunker: Token-aware chunker
            emitter: Output emitter
        """
        self.config = config
        self.chunker = chunker
        self.emitter = emitter
        self.download_dir = Path(config["download"]["download_dir"])
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = config["download"]["timeout"]
        self.user_agent = config["download"]["user_agent"]
        self.max_extract_size = config["zip"]["max_extract_size_mb"] * 1024 * 1024
        self.allowed_extensions = config["zip"]["allowed_extensions"]
        self.table_patterns = config["zip"]["table_patterns"]
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def download(self, url: str) -> Path:
        """Download ZIP file."""
        headers = {"User-Agent": self.user_agent}
        response = requests.get(url, headers=headers, timeout=self.timeout, stream=True)
        response.raise_for_status()
        
        filename = f"{hash(url)}.zip"
        file_path = self.download_dir / filename
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return file_path
    
    def extract_and_process(self, zip_path: Path, url: str, title: Optional[str]) -> bool:
        """
        Extract ZIP and process contents.
        
        Args:
            zip_path: Path to ZIP file
            url: Source URL
            title: Document title
            
        Returns:
            True if successfully processed
        """
        extract_dir = self.download_dir / f"{zip_path.stem}_extracted"
        extract_dir.mkdir(exist_ok=True)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                # Check total size
                total_size = sum(info.file_size for info in zf.infolist())
                
                if total_size > self.max_extract_size:
                    return False
                
                # Extract
                zf.extractall(extract_dir)
                
                # Process extracted files
                processed_any = False
                
                for file_path in extract_dir.rglob('*'):
                    if file_path.is_file():
                        # Check extension
                        if file_path.suffix.lower() in self.allowed_extensions:
                            # Process file
                            if self._process_file(file_path, url, title):
                                processed_any = True
                
                return processed_any
        
        except Exception:
            return False
    
    def _process_file(self, file_path: Path, source_url: str, title: Optional[str]) -> bool:
        """Process individual file from ZIP."""
        try:
            # For simplicity, process text files and CSV
            if file_path.suffix.lower() in ['.txt', '.csv']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Check for table patterns
                is_table = any(pattern in content for pattern in self.table_patterns)
                
                # Chunk content
                metadata = {
                    "is_table": is_table,
                    "file_name": file_path.name,
                    "file_type": file_path.suffix,
                }
                
                chunks = self.chunker.chunk(content, metadata)
                
                # Emit
                self.emitter.emit_chunks(
                    chunks=chunks,
                    source_url=source_url,
                    source_file=str(file_path),
                )
                
                return True
        
        except Exception:
            pass
        
        return False
    
    def ingest(
        self,
        url: str,
        title: Optional[str],
        etag: Optional[str] = None,
        last_modified: Optional[datetime] = None,
        expected_type: str = "zip",
    ) -> bool:
        """
        Ingest ZIP archive.
        
        Args:
            url: ZIP URL
            title: Document title
            etag: Previous ETag (unused for now)
            last_modified: Previous Last-Modified (unused for now)
            expected_type: Expected document type (should be 'zip')
            
        Returns:
            True if successfully ingested
        """
        # Validate expected type
        if expected_type and expected_type != "zip":
            logger.error(
                "zip_type_mismatch",
                url=url,
                expected=expected_type,
                executor="zip",
            )
            return False
        
        try:
            logger.info("zip_download_start", url=url)
            zip_path = self.download(url)
            logger.info("zip_downloaded", url=url, path=str(zip_path))
            
            logger.info("zip_extract_start", url=url)
            result = self.extract_and_process(zip_path, url, title)
            
            if result:
                logger.info("zip_ingest_complete", url=url)
            else:
                logger.warning("zip_ingest_no_files_processed", url=url)
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(
                "zip_download_failed",
                url=url,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            raise
        except Exception as e:
            logger.error(
                "zip_ingest_failed",
                url=url,
                error_type=type(e).__name__,
                error_message=str(e),
            )
            raise

