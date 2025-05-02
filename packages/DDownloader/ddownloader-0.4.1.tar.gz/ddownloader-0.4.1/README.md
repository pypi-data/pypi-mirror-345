# DDownloader
_DDownloader is a powerful Python-based tool and library designed to download and decrypt DRM-protected content from DASH, HLS, and ISM manifests. It provides seamless support for encrypted media streams, extracting metadata and ensuring high compatibility with various DRM standards._

## Features
- **Download and Decrypt**: Supports DASH, HLS, and ISM manifests with seamless decryption using provided keys.
- **Automatic Detection**: Automatically detects manifest types (.mpd, .m3u8, .ism) and processes accordingly.
- **Media Information Extraction**: Extracts metadata (e.g., codec, resolution, duration) for .mp4 files and saves it in a `logs/` directory.
- **CLI and Library Support**: Flexible usage via command-line or Python library.
- **Detailed Logging**: Provides real-time progress and logs errors for debugging.

## Requirements

- **Python**: Version 3.7 or higher.
- **Required binaries**:
  
    - `N_m3u8DL-RE` for downloading protected DRM content.
    - `mp4decrypt` for decrypting protected media files.
    - `ffmpeg` for re-encoding and muxer method
    - a proper environment variable configuration for binaries.

##  Installation
- Install `DDownloader` using pip:
  
	```bash
	pip install DDownloader
	```

##  Usage
- Download Content:
  
	```python
	from DDownloader.modules.downloader import DOWNLOADER

	downloader = DOWNLOADER()
	downloader.manifest_url = "https://example.com/path/to/manifest"  # DASH, HLS, or ISM manifest URL
	downloader.output_name = "output.mp4"  # Desired output file name
	downloader.decryption_keys = ["12345:678910"]  # Provide decryption keys if needed
	downloader.download()  # Start the downloading and decryption process
	```
 
- Extract Media Information:
  
	```python
	from DDownloader.modules.helper import get_media_info

	file_path = "downloads/example.mp4"
	media_info = get_media_info(file_path)
	print(media_info)
	```

- Re-encoding:

	```python
	from DDownloader.modules.downloader import DOWNLOADER

 	re_encode = DOWNLOADER()
	quality = ["HD", "FHD", "UHD"]
	input_content = "downloads/example.mp4"
	output_content = "/path/to/output.mp4"
 	re_encode.re_encode_content(input_file=input_content,quality=quality,codec="libx265",crf=20,preset="medium")
	```
  
## CLI Usage
- Download Media
  
	```bash
	DDownloader -u https://example.com/path/to/manifest -o output.mp4
	```
 
- Specify Decryption Keys
  
	```bash
	DDownloader -u https://example.com/path/to/manifest -o output.mp4 -k 12345:678910
	```

- Re-encoding

	```bash
 	DDownloader -i "input.mp4" -o "output.mp4" -q "HD, FHD, UHD"
 	```


- Display Help
  
	```bash
	DDownloader -h
	```

- ![image](https://github.com/user-attachments/assets/8c73a79e-fcac-4bde-a07c-5628db0d19df)
