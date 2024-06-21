import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from extractor import parse_lab_results
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

st.sidebar.title('LAB-LINK 🔗')


if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if 'sheetmade' not in st.session_state:
    st.session_state['sheetmade'] = False

if st.session_state['authenticated'] == True:


    # Streamlit interface
    st.title("🧪 Labs")

    # Creating columns for inputs
    col1, col2 , col3 = st.columns(3)

    with col1:
        id_input = st.text_input("ID:", placeholder= 'Id')  ##173293317 - Default value
        st.session_state['id'] = id_input

    with col2:
        surname_input = st.text_input("Surname:",placeholder= 'Surname') ##ABRAHAMS
        st.session_state['surname'] = surname_input

    with col3:
        button_search =  st.button("Search")
        button_logout = st.button("Logout")

    if button_logout:
        # time.sleep(2)
        st.switch_page("🏠_Home.py")

    if button_search:

        st.session_state['sheetmade'] = False
        if (id_input == '') or (surname_input == ''):
            st.error("Please type in an ID and Surname")

        else:
            with st.spinner("Fetching patient and labs"):
                try: ## STEP 1 = Authentication
                    # Setup Selenium WebDriver
                    print("########################")
                    chrome_options = Options()
                    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
                    chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
                    chrome_options.add_argument("--window-size=1920x1080")  # Set the window size
                    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection

                    # Create Chrome driver with the specified options
                    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

                # Navigate to the website
                    website = 'https://trakcarelabwebview.nhls.ac.za/trakcarelab/csp/system.Home.cls#/Component/SSUser.Logon'
                    driver.get(website)


                    # Wait for the login page elements
                    wait = WebDriverWait(driver,3)
                    username_id = "SSUser_Logon_0-item-USERNAME"
                    password_id = "SSUser_Logon_0-item-PASSWORD"
                    username_element = wait.until(EC.presence_of_element_located((By.ID, username_id)))
                    password_element = wait.until(EC.presence_of_element_located((By.ID, password_id)))

                    # Enter the credentials
                    username_element.clear()
                    username_element.send_keys(st.session_state.username)
                    password_element.clear()
                    password_element.send_keys(st.session_state.password + Keys.ENTER) 
                    ## CREDENTIALS CANNOT BE WRONG AND HENCE THE ONLY PROBLEM IS WITH AUTHENTICATION


                    wait = WebDriverWait(driver,3)
                    record_id = "web_DEBDebtor_FindList_0-item-HospitalMRN"
                    record_element = wait.until(EC.presence_of_element_located((By.ID, record_id))) ## STEP 1 - IF THIS COMPONENT YIELDS TRUE THEN AUTHETICATION Is right

                    try: ### STEP 2
                        id = st.session_state.id
                        surname = st.session_state.surname

                        
                        surname_id="web_DEBDebtor_FindList_0-item-SurnameParam"
                        surname_element = wait.until(EC.presence_of_element_located((By.ID,surname_id)))
                        surname_element.clear()

                        surname_element.send_keys(surname)

                        
                        record_id = "web_DEBDebtor_FindList_0-item-HospitalMRN"
                        record_element = wait.until(EC.presence_of_element_located((By.ID, record_id))) ## STEP 1 - IF THIS COMPONENT YIELDS TRUE THEN AUTHETICATION Is right
                        record_element.clear()

                        record_element.send_keys(id + Keys.ENTER) 

                        wait = WebDriverWait(driver,3)
                        
                        testing_id = "web_DEBDebtor_FindList_0-row-0-item-Episodes" ## STEP - IF THIS COMPONENT YIELDS TRUE then both patient and record ID are correct.
                        testing_element =wait.until(EC.element_to_be_clickable((By.ID, testing_id)))
                        st.success("Patient was found")
                        
                        wait = WebDriverWait(driver,60) ## IF IT REACHES HERE THEN THE PATIENT IS FOUND


                        ## STEP 3) Finding labs
                        try:
                            rows = driver.find_elements(By.XPATH, '//md-icon[starts-with(@id, "web_DEBDebtor_FindList_0-row-")]')
                            num_of_labs = len(rows)


                            if num_of_labs == 0:
                                st.error("Patient does not have any lab results")
                                driver.quit()

                            else:

                                ## Figure out how many labs the patient has had
                                textfile_content = ''

                                
                                for index, row in enumerate(rows):
                                    textfile_content = textfile_content + "\n"+  'Lab: ' + str(index+1) 
                                    dropdown_id = "web_DEBDebtor_FindList_0-row-"+ str(index) +"-item-Episodes" ## STEP - IF THIS COMPONENT YIELDS TRUE then both patient and record ID are correct.
                                    dropdown_element =wait.until(EC.element_to_be_clickable((By.ID, dropdown_id)))
                                    dropdown_element.click()
            
                                    ## The id is dependent on the laboratory number
                                    more_action_id = "web_EPVisitNumber_List_"+str(index)+"_0-row-0-misc-actionButton"

                                    # Wait for the PDF element to be clickable
                                    more_action_element  = wait.until(EC.presence_of_element_located((By.ID, more_action_id)))

                                    # Click the PDF element to trigger the download
                                    more_action_element.click()
                                    cumulative_history_id = "tc_ActionMenu-link-CumulativeHistory"

                                    # Wait for the PDF element to be clickable
                                    cumulative_history_element  = wait.until(EC.element_to_be_clickable((By.ID, cumulative_history_id)))
                                    
                                    # Click the PDF element to trigger the download
                                    cumulative_history_element.click()

                                    ## Waiting for the Page to load
                                    history_page_id = 'web_EPVisitTestSet_CumulativeHistoryView_0-header-caption'
                                    history_page_element = wait.until(EC.presence_of_element_located((By.ID,history_page_id)))
                                    history_page_element.click()
                                    st.success('Labs found')


                                    copied_content = driver.execute_script("return document.body.innerText")

                                    ## Do not need to use control keys but can run 
                                    
                                    patient_content = textfile_content+ "\n" + copied_content

                                    driver.back()
                            
                                    dropdown_id = "web_DEBDebtor_FindList_0-row-"+ str(index) +"-item-Episodes" ## STEP - IF THIS COMPONENT YIELDS TRUE then both patient and record ID are correct.
                                    dropdown_element =wait.until(EC.element_to_be_clickable((By.ID, dropdown_id)))
                                    dropdown_element.click()
                        
                                        
                            
                                
                                data_without = parse_lab_results(patient_content)
                                st.session_state['sheetmade'] = True   ### This way either the sheet is made directly or through the processer
                                st.session_state['table'] = data_without
                    
                                
                                
                        
                                home_id = "tc_NavBar-misc-homeButtonIcon"
                                home_element  = wait.until(EC.element_to_be_clickable((By.ID, home_id)))
                                home_element.click()
                                driver.quit()

                        except:
                            st.error("Problems with lab results, Please-Rerun")
                            driver.quit()

                        
                
                    except:
                        driver.quit()
                        st.error("Patient was not found, Please try again")


                except:
                    
                    st.error("Server Authentication Error, Please Re-run")
                    print("Authentication error")
                    driver.quit()
                

            
        

    


## ONLY PERFORMED WHEN A PATIENT IS FOUND AND TABLE IS SHOWN
    if st.session_state['sheetmade'] == True:
        data = st.session_state['table']
        st.dataframe(data)
        investigation_names = data['Investigation'].tolist() 

        # Create a selectbox with the title 'Choose an Option'
        selected_investigation = st.selectbox('Choose an Investigation:', investigation_names)

        # Display the selected option
        filtered_data = data[data['Investigation'] == selected_investigation]

        # Display the filtered data
        st.write('Details for : ' + selected_investigation)
        st.dataframe(filtered_data)

    

elif st.session_state['authenticated'] == False:

    st.error("Lab Results are only available after logging in.")
    page_button = st.button("Return Home")
    if page_button:
        with st.spinner('Returning home'):
            time.sleep(2)
            st.switch_page("🏠_Home.py")

    

