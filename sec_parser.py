import os
import re
from sec_edgar_downloader import Downloader
from bs4 import BeautifulSoup
from datetime import datetime

class SECParser:
    """
    Parser for SEC 10-K filings
    Downloads and extracts key sections from EDGAR
    """
    
    def __init__(self, download_folder="sec_filings"):
        """Initialize downloader"""
        self.download_folder = download_folder
        self.dl = Downloader("YourCompanyName", "your.email@example.com", download_folder)
    
    def get_latest_10k(self, ticker):
        """
        Download the most recent 10-K filing for a company
        Returns: dict with filing info and file path
        """
        try:
            # Download latest 10-K
            self.dl.get("10-K", ticker, limit=1)
            
            # Find the downloaded file
            company_folder = os.path.join(self.download_folder, "sec-edgar-filings", ticker, "10-K")
            
            # Get most recent filing
            filing_folders = [f for f in os.listdir(company_folder) if os.path.isdir(os.path.join(company_folder, f))]
            if not filing_folders:
                return {"error": f"No 10-K filings found for {ticker}"}
            
            latest_filing = sorted(filing_folders)[-1]
            filing_path = os.path.join(company_folder, latest_filing)
            
            # Check if we need to extract from full-submission.txt
            submission_file = os.path.join(filing_path, 'full-submission.txt')
            
            if os.path.exists(submission_file):
                # Extract the actual document from the submission wrapper
                print(f"    [Debug] Extracting document from submission file...")
                document_content = self.extract_document_from_submission(submission_file)
                
                if document_content:
                    # Save extracted content to a temporary file
                    extracted_file = os.path.join(filing_path, 'extracted_10k.html')
                    with open(extracted_file, 'w', encoding='utf-8', errors='ignore') as f:
                        f.write(document_content)
                    
                    filing_file = extracted_file
                    print(f"    [Debug] Extracted {len(document_content)/1024:.1f} KB of content")
                else:
                    filing_file = submission_file
            else:
                # Look for other files
                all_files = [f for f in os.listdir(filing_path) if f.endswith(('.htm', '.html', '.txt'))]
                if all_files:
                    filing_file = os.path.join(filing_path, all_files[0])
                else:
                    return {"error": "No readable filing found"}
            
            return {
                "ticker": ticker.upper(),
                "filing_date": latest_filing,
                "file_path": filing_file,
                "filing_type": "10-K"
            }
            
        except Exception as e:
            return {"error": f"Error downloading 10-K: {str(e)}"}
    
    def extract_document_from_submission(self, submission_path):
        """
        Extract the primary 10-K document from full-submission.txt
        The submission file is SGML format with the actual document embedded
        """
        try:
            with open(submission_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # The actual document is between <DOCUMENT> tags
            pattern = r'<DOCUMENT>(.*?)</DOCUMENT>'
            documents = re.findall(pattern, content, re.DOTALL)
            
            if not documents:
                return None
            
            # Find the largest document (usually the primary 10-K)
            largest_doc = max(documents, key=len)
            
            # The HTML content is after <TEXT> tag
            text_match = re.search(r'<TEXT>(.*?)(?:</TEXT>|$)', largest_doc, re.DOTALL)
            if text_match:
                return text_match.group(1)
            
            return largest_doc
            
        except Exception as e:
            print(f"Error extracting document: {str(e)}")
            return None
    
    def extract_risk_factors(self, file_path):
        """
        Extract Item 1A - Risk Factors section
        Returns: cleaned text of risk factors
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'lxml')
            text = soup.get_text()
            
            # Find ALL occurrences of "Item 1A" - first is usually table of contents
            all_matches = []
            for match in re.finditer(r'Item 1A', text, re.IGNORECASE):
                all_matches.append(match.start())
            
            if len(all_matches) < 2:
                return "Could not find Risk Factors section (only found table of contents)"
            
            # Use the SECOND occurrence (skip table of contents)
            start_pos = all_matches[1]
            
            # Find where Item 1B starts (after the second Item 1A)
            item_1b_match = re.search(r'Item 1B', text[start_pos:], re.IGNORECASE)
            if not item_1b_match:
                return "Could not find end of Risk Factors section"
            
            end_pos = start_pos + item_1b_match.start()
            
            # Extract the risk factors text
            risk_text = text[start_pos:end_pos]
            
            # Clean it up
            risk_text = self._clean_text(risk_text)
            
            # Remove the header
            risk_text = re.sub(r'^Item 1A\.?\s*Risk Factors\s*', '', risk_text, flags=re.IGNORECASE)
            
            print(f"    [Debug] Extracted from position {start_pos} to {end_pos}")
            
            if len(risk_text) > 1000:
                return risk_text[:15000]
            else:
                return "Risk Factors section appears too short after extraction."
                
        except Exception as e:
            return f"Error extracting risk factors: {str(e)}"
    
    def extract_mda(self, file_path):
        """
        Extract Item 7 - Management's Discussion and Analysis
        Returns: cleaned text of MD&A
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'lxml')
            text = soup.get_text()
            
            # Find ALL occurrences of "Item 7" - skip table of contents
            all_matches = []
            for match in re.finditer(r'Item 7[^A]', text, re.IGNORECASE):
                all_matches.append(match.start())
            
            if len(all_matches) < 2:
                return "Could not find MD&A section"
            
            # Use the SECOND occurrence
            start_pos = all_matches[1]
            
            # Find where Item 7A starts
            item_7a_match = re.search(r'Item 7A', text[start_pos:], re.IGNORECASE)
            if not item_7a_match:
                # Try Item 8 as fallback
                item_7a_match = re.search(r'Item 8', text[start_pos:], re.IGNORECASE)
            
            if not item_7a_match:
                return "Could not find end of MD&A section"
            
            end_pos = start_pos + item_7a_match.start()
            
            # Extract MD&A text
            mda_text = text[start_pos:end_pos]
            
            # Clean it up
            mda_text = self._clean_text(mda_text)
            
            # Remove the header
            mda_text = re.sub(r'^Item 7\..*?(?:Results of Operations)\s*', '', mda_text, flags=re.IGNORECASE)
            
            print(f"    [Debug] Extracted from position {start_pos} to {end_pos}")
            
            if len(mda_text) > 1000:
                return mda_text[:20000]
            else:
                return "MD&A section appears too short."
                
        except Exception as e:
            return f"Error extracting MD&A: {str(e)}"
    
    def _clean_text(self, text):
        """Clean extracted text"""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'Table of Contents', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\d+\s*$', '', text)
        text = ' '.join(text.split())
        return text.strip()
    
    def get_filing_metadata(self, file_path):
        """Extract metadata from filing"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'lxml')
            text = soup.get_text()
            
            fiscal_year = re.search(r'fiscal year ended?\s+(\w+\s+\d+,?\s+\d{4})', text, re.IGNORECASE)
            
            metadata = {
                "fiscal_year_end": fiscal_year.group(1) if fiscal_year else "Not found",
                "filing_size_kb": os.path.getsize(file_path) / 1024
            }
            
            return metadata
            
        except Exception as e:
            return {"error": str(e)}


# Test the parser
if __name__ == "__main__":
    print("Testing SEC Parser...")
    print("="*60)
    
    parser = SECParser()
    
    print("\n[1/4] Downloading NVDA 10-K...")
    filing_info = parser.get_latest_10k("NVDA")
    
    if "error" in filing_info:
        print(f"❌ Error: {filing_info['error']}")
    else:
        print(f"✅ Downloaded {filing_info['filing_type']}")
        print(f"    Ticker: {filing_info['ticker']}")
        print(f"    Filing Date: {filing_info['filing_date']}")
        
        print("\n[2/4] Extracting Risk Factors...")
        risks = parser.extract_risk_factors(filing_info['file_path'])
        print(f"✅ Extracted {len(risks)} characters")
        print(f"    Preview: {risks[:200]}...")
        
        print("\n[3/4] Extracting MD&A...")
        mda = parser.extract_mda(filing_info['file_path'])
        print(f"✅ Extracted {len(mda)} characters")
        print(f"    Preview: {mda[:200]}...")
        
        print("\n[4/4] Getting metadata...")
        metadata = parser.get_filing_metadata(filing_info['file_path'])
        print(f"✅ Metadata extracted")
        print(f"    Fiscal Year End: {metadata.get('fiscal_year_end', 'N/A')}")
    
    print("\n" + "="*60)
    print("SEC PARSER TEST COMPLETE ✅")
    print("="*60)