from splinter import Browser as browser
import time
import csv
import argparse
import os

def writeToCSV(fileObject, data):
    csv_writer = csv.writer(fileObject)

    for index, row in enumerate(data, start=0):
        csv_writer.writerow(row)

#fn to print table data
def getTableData(tableRow):

    table_element = browser.find_by_xpath('/html/body/div[8]/div/div/div[2]/div[1]/div[2]/table').first

    # Iterate through rows in the table
    cnt=0
    tableData=[]
    for row in table_element.find_by_xpath('.//tr')[tableRow:tableRow+51]:
        # Extract and print the text content of each cell in the row
        cell_texts = [cell.text.strip() for cell in row.find_by_xpath('.//td | .//th')]
        cell_cleaned=[]
        for cell in cell_texts:
            if "\n" in cell:
                cell_cleaned+=cell.split("\n")
            else:
                cell_cleaned.insert(-1,cell)
        if '' in cell_cleaned:
            cell_cleaned[cell_cleaned.index('')]=1
        tableRow=cell_cleaned
        tableData.append(tableRow)
    return (tableData)


if __name__ =="__main__":
    # >>>>> Usage <<<<<
    # >>>>> python main.py -email "EMAIL" -pwd "PWD"

    parser = argparse.ArgumentParser()
    
    # email and pwd
    parser.add_argument('-email', type=str, help='Email address')
    parser.add_argument('-pwd', type=str, help='Password')

    # Parse the cli args
    args = parser.parse_args()

    browser = browser('firefox', headless=True)
    browser.visit('https://monkeytype.com/login')
    ## Accept Cookies
    accept_cookies_btn=browser.find_by_xpath("/html/body/div[8]/div/div[2]/div[2]/div[2]/button[1]")
    accept_cookies_btn.click()

    # login
    userName=args.email
    pwd=args.pwd
    userNameField=browser.find_by_xpath("/html/body/div[9]/div[2]/main/div[2]/div[3]/form/input[1]").fill(userName)
    pwdField=browser.find_by_xpath("/html/body/div[9]/div[2]/main/div[2]/div[3]/form/input[2]").fill(pwd)
    loginBtn=browser.find_by_xpath("/html/body/div[9]/div[2]/main/div[2]/div[3]/form/button[1]")
    loginBtn.click()

    # open leader board
    browser.find_by_xpath("/html/body/div[9]/div[2]/header/nav/button[1]/div/i").click()

    time.sleep(2)



    count=0
    verbose=True
    # saving file csv:
    csv_file_path="./output.csv"
      
    # # Check if the file exists
    if os.path.exists(csv_file_path):
        os.system("rm -f {}".format(csv_file_path))
        
    csv_file=open(csv_file_path, 'w', newline='')

  
    while (count<10000):
        scrollScript = "document.evaluate('//table', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.scrollIntoView({ behavior: 'smooth', block: 'end', inline: 'nearest' });"
        browser.execute_script(scrollScript)
        time.sleep(2)
        data=getTableData(count)
        if verbose:
            for row in data:
                print(row)
        writeToCSV(csv_file,data)
        count+=50
    csv_file.close()

    time.sleep(5)
    exit(0)