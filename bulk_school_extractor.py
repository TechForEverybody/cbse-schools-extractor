from bs4 import BeautifulSoup
import json
import requests
import time
from datetime import datetime

def extract_schools_from_html(html_content):
    """Extract school data from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    schools = []
    
    # Find all catbox divs
    catboxes = soup.find_all('div', class_='catbox')
    
    for catbox in catboxes:
        try:
            # Extract school name and link
            h2 = catbox.find('h2')
            if h2 and h2.find('a'):
                school_name = h2.find('a').get_text(strip=True)
                school_link = h2.find('a').get('href')
            else:
                continue
            
            # Extract description
            p = catbox.find('p')
            description = p.get_text(strip=True) if p else ""
            
            schools.append({
                'school_name': school_name,
                'school_link': school_link,
                'school_description': description
            })
        except Exception as e:
            print(f"Error extracting school data: {e}")
            continue
    
    return schools

def get_next_page_url(html_content):
    """Extract next page URL from pagination"""
    soup = BeautifulSoup(html_content, 'html.parser')
    next_link = soup.find('a', class_='nextpostslink')
    
    if next_link and next_link.get('href'):
        return next_link.get('href')
    return None

def scrape_schools_from_district(district_url, district_name):
    """Scrape all schools from a district following pagination"""
    all_schools = []
    current_url = district_url
    page_num = 1
    
    while current_url:
        print(f"  Scraping page {page_num}: {current_url}")
        
        try:
            # Fetch the page
            response = requests.get(current_url, timeout=15)
            response.raise_for_status()
            html_content = response.text
            
            # Extract schools
            schools = extract_schools_from_html(html_content)
            
            # Add district name to each school
            for school in schools:
                school['school_district'] = district_name
            
            all_schools.extend(schools)
            print(f"  ✓ Extracted {len(schools)} schools from page {page_num}")
            
            # Get next page URL
            next_url = get_next_page_url(html_content)
            
            if next_url:
                current_url = next_url
                page_num += 1
                time.sleep(1)  # Be polite to the server
            else:
                current_url = None
                
        except Exception as e:
            print(f"  ✗ Error scraping page {page_num}: {e}")
            break
    
    return all_schools

def load_districts(file_path='districts.json'):
    """Load districts from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            districts = json.load(file)
        print(f"Loaded {len(districts)} districts from {file_path}")
        return districts
    except Exception as e:
        print(f"Error loading districts: {e}")
        return []

def save_schools_data(schools, output_file='SchoolsData.json'):
    """Save schools data to JSON file"""
    try:
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(schools, json_file, indent=2, ensure_ascii=False)
        print(f"\n✓ Data saved to: {output_file}")
        return True
    except Exception as e:
        print(f"\n✗ Error saving data: {e}")
        return False

def main():
    print("="*70)
    print("BULK SCHOOL EXTRACTOR - CBSE Schools Data Scraper")
    print("="*70)
    
    # Load districts
    districts = load_districts('districts.json')
    
    if not districts:
        print("No districts found. Exiting...")
        return
    
    # Ask user for confirmation or limit
    print(f"\nTotal districts to scrape: {len(districts)}")
    user_input = input("Enter number of districts to scrape (press Enter for all): ").strip()
    
    if user_input:
        try:
            limit = int(user_input)
            districts = districts[:limit]
            print(f"Limiting to first {limit} districts")
        except ValueError:
            print("Invalid input. Processing all districts.")
    
    all_schools = []
    start_time = datetime.now()
    
    # Scrape each district
    for idx, district in enumerate(districts, 1):
        district_name = district.get('name', 'Unknown')
        district_url = district.get('url', '')
        
        if not district_url:
            print(f"\n[{idx}/{len(districts)}] Skipping {district_name} - No URL")
            continue
        
        print(f"\n[{idx}/{len(districts)}] Processing: {district_name}")
        print(f"URL: {district_url}")
        
        try:
            schools = scrape_schools_from_district(district_url, district_name)
            all_schools.extend(schools)
            print(f"  ✓ Total schools from {district_name}: {len(schools)}")
            
            # Save progress every 10 districts
            if idx % 10 == 0:
                save_schools_data(all_schools, 'SchoolsData.json')
                print(f"\n>>> Progress saved: {len(all_schools)} schools from {idx} districts")
            
            # Small delay between districts
            time.sleep(2)
            
        except Exception as e:
            print(f"  ✗ Error processing {district_name}: {e}")
            continue
    
    # Final save
    save_schools_data(all_schools, 'SchoolsData.json')
    
    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "="*70)
    print("EXTRACTION COMPLETE!")
    print("="*70)
    print(f"Total districts processed: {len(districts)}")
    print(f"Total schools extracted: {len(all_schools)}")
    print(f"Time taken: {duration:.2f} seconds ({duration/60:.2f} minutes)")
    print(f"Output file: SchoolsData.json")
    print("="*70)
    
    # Display sample data
    if all_schools:
        print("\nSample data (first 3 schools):")
        for i, school in enumerate(all_schools[:3], 1):
            print(f"\n{i}. {school['school_name']}")
            print(f"   District: {school['school_district']}")
            print(f"   Link: {school['school_link']}")
            print(f"   Description: {school['school_description'][:80]}...")
    
    # District-wise summary
    district_counts = {}
    for school in all_schools:
        district = school['school_district']
        district_counts[district] = district_counts.get(district, 0) + 1
    
    print("\n" + "="*70)
    print("DISTRICT-WISE SCHOOL COUNT:")
    print("="*70)
    for district, count in sorted(district_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"{district}: {count} schools")
    
    if len(district_counts) > 10:
        print(f"... and {len(district_counts) - 10} more districts")

if __name__ == "__main__":
    main()
