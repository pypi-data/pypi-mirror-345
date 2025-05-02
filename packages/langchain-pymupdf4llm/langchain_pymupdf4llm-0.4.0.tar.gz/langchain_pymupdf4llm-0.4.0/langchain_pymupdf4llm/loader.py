import logging
from pathlib import Path
from typing import List, Optional, Union

from langchain.document import Document
from langchain.loaders.base import BaseLoader

import fitz  # PyMuPDF


logger = logging.getLogger(__name__)


class PyMuPDFLoader(BaseLoader):
    """Load `PDF` files using `PyMuPDF`."""

    def __init__(
        self,
        file_path: Union[str, Path],
        *,
        extract_images: bool = False,
        password: Optional[str] = None,
        metadata: Optional[dict] = None,
        text_kwargs: Optional[dict] = None,
    ):
        """Initialize with file path."""
        self.file_path = Path(file_path).resolve()
        self._validate_file_path()
        self.extract_images = extract_images
        self.password = password
        self.metadata = metadata or {}
        self.text_kwargs = text_kwargs or {}

    def _validate_file_path(self) -> None:
        """Validate file path."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
        if not self.file_path.is_file():
            raise ValueError(f"Expected a file, got a directory: {self.file_path}")
        # Consider adding a check for PDF extension or mime type if desired
        # e.g., if self.file_path.suffix.lower() != ".pdf":
        #    logger.warning(...) or raise ValueError(...)

    def load(self) -> List[Document]:
        """Load file."""
        logger.info(f"Loading PDF document from {self.file_path}")
        try:
            doc = fitz.open(self.file_path, password=self.password)
        except FileNotFoundError: # Although validated in init, good practice here too
             logger.error(f"File not found during load: {self.file_path}")
             raise
        except Exception as e: # Catch potential PyMuPDF errors (e.g., RuntimeError)
            logger.error(f"Failed to open PDF {self.file_path}: {e}", exc_info=True)
            raise RuntimeError(f"Could not open PDF {self.file_path}: {e}") from e


        docs = []
        try: # Wrap page processing
            for i, page in enumerate(doc):
                logger.debug(f"Processing page {i+1}/{len(doc)}")
                # ...existing code...
                # ^-- Code for extracting text, images, metadata per page
                try:
                    text = page.get_text(**self.text_kwargs)
                    page_metadata = {"source": str(self.file_path), "page": i}
                    # ... potentially add more metadata extraction ...

                    if self.extract_images:
                        # ... existing image extraction logic ...
                        pass # Placeholder

                    # Combine custom metadata with page-specific metadata
                    combined_metadata = {**self.metadata, **page_metadata}

                    docs.append(Document(page_content=text, metadata=combined_metadata))
                except Exception as page_e:
                    logger.error(f"Error processing page {i} of {self.file_path}: {page_e}", exc_info=True)
                    # Decide whether to skip the page or re-raise
                    # For now, let's skip and log
                    continue # Skip to the next page

        finally: # Ensure the document is closed even if errors occur
            try:
                doc.close()
                logger.info(f"Finished processing {self.file_path}")
            except Exception as close_e:
                 logger.error(f"Error closing PDF document {self.file_path}: {close_e}", exc_info=True)
                 # Decide if this error should be propagated

        return docs