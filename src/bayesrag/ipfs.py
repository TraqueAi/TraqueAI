import os
import zipfile
import ipfshttpclient
import time
from loguru import logger
from bayesrag.config import download_path, extract_to_path, directory_path, zip_file_path, IPFS_RETRY_LIMIT, IPFS_RETRY_DELAY


class IPFSManager:
    def __init__(self, ipfs_address=None, retry_limit=IPFS_RETRY_LIMIT, retry_delay=IPFS_RETRY_DELAY):

        self.ipfs_address = ipfs_address or os.getenv('IPFS_ADDRESS', '/ip4/127.0.0.1/tcp/5001/http')
        self.retry_limit = retry_limit
        self.retry_delay = retry_delay
        self.client = self._connect_to_ipfs(self.ipfs_address)
    
    def _connect_to_ipfs(self, ipfs_address):
        """Connect to the IPFS client with retry logic."""
        for attempt in range(self.retry_limit):
            try:
                ipfs_conn_obj = ipfshttpclient.connect(ipfs_address)
                logger.info("Connected to IPFS")
                return ipfs_conn_obj
            except Exception as e:
                logger.error(f"Error during IPFS connection attempt {attempt + 1}/{self.retry_limit}: {e}")
                if attempt < self.retry_limit - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.critical("Unable to connect to IPFS after multiple attempts.")
                    raise
    
    def _validate_path(self, path, path_type="directory"):
        """Validate the existence of a file or directory."""
        if path_type == "directory" and not os.path.isdir(path):
            logger.error(f"Directory {path} does not exist or is not accessible.")
            raise FileNotFoundError(f"Directory {path} not found.")
        elif path_type == "file" and not os.path.isfile(path):
            logger.error(f"File {path} does not exist or is not accessible.")
            raise FileNotFoundError(f"File {path} not found.")

    def _zip_directory(self, directory_path, zip_file_path):
        """Compress a directory into a zip file."""
        self._validate_path(directory_path, "directory")
        
        logger.info(f"Creating zip file at: {zip_file_path}")
        try:
            with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(directory_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.relpath(file_path, directory_path))
            logger.info(f"Zip file created successfully: {zip_file_path}")
            return zip_file_path
        except Exception as e:
            logger.error(f"Error while zipping directory: {e}")
            raise

    def _unzip_file(self, zip_file_path, extract_to_path):
        """Extract a zip file to a specific directory."""
        self._validate_path(zip_file_path, "file")
        
        logger.info(f"Unzipping file: {zip_file_path} to {extract_to_path}")
        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to_path)
            logger.info(f"Unzipped file successfully to: {extract_to_path}")
        except Exception as e:
            logger.error(f"Error while unzipping file: {e}")
            raise

    def upload_directory(self, directory_path=directory_path):
        """Automatically zip and upload a directory to IPFS."""
        logger.info(f"Zipping and uploading directory: {directory_path}")
        try:
            zip_file = self._zip_directory(directory_path, zip_file_path)
            return self.upload_file(zip_file)
        except Exception as e:
            logger.error(f"Error during upload: {e}")
            return None

    def upload_file(self, file_path):
        """Upload a file to IPFS."""
        self._validate_path(file_path, "file")
        
        for attempt in range(self.retry_limit):
            try:
                logger.info(f"Uploading file: {file_path}")
                result = self.client.add(file_path)
                logger.info(f"Upload successful. IPFS result: {result}")
                return result
            except Exception as e:
                logger.error(f"Error during file upload attempt {attempt + 1}/{self.retry_limit}: {e}")
                if attempt < self.retry_limit - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.critical("Failed to upload file after multiple attempts.")
                    return None

    def download_and_extract(self, file_hash, download_path, extract_to_path):
        """Download a zip file from IPFS and extract its contents."""
        logger.info(f"Starting download of IPFS hash: {file_hash}")
        
        os.makedirs(os.path.dirname(download_path), exist_ok=True)
        
        for attempt in range(self.retry_limit):
            try:
                file_content = self.client.cat(file_hash)
                with open(download_path, 'wb') as file:
                    file.write(file_content)
                logger.info(f"Downloaded and saved file: {download_path}")
                
                # Unzip the downloaded file
                self._unzip_file(download_path, extract_to_path)
                return
            except Exception as e:
                logger.error(f"Error during download attempt {attempt + 1}/{self.retry_limit}: {e}")
                if attempt < self.retry_limit - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.critical("Failed to download and extract file after multiple attempts.")
                    return None


# Usage example (to be run only in a non-production environment):
if __name__ == "__main__":
    # Initialize IPFSManager with a retry limit and delay
    ipfs_manager = IPFSManager()

    # Zip and upload directory
    upload_result = ipfs_manager.upload_directory(directory_path)

    # If upload was successful, download and extract the file
    if upload_result:
        file_hash = upload_result['Hash']
        ipfs_manager.download_and_extract(file_hash, download_path, extract_to_path)
    else:
        logger.critical("Upload failed, no file to download.")
