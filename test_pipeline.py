import requests
import time
import sys
import os

BASE_URL = "http://localhost:8000/api"
FILE_PATH = "/Users/kaffan/.gemini/antigravity/brain/80daed99-e569-4cbc-af3f-5c0099f736bf/uploaded_image_1763768356787.png"

def test_pipeline():
    print(f"Testing pipeline with file: {FILE_PATH}")
    
    # 1. Upload
    print("\n[1] Testing /api/upload...")
    if not os.path.exists(FILE_PATH):
        print(f"Error: File not found at {FILE_PATH}")
        return

    with open(FILE_PATH, 'rb') as f:
        files = {'file': ('test_image.png', f, 'image/png')}
        try:
            response = requests.post(f"{BASE_URL}/upload", files=files)
            response.raise_for_status()
            data = response.json()
            doc_id = data['id']
            print(f"✅ Upload Successful! Document ID: {doc_id}")
            print(f"   Filename: {data['filename']}")
            print(f"   Content Type: {data['mime_type']}")
        except Exception as e:
            print(f"❌ Upload Failed: {e}")
            print(response.text)
            return

    # 2. Run Task
    print("\n[2] Testing /api/run_task (Task: summary)...")
    payload = {
        "task_type": "summary",
        "document_ids": [doc_id],
        "instructions": "Provide a brief summary of this document."
    }
    
    try:
        response = requests.post(f"{BASE_URL}/run_task", json=payload)
        response.raise_for_status()
        task_data = response.json()
        task_id = task_data['id']
        print(f"✅ Task Started! Task ID: {task_id}")
    except Exception as e:
        print(f"❌ Task Start Failed: {e}")
        print(response.text)
        return

    # 3. Poll Results
    print("\n[3] Polling /api/tasks/{id} for results...")
    start_time = time.time()
    while True:
        try:
            response = requests.get(f"{BASE_URL}/tasks/{task_id}")
            response.raise_for_status()
            result = response.json()
            status = result['status']
            
            if status == 'completed':
                print(f"✅ Task Completed in {time.time() - start_time:.2f}s!")
                print("\n--- Result Output ---")
                print(result['result'])
                print("---------------------")
                break
            elif status == 'failed':
                print(f"❌ Task Failed: {result.get('error')}")
                break
            else:
                print(f"   Status: {status}...")
                time.sleep(2)
                
            if time.time() - start_time > 60:
                print("❌ Timeout waiting for task completion.")
                break
        except Exception as e:
            print(f"❌ Polling Failed: {e}")
            break

if __name__ == "__main__":
    test_pipeline()
