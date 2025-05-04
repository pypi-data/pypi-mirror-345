#!/usr/bin/env python3
import os
import sys
import glob
import time
from mistralai import Mistral
from .utils import load_environment_variables, ensure_info_folder

def pdf_to_markdown(pdf_path, output_path=None, api_key=None, quiet=False):
    """
    Convert a PDF file to markdown using Mistral API.
    
    Args:
        pdf_path (str): Path to the PDF file
        output_path (str, optional): Path to save the markdown file. If None, 
                                    will use the PDF filename with .md extension.
        api_key (str, optional): Mistral API key. If None, will try to get it from
                                environment variable MISTRAL_API_KEY.
        quiet (bool, optional): If True, suppress detailed output
    
    Returns:
        str: Path to the generated markdown file
    """
    if not quiet:
        print(f"Processing PDF: {pdf_path}")
    
    # Get API key from environment if not provided
    if api_key is None:
        api_key = os.environ.get("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("Mistral API key not provided and not found in environment variable MISTRAL_API_KEY")
    
    # Initialize Mistral client
    client = Mistral(api_key=api_key)
    
    # If output path is not specified, use the PDF filename with .md extension
    if output_path is None:
        output_path = os.path.splitext(pdf_path)[0] + ".md"
    
    # Check if file exists
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    if not quiet:
        print("Uploading PDF to Mistral API...")
    # Upload the PDF file
    with open(pdf_path, "rb") as f:
        uploaded_pdf = client.files.upload(
            file={
                "file_name": os.path.basename(pdf_path),
                "content": f.read(),
            },
            purpose="ocr"
        )
    
    # Get signed URL
    signed_url = client.files.get_signed_url(file_id=uploaded_pdf.id)
    
    if not quiet:
        print("Running OCR on the PDF...")
    # Process the PDF with OCR
    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": signed_url.url
        }
    )
    
    if not quiet:
        print("Converting to markdown...")
    # Extract markdown content
    markdown_content = ""
    
    for i, page in enumerate(ocr_response.pages, 1):
        markdown_content += f"# Page {i}\n\n"
        # Check if the page has a markdown attribute
        if hasattr(page, 'markdown'):
            markdown_content += page.markdown + "\n\n"
        else:
            # Try to access the text content in a different way
            if not quiet:
                print(f"Page attributes: {dir(page)}")
            # If there's no markdown attribute, try to use the text content
            if hasattr(page, 'text'):
                markdown_content += page.text + "\n\n"
            else:
                print(f"Warning: Could not extract text from page {i}")
                # Try to convert the page object to a string or dictionary
                try:
                    page_dict = page.to_dict() if hasattr(page, 'to_dict') else str(page)
                    print(f"Page content: {page_dict}")
                    markdown_content += f"Could not extract text from this page. Raw content: {page_dict}\n\n"
                except Exception as e:
                    print(f"Error converting page to string or dict: {e}")
                    markdown_content += "Could not extract text from this page.\n\n"
    
    # Write the markdown content to a file
    with open(output_path, "w") as f:
        f.write(markdown_content)
    
    if not quiet:
        print(f"Markdown file saved to: {output_path}")
    return output_path

def process_directory(directory_path, api_key=None):
    """
    Process all PDF files in a directory and convert them to individual markdown files.
    
    Args:
        directory_path (str): Path to the directory containing PDF files
        api_key (str, optional): Mistral API key
    
    Returns:
        list: List of paths to the generated markdown files
    """
    # Get all PDF files in the directory
    pdf_files = glob.glob(os.path.join(directory_path, "*.pdf"))
    pdf_files.sort()  # Sort files alphabetically
    
    if not pdf_files:
        print(f"No PDF files found in {directory_path}")
        # Return an empty list but don't stop the process
        return []
    
    print(f"Found {len(pdf_files)} PDF files in {directory_path}")
    
    # Process each PDF file
    markdown_files = []
    for pdf_file in pdf_files:
        try:
            # Convert PDF to markdown
            markdown_file = pdf_to_markdown(pdf_file, api_key=api_key)
            markdown_files.append(markdown_file)
            # Add a small delay to avoid rate limiting
            time.sleep(2)
        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")
    
    return markdown_files

def process_project_pdfs(project_path, api_key=None, quiet=False):
    """
    Process all PDF files in the 'info' folder of a project and include any existing markdown files.
    
    Args:
        project_path (str): Path to the project folder
        api_key (str, optional): Mistral API key
        quiet (bool, optional): If True, suppress detailed output
    
    Returns:
        list: List of paths to all markdown files (both existing and newly generated)
    """
    info_folder = os.path.join(project_path, "info")
    
    # Check if the info folder exists
    if not os.path.exists(info_folder) or not os.path.isdir(info_folder):
        print(f"Error: 'info' folder not found in {project_path}")
        return []
    
    # Get all files in the info folder
    all_files = os.listdir(info_folder)
    if not all_files:
        if not quiet:
            print(f"Error: No files found in the 'info' folder of {project_path}")
        return []
    
    # Get existing markdown files
    existing_md_files = glob.glob(os.path.join(info_folder, "*.md"))
    
    # Get PDF files
    pdf_files = glob.glob(os.path.join(info_folder, "*.pdf"))
    
    # Convert PDF files to markdown if they exist
    new_md_files = []
    if pdf_files:
        if not quiet:
            print(f"Converting {len(pdf_files)} PDF files to markdown...")
        for pdf_file in pdf_files:
            try:
                # Convert PDF to markdown
                markdown_file = pdf_to_markdown(pdf_file, api_key=api_key, quiet=quiet)
                new_md_files.append(markdown_file)
                # Add a small delay to avoid rate limiting
                time.sleep(2)
            except Exception as e:
                if not quiet:
                    print(f"Error processing {pdf_file}: {e}")
    
    # Combine existing and new markdown files
    all_md_files = existing_md_files + [f for f in new_md_files if f not in existing_md_files]
    
    # Print summary if not in quiet mode
    if not quiet:
        if existing_md_files:
            print(f"Found {len(existing_md_files)} existing markdown files in {info_folder}")
        if new_md_files:
            print(f"Generated {len(new_md_files)} new markdown files from PDFs")
        print(f"Total of {len(all_md_files)} markdown files available for processing")
    
    return all_md_files
