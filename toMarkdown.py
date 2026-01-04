import requests
import zipfile
import os
import tempfile
from typing import Optional
def get_url(file_path):
    token = ""
    url = "https://mineru.net/api/v4/extract/task"
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    data = {
        "url": file_path,
        "model_version": "vlm"
    }

    res = requests.post(url,headers=header,json=data)
    print(res.status_code)
    print(res.json())
    print(res.json()["data"])
    task_id = res.json()["data"]["task_id"]
    url = f"https://mineru.net/api/v4/extract/task/{task_id}"
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    while True:
        res = requests.get(url, headers=header)
        print(res.status_code)
        if res.json()["data"]["state"] != "pending":
            print(res.json()["data"]["full_zip_url"])
            return res.json()["data"]["full_zip_url"]
        print("waiting for result...")        






def download_and_extract_full_md(zip_url: str, temp_dir: str) -> Optional[str]:
    """Download ZIP file, extract full.md, return path to full.md"""
    zip_file_path = os.path.join(temp_dir, "mineru_download.zip")
    try:
        with requests.get(zip_url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(zip_file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        # Check if ZIP file is valid
        if not zipfile.is_zipfile(zip_file_path):
            print("Downloaded file is not a valid ZIP")
            return None

        # Extract full.md from ZIP
        print(f"Extracting full.md from ZIP...")
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            # Find full.md in the ZIP (case-insensitive)
            full_md_paths = [
                name for name in zip_ref.namelist()
                if name.lower().endswith("full.md")
            ]

            if not full_md_paths:
                print("full.md not found in ZIP file")
                return None

            # Extract the first full.md found (adjust if multiple exist)
            full_md_path_in_zip = full_md_paths[0]
            zip_ref.extract(full_md_path_in_zip, temp_dir)

            full_md_abs_path = os.path.join(temp_dir, full_md_path_in_zip)
            print(f"Extracted full.md to: {full_md_abs_path}")
             # Clean up ZIP file
        os.remove(zip_file_path) 
        return full_md_abs_path

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to download ZIP: {str(e)}")
        return None
    except zipfile.BadZipFile as e:
        print(f"❌ Invalid ZIP file: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ Extraction failed: {str(e)}")
        return None


file_path = "https://cdn-mineru.openxlab.org.cn/demo/example.pdf"
zip_url = get_url(file_path)

download_and_extract_full_md(zip_url, '.\\temp')
