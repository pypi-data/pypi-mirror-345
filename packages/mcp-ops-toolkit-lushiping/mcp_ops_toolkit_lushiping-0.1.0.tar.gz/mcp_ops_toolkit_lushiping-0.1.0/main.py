from pathlib import Path
from mcp.server.fastmcp import FastMCP
import pandas as pd
import subprocess
import os

# Create an MCP server
mcp = FastMCP("Demo")

# Get FILE_PATH from environment variable, if not set, use user's home directory as default
# Example: 
#   - If FILE_PATH is set: FILE_PATH="/data/files" -> uses "/data/files"
#   - If FILE_PATH is not set: -> uses user's home directory (e.g., "/Users/username")
FILE_PATH = os.getenv("FILE_PATH", os.path.expanduser("~"))

# Add Excel to CSV conversion tool
@mcp.tool()
def excel_to_csv(filepath: str, sheet_name: str = None) -> str:
    """Convert Excel file sheet to CSV format
    
    Args:
        filepath: Path to the Excel file to convert (relative to FILE_PATH)
        sheet_name: Name of the sheet to convert, if None converts first sheet
        
    Returns:
        str: Result message indicating success or failure
    """
    try:
        # Convert filepath to absolute Path object using FILE_PATH
        excel_path = Path(FILE_PATH) / filepath
        if not excel_path.exists():
            raise ValueError(f"File {excel_path} not found")
            
        # Check if it's an Excel file
        if not excel_path.suffix.lower() in ['.xlsx', '.xls']:
            raise ValueError(f"File {excel_path} is not an Excel file")
            
        # Read Excel file
        if sheet_name:
            try:
                df = pd.read_excel(excel_path, sheet_name=sheet_name)
            except ValueError:
                # Get available sheet names
                available_sheets = pd.ExcelFile(excel_path).sheet_names
                raise ValueError(f"Sheet '{sheet_name}' not found. Available sheets: {', '.join(available_sheets)}")
        else:
            df = pd.read_excel(excel_path)  # Defaults to first sheet
            
        # Create CSV filename with sheet name if specified
        if sheet_name:
            csv_path = excel_path.with_name(f"{excel_path.stem}_{sheet_name}.csv")
        else:
            csv_path = excel_path.with_suffix('.csv')
        
        # Save to CSV
        df.to_csv(csv_path, index=False)
        
        return f"Successfully converted sheet '{sheet_name or 'first'}' from {excel_path.name} to {csv_path.name}"
    except Exception as e:
        raise ValueError(f"Error during conversion: {str(e)}")

# Add tool to open Wireshark
@mcp.tool()
def open_wireshark(pcap_file: str = None) -> str:
    """Open Wireshark application in a new window and optionally load a pcap file
    
    This tool launches Wireshark in multi-window mode, allowing multiple instances 
    of Wireshark to be opened simultaneously, each in its own window.
    
    Args:
        pcap_file: Optional path to a pcap file to open (relative to FILE_PATH), if None just opens Wireshark
        
    Returns:
        str: Result message indicating success or failure
    """
    try:
        wireshark_path = "/Applications/Wireshark.app"
        
        # Check if Wireshark is installed
        if not os.path.exists(wireshark_path):
            raise ValueError("Wireshark not found at /Applications/Wireshark.app")
            
        # Prepare command based on whether a pcap file is provided
        if pcap_file:
            # Convert pcap filepath to absolute Path object using FILE_PATH
            pcap_path = Path(FILE_PATH) / pcap_file
            if not pcap_path.exists():
                raise ValueError(f"PCAP file {pcap_path} not found")
                
            # Check if it's likely a pcap file
            if not pcap_path.suffix.lower() in ['.pcap', '.pcapng', '.cap']:
                raise ValueError(f"Warning: File {pcap_path} might not be a valid PCAP file, but attempting to open anyway")
                
            # Construct command with pcap file
            command = ["open", "-n", "-a", wireshark_path, str(pcap_path.absolute())]
            result_message = f"Opening Wireshark with PCAP file: {pcap_path}"
        else:
            # Just open Wireshark without a file
            command = ["open", "-n", "-a", wireshark_path]
            result_message = "Opening Wireshark"
            
        # Execute the command
        subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result_message
        
    except Exception as e:
        raise ValueError(f"Error opening Wireshark: {str(e)}")

if __name__ == "__main__":
    # Initialise and run the server
    mcp.run(transport='stdio')