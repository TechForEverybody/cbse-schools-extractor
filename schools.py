from bs4 import BeautifulSoup
import json
import requests
import time

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
                'name': school_name,
                'link': school_link,
                'description': description
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

def scrape_all_schools_from_file(file_path):
    """Scrape schools from local HTML file"""
    print(f"Reading from file: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    all_schools = []
    schools = extract_schools_from_html(html_content)
    all_schools.extend(schools)
    print(f"Extracted {len(schools)} schools from local file")
    
    # Check for next page
    next_url = get_next_page_url(html_content)
    
    return all_schools, next_url

def scrape_all_schools_from_url(start_url):
    """Scrape schools from URL and follow pagination"""
    all_schools = []
    current_url = start_url
    page_num = 1
    
    while current_url:
        print(f"\nScraping page {page_num}: {current_url}")
        
        try:
            # Fetch the page
            response = requests.get(current_url, timeout=10)
            response.raise_for_status()
            html_content = response.text
            
            # Extract schools
            schools = extract_schools_from_html(html_content)
            all_schools.extend(schools)
            print(f"Extracted {len(schools)} schools from page {page_num}")
            
            # Get next page URL
            next_url = get_next_page_url(html_content)
            
            if next_url:
                current_url = next_url
                page_num += 1
                time.sleep(1)  # Be polite to the server
            else:
                print("No more pages found")
                current_url = None
                
        except Exception as e:
            print(f"Error scraping page {page_num}: {e}")
            break
    
    return all_schools

def main():
    # First, extract from local file
    local_file = 'schools-list.html'
    all_schools, next_url = scrape_all_schools_from_file(local_file)
    
    # If there's a next page URL, continue scraping from the web
    if next_url:
            print("\nScraping remaining pages from the web...")
            web_schools = scrape_all_schools_from_url(next_url)
            all_schools.extend(web_schools)
    
    # Save to JSON
    output_file = 'schools_data.json'
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(all_schools, json_file, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"Total schools extracted: {len(all_schools)}")
    print(f"Data saved to: {output_file}")
    print(f"{'='*60}")
    
    # Display first 3 schools as sample
    if all_schools:
        print("\nSample data (first 3 schools):")
        for i, school in enumerate(all_schools[:3], 1):
            print(f"\n{i}. {school['name']}")
            print(f"   Link: {school['link']}")
            print(f"   Description: {school['description'][:100]}...")

if __name__ == "__main__":
    main()
