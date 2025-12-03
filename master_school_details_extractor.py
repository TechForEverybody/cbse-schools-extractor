from bs4 import BeautifulSoup
import json
import requests
import time
from datetime import datetime
import os

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

def fetch_school_details(url, retry_count=3):
    """Fetch school detail page and extract information with retry logic"""
    for attempt in range(retry_count):
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            school_details = extract_school_details_from_html(response.text)
            return school_details
            
        except Exception as e:
            if attempt < retry_count - 1:
                time.sleep(2)  # Wait before retry
                continue
            else:
                print(f"    ✗ Failed after {retry_count} attempts: {e}")
                return None

def load_schools_data(file_path='SchoolsData.json'):
    """Load schools data from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            schools = json.load(file)
        print(f"✓ Loaded {len(schools)} schools from {file_path}")
        return schools
    except Exception as e:
        print(f"✗ Error loading schools data: {e}")
        return []

def save_schools_data(schools, output_file='SchoolsData_Complete.json'):
    """Save complete schools data to JSON file"""
    try:
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(schools, json_file, indent=2, ensure_ascii=False)
        print(f"✓ Data saved to: {output_file}")
        return True
    except Exception as e:
        print(f"✗ Error saving data: {e}")
        return False

def save_progress(schools, progress_file='progress_checkpoint.json'):
    """Save progress checkpoint"""
    try:
        with open(progress_file, 'w', encoding='utf-8') as json_file:
            json.dump(schools, json_file, indent=2, ensure_ascii=False)
        return True
    except:
        return False

def main():
    print("="*80)
    print("MASTER SCHOOL DETAILS EXTRACTOR")
    print("Fetching detailed information for all schools")
    print("="*80)
    
    # Load schools data
    schools = load_schools_data('SchoolsData.json')
    
    if not schools:
        print("No schools data found. Exiting...")
        return
    
    # Ask user for configuration
    print(f"\nTotal schools to process: {len(schools)}")
    
    start_input = input("Enter starting index (press Enter for 0): ").strip()
    start_idx = int(start_input) if start_input else 0
    
    limit_input = input(f"Enter number of schools to process (press Enter for all from {start_idx}): ").strip()
    if limit_input:
        end_idx = start_idx + int(limit_input)
    else:
        end_idx = len(schools)
    
    delay_input = input("Enter delay between requests in seconds (default 2): ").strip()
    delay = float(delay_input) if delay_input else 2.0
    
    save_interval_input = input("Save progress every N schools (default 50): ").strip()
    save_interval = int(save_interval_input) if save_interval_input else 50
    
    print("\n" + "="*80)
    print(f"Starting extraction from index {start_idx} to {end_idx}")
    print(f"Delay between requests: {delay} seconds")
    print(f"Progress checkpoint every: {save_interval} schools")
    print("="*80 + "\n")
    
    start_time = datetime.now()
    
    # Process each school
    success_count = 0
    fail_count = 0
    already_processed = 0
    
    for idx in range(start_idx, min(end_idx, len(schools))):
        school = schools[idx]
        
        # Check if already processed (has detailed fields)
        if 'affiliate_id' in school or 'affiliation_id' in school:
            already_processed += 1
            print(f"[{idx+1}/{len(schools)}] Skipping {school.get('school_name', 'Unknown')} - Already processed")
            continue
        
        school_name = school.get('school_name', 'Unknown')
        school_link = school.get('school_link', '')
        school_district = school.get('school_district', 'Unknown')
        
        if not school_link:
            fail_count += 1
            print(f"[{idx+1}/{len(schools)}] ✗ Skipping {school_name} - No link available")
            continue
        
        print(f"\n[{idx+1}/{len(schools)}] Processing: {school_name}")
        print(f"  District: {school_district}")
        print(f"  Link: {school_link}")
        
        # Fetch detailed information
        details = fetch_school_details(school_link)
        
        if details:
            # Merge detailed information into school data
            school.update(details)
            success_count += 1
            print(f"  ✓ Successfully extracted {len(details)} additional fields")
        else:
            fail_count += 1
            print(f"  ✗ Failed to extract details")
        
        # Save progress at intervals
        if (idx + 1 - start_idx) % save_interval == 0:
            save_progress(schools, 'progress_checkpoint.json')
            print(f"\n>>> Progress checkpoint saved: {idx + 1} schools processed")
            print(f">>> Success: {success_count} | Failed: {fail_count} | Already processed: {already_processed}\n")
        
        # Delay between requests
        time.sleep(delay)
    
    # Final save
    output_file = 'SchoolsData_Complete.json'
    save_schools_data(schools, output_file)
    
    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "="*80)
    print("EXTRACTION COMPLETE!")
    print("="*80)
    print(f"Total schools processed: {end_idx - start_idx}")
    print(f"Successfully extracted details: {success_count}")
    print(f"Failed extractions: {fail_count}")
    print(f"Already processed: {already_processed}")
    print(f"Time taken: {duration:.2f} seconds ({duration/60:.2f} minutes)")
    print(f"Output file: {output_file}")
    print("="*80)
    
    # Sample data
    if success_count > 0:
        print("\nSample of complete data (first school with details):")
        for school in schools:
            if 'affiliate_id' in school or 'affiliation_id' in school:
                print(f"\nSchool: {school.get('school_name', 'Unknown')}")
                print(f"District: {school.get('school_district', 'Unknown')}")
                for key, value in list(school.items())[:15]:  # Show first 15 fields
                    if key not in ['school_name', 'school_district']:
                        print(f"  {key}: {value}")
                if len(school) > 15:
                    print(f"  ... and {len(school) - 15} more fields")
                break
    
    # District-wise completion summary
    district_stats = {}
    for school in schools:
        district = school.get('school_district', 'Unknown')
        has_details = 'affiliate_id' in school or 'affiliation_id' in school
        
        if district not in district_stats:
            district_stats[district] = {'total': 0, 'completed': 0}
        
        district_stats[district]['total'] += 1
        if has_details:
            district_stats[district]['completed'] += 1
    
    print("\n" + "="*80)
    print("DISTRICT-WISE COMPLETION STATUS:")
    print("="*80)
    for district, stats in sorted(district_stats.items(), key=lambda x: x[1]['completed'], reverse=True)[:20]:
        completion_pct = (stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"{district}: {stats['completed']}/{stats['total']} ({completion_pct:.1f}%)")
    
    if len(district_stats) > 20:
        print(f"... and {len(district_stats) - 20} more districts")

if __name__ == "__main__":
    main()
