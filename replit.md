# Overview

This is a PDF renaming application built with Streamlit that uses Optical Character Recognition (OCR) to automatically extract information from PDF documents and rename them according to user-defined templates. The application supports multiple document types including invoices (Notas Fiscais), payment receipts, legal processes, and insurance claims, with the ability to create custom naming patterns.

The tool processes PDF files by converting them to images, applying OCR via Tesseract, extracting relevant information using regex patterns, and generating standardized filenames. It supports batch processing and can export renamed files as a ZIP archive.

## Recent Changes (November 8, 2025)

### Major Refactoring - Batch Processing System
- **Modular Architecture**: Separated concerns into core modules (core/ocr.py, core/parser.py, core/batch_manager.py)
- **Batch Management System**: Automatic division of PDFs into batches of 50 for optimized processing
- **Task Queue**: Persistent JSON-based queue with status tracking (pending, processing, completed, failed)
- **Separated Data Storage**: Fixed critical bug - binary PDF content stored in Streamlit session state, only metadata in JSON
- **Progress Tracking**: Real-time progress bars with batch-level status monitoring
- **4-Tab Interface**: Organized UI with Upload, Task Queue, Cloud Storage, and Settings tabs
- **Cloud Storage Integration**: Instructions and UI for Google Drive and Dropbox monitoring (manual setup required - no native Replit integration available)
- **Email Notifications**: Configuration interface for email notifications when batches complete
- **Improved Error Handling**: Individual error tracking per file without stopping batch processing
- **Download Management**: ZIP download for each completed batch separately

### Performance & Reliability
- **Hybrid OCR**: PyPDF2 first (fast), fallback to Tesseract OCR (slow but works on scans)
- **Optimized Settings**: 2 pages max, 150 DPI default for speed/quality balance
- **Persistent State**: Batch data survives Streamlit reruns via JSON persistence
- **Clean Separation**: Binary data never touches JSON serialization (fixes TypeError crashes)

# User Preferences

Preferred communication style: Portuguese (Brazilian), simple everyday language.

# Como Iniciar a Aplicação

**Método Rápido**: Execute `bash start.sh` no Shell

O workflow do Replit (`streamlit_app`) falha devido a problema de timeout na porta 5000, mas a aplicação funciona perfeitamente quando executada manualmente. O script `start.sh` verifica se o Streamlit está rodando e inicia automaticamente se necessário.

Para mais detalhes, veja o arquivo `INICIAR.md`.

# System Architecture

## Application Framework
- **Streamlit**: Web-based UI framework for the entire application
  - Chosen for rapid prototyping and built-in state management
  - Provides interactive widgets without requiring frontend development
  - Session state used to persist binary PDF data and results
  - 4-tab interface: Upload & Process, Task Queue, Cloud Storage, Settings

## Batch Processing System
- **BatchManager** (core/batch_manager.py): Manages division and tracking of large PDF batches
  - Automatically divides uploads into groups of 50 PDFs
  - Persists batch metadata to data/batches.json (never binary content)
  - Tracks status, progress, results, and errors per batch
  - Auto-cleanup of batches older than 7 days
  - Supports concurrent batch processing with independent progress tracking

## Document Processing Pipeline
- **OCR Module** (core/ocr.py): Hybrid text extraction for maximum compatibility
  - **Step 1**: PyPDF2 direct text extraction (fast, <1s per PDF)
  - **Step 2**: PyMuPDF + Tesseract OCR fallback (slow, ~30-60s per scanned PDF)
  - Processes max 2 pages at 150 DPI by default (configurable)
  - Handles both digital PDFs and scanned documents seamlessly
  
- **Parser Module** (core/parser.py): Regex-based data extraction and filename generation
  - Predefined templates for: Notas Fiscais, Comprovantes, Processos Judiciais, Sinistros
  - Extracts structured fields: numbers, dates, values, names
  - Generates clean filenames with configurable separators and affixes
  - Sanitizes filenames to remove invalid characters

## Pattern Matching & Data Extraction
- **Regex-based extraction**: Custom regex patterns for each document type
  - Extracts structured data (invoice numbers, dates, values, process numbers)
  - Template configurations stored in session state dictionary
  - Predefined templates for common document types with extensibility for custom patterns

## File Management
- **Temporary file handling**: tempfile module for OCR processing
  - Creates temporary PDFs for PyMuPDF/Tesseract processing
  - Automatic cleanup in finally blocks
  - No disk persistence of uploaded files
  
- **State Management**: Dual storage architecture
  - **Streamlit session_state**: Binary PDF content, processing results with bytes
  - **JSON persistence** (data/batches.json): Batch metadata, status, file lists (no binary)
  - Prevents JSON serialization errors while maintaining persistence across reruns
  
- **Batch Processing**: Automatic chunking for large-scale operations
  - Divides uploads into batches of 50 PDFs (configurable)
  - Independent processing and download per batch
  - Progress tracking and error isolation per batch
  - ZIP export for each completed batch

## Data Display
- **Pandas DataFrames**: Displays processing results in tabular format
  - Shows original filename, extracted data, and new filename
  - Enables easy review before downloading

# External Dependencies

## Core Libraries
- **Streamlit**: Web application framework and UI components
- **Pytesseract**: OCR engine wrapper (requires Tesseract binary installation)
- **pdf2image**: PDF to image conversion (requires Poppler binary)
- **PyPDF2**: PDF text extraction and manipulation
- **Pillow (PIL)**: Image processing and manipulation

## System Dependencies
- **Tesseract OCR**: Binary installation required on system
- **Poppler**: Binary utilities for PDF rendering (required by pdf2image)

## Standard Library
- **re**: Regular expression operations for pattern matching
- **zipfile**: Creating ZIP archives for batch downloads
- **io**: In-memory file operations
- **tempfile**: Temporary file and directory management
- **shutil**: High-level file operations
- **datetime**: Date/time handling for extracted data and filenames
- **pathlib**: Object-oriented filesystem paths
- **os**: Operating system interfaces

## Data Processing
- **Pandas**: Tabular data display and manipulation