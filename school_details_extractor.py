from bs4 import BeautifulSoup
import json
import requests
import time

def extract_school_details_from_html(html_content):
    """Extract detailed school information from school detail page"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the schooldetails div
    school_details_div = soup.find('div', id='schooldetails')
    
    if not school_details_div:
        return None
    
    # Find the table within the div
    table = school_details_div.find('table')
    
    if not table:
        return None
    
    school_data = {}
    
    # Extract all rows from the table
    rows = table.find_all('tr')
    
    for row in rows:
        cells = row.find_all('td')
        
        # Skip if not exactly 2 cells
        if len(cells) != 2:
            continue
        
        # Get field name and value
        field_name = cells[0].get_text(strip=True)
        field_value = cells[1].get_text(strip=True)
        
        # Clean field name - remove extra spaces and convert to lowercase with underscores
        field_key = field_name.lower().replace(' ', '_').replace('/', '_')
        
        # Store in dictionary
        school_data[field_key] = field_value
    
    return school_data

def extract_school_details_from_url(url):
    """Fetch school detail page and extract information"""
    try:
        print(f"Fetching: {url}")
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        school_details = extract_school_details_from_html(response.text)
        
        if school_details:
            # Add the URL to the data
            school_details['url'] = url
            print(f"✓ Extracted {len(school_details)} fields")
            return school_details
        else:
            print("✗ No school details found")
            return None
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def extract_school_details_from_file(file_path):
    """Extract school details from local HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        school_details = extract_school_details_from_html(html_content)
        
        if school_details:
            print(f"✓ Extracted {len(school_details)} fields from local file")
            return school_details
        else:
            print("✗ No school details found in local file")
            return None
            
    except Exception as e:
        print(f"✗ Error reading file: {e}")
        return None

def save_to_json(data, output_file='school_details_output.json'):
    """Save school details to JSON file"""
    try:
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=2, ensure_ascii=False)
        print(f"\n✓ Data saved to: {output_file}")
        return True
    except Exception as e:
        print(f"\n✗ Error saving data: {e}")
        return False

def main():
    print("="*70)
    print("SCHOOL DETAILS EXTRACTOR")
    print("="*70)
    
    # Test with local file first
    print("\nTesting with local file: school_details.html")
    school_data = extract_school_details_from_file('school_details.html')
    
    if school_data:
        # Display extracted data
        print("\n" + "="*70)
        print("EXTRACTED SCHOOL DETAILS:")
        print("="*70)
        for key, value in school_data.items():
            print(f"{key}: {value}")
        
        # Save to JSON
        save_to_json(school_data, 'school_details_output.json')
        
        print("\n" + "="*70)
        print("EXTRACTION COMPLETE!")
        print("="*70)
    else:
        print("\nFailed to extract school details from local file")
    
    # Ask if user wants to test with a URL
    print("\n" + "="*70)
    user_input = input("\nDo you want to test with a URL? (yes/no): ").lower()
    
    if user_input == 'yes':
        url = input("Enter school detail page URL: ").strip()
        if url:
            school_data_url = extract_school_details_from_url(url)
            if school_data_url:
                print("\n" + "="*70)
                print("EXTRACTED SCHOOL DETAILS FROM URL:")
                print("="*70)
                for key, value in school_data_url.items():
                    print(f"{key}: {value}")
                
                save_to_json(school_data_url, 'school_details_from_url.json')

if __name__ == "__main__":
    main()
