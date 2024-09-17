import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time

driver = webdriver.Chrome()  #initialize a web-browser instance 
driver.get("https://www.defense.gov/News/Contracts/") #this method directs the browser to the url


def extract_dates_and_urls(driver):
    """Extract dates and URLs from the current page."""
    # Wait until the anchors are present
    anchors = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.XPATH, '//a[contains(text(), "Contracts For")]')) #locate this element in the html code
    )
    
    date_info = []
    
    # Loop through the anchors and extract date information
    for anchor in anchors:
        text = anchor.text
        match = re.search(r'Contracts For (\w+\. \d{1,2}, \d{4})', text)
        if match:
            date = match.group(1)
            href = anchor.get_attribute('href')
            date_info.append({'date': date, 'url': href})
    
    return date_info

# Extract dates and URLs from the single page
all_dates_info = extract_dates_and_urls(driver)

# Print all extracted dates and URLs
for info in all_dates_info:
    print(f"Date: {info['date']}, URL: {info['url']}")

# Close the WebDriver
driver.quit()

#print out dates available for user to choose from 
for index, entry in enumerate(all_dates_info, start=1):
    if 'date' in entry:
        data_value = entry['date']
        print(f"{index}: {data_value}")
    #print(f"{index}: {all_dates_info[]}")
    #dates_dictionary[index] = date
    
#allows user to choose 1 date 
user_input = int(input("Please select one date above: "))
for index, entry in enumerate(all_dates_info, start=1):
 if user_input == index: 
        chosen_date = entry['date']
        print(f"Date: {entry['date']}\nURL:  {entry['url']}")
        selected_url = entry['url']

# go through every paragraph in the page (parsed from the URL) to match company name and award amount
def extract_company_and_amount(paragraph_text):
    # Define a regex pattern for company names 
    company_pattern = r'^(.+?)\s+(?:is awarded|was awarded|has been awarded|has been added|are awarded|are each awarded|is receiving|have each been awarded|is being awarded|awarded)'
    # Define a regex pattern for the awarded amount (matches dollar amounts)
    amount_pattern = r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
    # Search for the company name
    company_match = re.search(company_pattern, paragraph_text)
    if company_match:
        # Get the text up to the unwanted phrase
        company_name = company_match.group(1).strip()     
        # removes these phrases from company name
        clean_company_name = re.sub(r'(is awarded|was awarded|has been awarded|has been added|are awarded|are each awarded|is receiving|have each been awarded|is being awarded|awarded)', '', company_name).strip()
        # Remove any trailing commas from the cleaned company name
        clean_company_name = clean_company_name.rstrip(',').strip()
    else:
        clean_company_name = "Company not found"
    # Search for the awarded amount
    amount_match = re.search(amount_pattern, paragraph_text)
    awarded_amount = amount_match.group(0) if amount_match else "Amount not found"
    
    return clean_company_name, awarded_amount


def extract_awarded_info_from_paragraphs(selected_url):
    total_amount_list = []
    driver = webdriver.Chrome()
    driver.get(selected_url)
    # Get all paragraphs from the page
    paragraphs = driver.find_elements(By.TAG_NAME, 'p')
    # Filter paragraphs that contain the word "awarded", this is to find visible paragraphs
    awarded_paragraphs = [p for p in paragraphs if "awarded" in p.text]
    results = []
    #get first word
    for index, paragraph in enumerate(awarded_paragraphs, start=1):
        first_word = paragraph.text.split()[0] if paragraph.text.strip() else "(Empty paragraph)"
        #print(f"Paragraph {index}: First word is '{first_word}'")
        print(f"{index}.", end = " ")   
        # Extract company name and awarded amount
        company, amount = extract_company_and_amount(paragraph.text)
        print(f"Company: {company}")
        print(f"Awarded Amount: {amount}")
        print("-" * 50)
        # add each amount to the total amount
        total_amount_list.append(int(amount.replace('$', '').replace(',', '')))
        # Append result to the list for further processing if needed
        results.append({
            'paragraph_index': index,
            'first_word': first_word,
            'company': company,
            'amount': amount
        })
    sum_amount = sum(total_amount_list)
    formatted_sum = "{:,}".format(sum_amount)
    print(f"The U.S Department of Defense spent ${formatted_sum} on this date!")
    
    driver.quit()  # Close the browser after extracting information
    
    return results

awarded_info = extract_awarded_info_from_paragraphs(selected_url)

# Optionally, process the awarded_info further or display it
#print(f"Number of private companies receiving contracts': {len(awarded_info)}")



"""
#for each paragraph, fetch the company's name and the award amount using regex patterns 
def fetch_company_names_and_dollars(selected_url):
         if selected_url:
          paragraphs = []
          driver = webdriver.Chrome()
          driver.get(selected_url)
          paragraphs = driver.find_elements(By.TAG_NAME, 'p')
          
          paragraph_texts = [paragraph.text for paragraph in paragraphs]
          #define regex patterns to find company names
          name_patterns = [r'(.+?)\s+(Co\.|Inc\.|Corp\.)\b',r'(.+?),\s+(is awarded|are awarded)\b']
          #define regex patterns to find contract value 
          dollar_patterns = [r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)']
          companies = []
          dollar_amounts =[]
          for paragraph in paragraph_texts: 
           for pattern in name_patterns:
             matches = re.findall(pattern, paragraph)
             for match in matches:
                 if isinstance(match, tuple):
                     companies.append(' '.join(match).strip())
                 else:
                     companies.append(match.strip())
           for dollar_pattern in dollar_patterns: 
             dollar_matches = re.findall(dollar_pattern,paragraph)
             if dollar_matches:
                 dollar_amounts.append(dollar_matches[0])

         driver.quit()     
         return companies, dollar_amounts, paragraph_texts 
"""

"""
companies, dollar_amounts, paragraph_texts = fetch_company_names_and_dollars(selected_url)
#later append all the integer amounts to this list, sum this up to fetch the total $ spent today
int_dollar_amounts = []
# this was supposed to return {Company} {Award $} based on matching indices, but it does not work since sometimes Company Names are not returned due to pattern matching 
for index, (company, dollar_amount) in enumerate(zip(companies, dollar_amounts),start =1):
    print(f"{index}: {company} ${dollar_amount}")
    #print(f"{index_format.format(index)} {company_format.format(company)} {amount_format.format(dollar_amount)}")
    int_dollar_amounts.append(int(dollar_amount.replace(',','')))

sum_amount = sum(int_dollar_amounts)
formatted_sum = "{:,}".format(sum_amount)
print(f"The U.S Department of Defense spent ${formatted_sum}")
"""



"""
an attempt to match company name and $ if they are in the same paragraph 
def print_final_output(paragraph_texts, companies, dollar_amounts):
 for index, paragraph in enumerate(paragraph_texts, start=1):
    companies_in_paragraph = [company for company in companies if company in paragraph]
    dollar_amounts_in_paragraph = [dollar_amount for dollar_amount in dollar_amounts if dollar_amount in paragraph]
    if companies_in_paragraph and dollar_amounts_in_paragraph:
        for company in companies_in_paragraph:
            for dollar_amount in dollar_amounts_in_paragraph:
                 print(f"{index}: Company: {company} Dollar Amount: ${dollar_amount}")
                 int_dollar_amounts.append(int(dollar_amount.replace(',','')))

"""

#print_final_output(paragraph_texts, companies, dollar_amounts)









    


        


