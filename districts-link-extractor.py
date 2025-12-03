from bs4 import BeautifulSoup
import json

# Read the HTML file
with open('districts-html.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parse HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Find all district links
districts = []
tag_cloud = soup.find('ul', class_='wp-tag-cloud')

if tag_cloud:
    links = tag_cloud.find_all('a')
    for link in links:
        district_name = link.get_text(strip=True)
        district_url = link.get('href')
        districts.append({
            'name': district_name,
            'url': district_url
        })

# Save to JSON file
with open('districts.json', 'w', encoding='utf-8') as json_file:
    json.dump(districts, json_file, indent=2, ensure_ascii=False)

print(f"Extracted {len(districts)} districts")
print("\nFirst 5 districts:")
for district in districts[:5]:
    print(f"  {district['name']}: {district['url']}")
