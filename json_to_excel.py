import json
import pandas as pd
from datetime import datetime

def json_to_excel(json_file, excel_file=None, sheet_name='Schools'):
    """
    Convert JSON file to Excel format
    
    Args:
        json_file: Path to input JSON file
        excel_file: Path to output Excel file (optional)
        sheet_name: Name of the Excel sheet
    """
    try:
        # Read JSON file
        print(f"Reading JSON file: {json_file}")
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✓ Loaded {len(data)} records")
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Generate output filename if not provided
        if not excel_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            excel_file = json_file.replace('.json', f'_{timestamp}.xlsx')
        
        # Save to Excel
        print(f"Saving to Excel: {excel_file}")
        df.to_excel(excel_file, sheet_name=sheet_name, index=False, engine='openpyxl')
        
        print(f"✓ Successfully saved {len(df)} rows and {len(df.columns)} columns to Excel")
        print(f"✓ Output file: {excel_file}")
        
        # Display summary
        print("\n" + "="*70)
        print("EXCEL CONVERSION SUMMARY")
        print("="*70)
        print(f"Total records: {len(df)}")
        print(f"Total columns: {len(df.columns)}")
        print(f"\nColumns: {', '.join(df.columns.tolist())}")
        
        return excel_file
        
    except Exception as e:
        print(f"✗ Error converting JSON to Excel: {e}")
        return None

def main():
    print("="*70)
    print("JSON TO EXCEL CONVERTER")
    print("="*70)
    
    # Ask for input file
    json_file = input("\nEnter JSON file name (default: progress_checkpoint.json): ").strip()
    if not json_file:
        json_file = 'progress_checkpoint.json'
    
    # Ask for output file
    excel_file = input("Enter Excel file name (press Enter for auto-generated): ").strip()
    if not excel_file:
        excel_file = None
    
    # Ask for sheet name
    sheet_name = input("Enter sheet name (default: Schools): ").strip()
    if not sheet_name:
        sheet_name = 'Schools'
    
    print("\n" + "="*70)
    
    # Convert
    result = json_to_excel(json_file, excel_file, sheet_name)
    
    if result:
        print("\n" + "="*70)
        print("CONVERSION COMPLETE!")
        print("="*70)
    else:
        print("\nConversion failed!")

if __name__ == "__main__":
    main()
