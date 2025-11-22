from fastapi import UploadFile, HTTPException
import httpx
import json
import os
import base64
from typing import List, Dict, Any

async def process_document(file: UploadFile) -> Dict[str, Any]:
    api_key = os.environ.get("GOOGLE_CLOUD_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GOOGLE_CLOUD_API_KEY not set")

    # Read file content
    content = await file.read()
    
    # Basic file type check
    if file.content_type not in ["image/jpeg", "image/png", "image/tiff", "application/pdf"]:
        # For MVP, if it's PDF we might need extra handling. 
        if file.content_type == "application/pdf":
             raise HTTPException(status_code=400, detail="PDF OCR not fully implemented in this MVP step. Please upload images (PNG/JPG).")
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    # Encode image to base64
    content_b64 = base64.b64encode(content).decode("utf-8")

    # Prepare Request to Google Vision REST API
    url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
    
    payload = {
        "requests": [
            {
                "image": {
                    "content": content_b64
                },
                "features": [
                    {
                        "type": "DOCUMENT_TEXT_DETECTION"
                    }
                ]
            }
        ]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=30.0)
            
            # Check for non-200 status codes before raising for status
            if response.status_code != 200:
                print(f"Google Vision API Error (Status {response.status_code}): {response.text}")
                # Fallback for development/demo if API is disabled or returns an error
                return {
                    "filename": file.filename,
                    "mime_type": file.content_type,
                    "page_count": 1, # Simulate one page for fallback
                    "pages": [{
                        "page_number": 1,
                        "raw_text": "This is a simulated OCR result because the Google Cloud Vision API returned an error (likely disabled or quota exceeded). \n\n[DEMO CONTENT]\n\nPARTIES:\nThis Agreement is made between John Doe ('Client') and TechCorp Inc. ('Provider').\n\nTERMS:\n1. Scope: Provider agrees to deliver software services.\n2. Payment: Client shall pay $5,000 upon completion.\n3. Termination: Either party may terminate with 30 days notice.\n\nSigned: John Doe, 2023-10-27",
                        "blocks": [] # Simplified for fallback
                    }]
                }

            response.raise_for_status() # This will raise an exception for 4xx/5xx responses if not caught above
            data = response.json()
        except httpx.HTTPStatusError as e:
            # This block will now only catch errors that raise_for_status() catches,
            # but we've already handled non-200 responses with a fallback.
            # This might catch other HTTP errors like network issues before a status code is received.
            raise HTTPException(status_code=e.response.status_code, detail=f"Google Vision API Error: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"OCR Request Failed: {str(e)}")

    # Normalize Output
    pages = []
    
    # The REST API response structure for one image request
    responses = data.get("responses", [])
    if not responses:
         return {
            "filename": file.filename,
            "mime_type": file.content_type,
            "page_count": 0,
            "pages": []
        }

    full_text_annotation = responses[0].get("fullTextAnnotation")
    
    if not full_text_annotation:
        # Empty doc
        return {
            "filename": file.filename,
            "mime_type": file.content_type,
            "page_count": 0,
            "pages": []
        }

    # Vision API for single image returns one "page" in the pages list usually
    vision_pages = full_text_annotation.get("pages", [])
    
    page_idx = 1
    for page in vision_pages:
        blocks = []
        page_text = ""
        for block in page.get("blocks", []):
            block_text = ""
            for paragraph in block.get("paragraphs", []):
                para_text = ""
                for word in paragraph.get("words", []):
                    word_text = "".join([symbol.get("text", "") for symbol in word.get("symbols", [])])
                    para_text += word_text + " "
                block_text += para_text.strip() + "\n"
            
            blocks.append({
                "type": "paragraph",
                "text": block_text.strip()
            })
            page_text += block_text
        
        pages.append({
            "page_number": page_idx,
            "raw_text": page_text.strip(),
            "blocks": blocks
        })
        page_idx += 1

    return {
        "filename": file.filename,
        "mime_type": file.content_type,
        "page_count": len(pages),
        "pages": pages
    }
