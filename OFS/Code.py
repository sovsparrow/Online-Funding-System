#!/usr/bin/env python
# coding: utf-8

# In[13]:


import sqlite3

con = sqlite3.connect('myDB.db')
cur = con.cursor()

print('All Users List:')
for row in cur.execute('SELECT e_mail, name, surname, password FROM User'):
    print(row)

print('\nCompany Owners:')
for row in cur.execute('SELECT user_e_mail FROM Company Owner'):
    print(row)
    
print('\nInvestors:')
for row in cur.execute('SELECT investor_e_mail FROM Investor'):
    print(row)

con.close()


# ### Mix

# In[14]:


#import libs
import PySimpleGUI as sg
import random
from datetime import datetime

#connect to the db
con = sqlite3.connect('myDB.db')
cur = con.cursor()

# global variables
# login_user_id = -1
# login_user_name = -1
# login_user_type = -1 ???????????

#window fucntion: creates a window for each function
def window_login():
    
    layout = [[sg.Text('Welcome to the Online Funding System. Please enter your information.')],
              [sg.Text('E-Mail:',size=(25,1)), sg.Input(size=(20,1), key='email')],
              [sg.Text('Password:',size=(25,1)), sg.Input(size=(20,1), key='password')],
              [sg.Button('Login')]]

    return sg.Window('Login Window', layout)

def window_company_owner():
    
    companies = []
    
    for row in cur.execute('''SELECT Company_Name
                              FROM Company
                              WHERE user_e_mail = ?''', (login_user_e_mail,)):
        companies.append(row)
    
    layout = [[sg.Text('Welcome ' + login_user_name + ' ' + login_user_surname + '!')],
              [sg.Text('Your Companies:')],
              [sg.Listbox(companies, size=(20, 5), key='chosen_company')],
              [sg.Button('Select Company and Edit')],
              [sg.Button('Select Company and See Products')],
              [sg.Button("Select Company and Create New Product")],
              [sg.Button('Logout')]]

    return sg.Window('Company Owner Window', layout)

def window_investor():
    
    companies = []
    
    for row in cur.execute('''SELECT Distinct Company_Name FROM Company'''):
        companies.append(row)    
    
    layout = [[sg.Text('Welcome Investor ' + login_user_name + ' ' + login_user_surname + '!')],
              [sg.Text('All Companies in Database:')],
              [sg.Listbox(companies, size=(20, 10), key='chosen_company_for_inv')],
              [sg.Button('Select Company and See All Their Products')],
              [sg.Button('Logout')]]
    
    
    return sg.Window('Investor Window', layout)

def window_product_choose(chosen_comp_for_inv):
    
    Prod_Name = []
    
    for row in cur.execute('SELECT Product_Name FROM Product WHERE Company_Name = ?', (chosen_comp_for_inv,)):
        Prod_Name.append(row)
    
    layout = [[sg.Text('Products of ' + chosen_comp_for_inv + ':')],
              [sg.Listbox(Prod_Name, size=(20, 10), key='chosen_product_for_inv')],
              [sg.Button('Choose This Product and See The Details')],
              [sg.Button('Return to Products List')]]
    
    return sg.Window('Investor Product Window', layout)   

def See_The_Details(chosen_product_for_inv):
    cur.execute('SELECT Donation_Goal, Description, Type, PID, End_Date FROM Product WHERE Product_Name = ?', (chosen_product_for_inv,))
    row = cur.fetchone()
    Donation_Goal = row[0]
    Description = row[1]
    Type = row[2]
    pıd = row[3]
    end_date = row[4]
    return sg.popup("Chosen Product: " + chosen_product_for_inv + "\n" + "Its Product ID is: " + str(pıd) + "\n" + "Donation Goal is: " + Donation_Goal + "\n" + "Description is: " + Description + "\n" + "Type is: " + Type + "\n" + "End Date is: " + str(end_date))

def button_Updated_Table(new_donation_goal,chose_product):
    if not new_donation_goal.isnumeric():
        sg.popup('Donation Goal should be numeric! No Update!')
        cur.execute('SELECT Donation_Goal FROM Product WHERE Product_Name = ?', (chose_product,))
        row = cur.fetchone()
        prev_info = row[0]
        layout = [[sg.Text('Update Donation Goal')],
                  [sg.Text(chosen_product+', '+'Previous Donation Goal: '+' '+prev_info)],
                  [sg.Text('Enter New Donation Goal'), sg.Input(key='new_donation_goal'),sg.Button('Update Donation!')],
                  [sg.Button('Return to Main Menu')]]
        return sg.Window('Update Donation Goal 1', layout)
    
    else:
        cur.execute('UPDATE Product SET Donation_Goal = ? WHERE Product_Name = ?', (new_donation_goal,chose_product))
        con.commit()
        sg.popup('Donation Goal is Updated!')
        cur.execute('SELECT Donation_Goal FROM Product WHERE Product_Name = ?', (chose_product,))
        row = cur.fetchone()
        prev_info = row[0] 
        layout = [[sg.Text('Update Donation Goal')],
                  [sg.Text(chosen_product+', '+'Previous Donation Goal: '+' '+prev_info)],
                  [sg.Text('Enter New Donation Goal'), sg.Input(key='new_donation_goal'),sg.Button('Update Donation!')],
                  [sg.Button('Return to Main Menu')]]
    
        return sg.Window('Update Donation Goal 2', layout)  


def button_Update_Donation_Goal(chosen_product):
    
    cur.execute('SELECT Donation_Goal FROM Product WHERE Product_Name = ?', (chosen_product,))
    row = cur.fetchone()
    prev_info = row[0]
    
    layout = [[sg.Text('Update Donation Goal')],
              [sg.Text(chosen_product+', '+'Previous Donation Goal: '+' '+prev_info)],
              [sg.Text('Enter New Donation Goal'), sg.Input(key='new_donation_goal'),sg.Button('Update Donation!')],
              [sg.Button('Return to Main Menu')]]
    
    return sg.Window('Update Donation Goal 1', layout), chosen_product

def Cancel_Funding(chosen_product):
    
    cur.execute('DELETE FROM Product WHERE Product_Name = ?', (chosen_product,))
    con.commit()    
    sg.popup('Funding is Cancelled')

    Products = []
    
    for row in cur.execute('SELECT Product_Name FROM Product WHERE Company_Name = ?',(chosen_company,)):
        Products.append(row)

    layout = [[sg.Text('Products of This Company')],
              [sg.Listbox(Products, size=(30, 10), key='chosen_product')],
              [sg.Button('Cancel Its Funding')],
              [sg.Button('Update Its Donation Goal')],
              [sg.Button("Add Tier")],
              [sg.Button('Return to Main Menu')]]
    
    return sg.Window('Products List of This Company', layout)      

def See_Products(chosen_company):
    
    Products = []
    
    for row in cur.execute('SELECT Product_Name FROM Product WHERE Company_Name = ?',(chosen_company,)):
        Products.append(row)

    layout = [[sg.Text('Products of This Company')],
              [sg.Listbox(Products, size=(30, 10), key='chosen_product')],
              [sg.Button('Cancel Its Funding')],
              [sg.Button('Update Its Donation Goal')],
              [sg.Button("Add Tier")],
              [sg.Button('Return to Main Menu')]]
    
    return sg.Window('Products List of This Company', layout)   

def update_company_information(new_information,chosen_company):
    
    cur.execute('UPDATE Company SET Brief_Description = ? WHERE Company_Name = ?', (new_information,chosen_company))
    con.commit()
    sg.popup('Company Information Updated')
    cur.execute('SELECT Brief_Description FROM Company WHERE Company_Name = ?', (chosen_company,))
    row = cur.fetchone()
    prev_info = row[0]
    
    layout = [[sg.Text('Company Information Window')],
              [sg.Text('Previous Company Description:'+' '+prev_info)],
              [sg.Text('Enter New Company Description'), sg.Input(key='new_description'),sg.Button('Edit')],
              [sg.Button('Return to Main Menu')]]

    return sg.Window('Edit Company Information Window', layout)
    
def edit_company_information(chosen_company):
    
    cur.execute('SELECT Brief_Description FROM Company WHERE Company_Name = ?',(chosen_company,))
    row = cur.fetchone()
    prev_info = row[0]

    layout = [[sg.Text('Company Information Window')],
              [sg.Text('Previous Company Description:'+' '+prev_info)],
              [sg.Text('Enter New Company Description'), sg.Input(key='new_description'),sg.Button('Edit')],
              [sg.Button('Return to Main Menu')]]
    
    return sg.Window('Edit Company Information Window', layout), chosen_company
    
def button_login(values):
    
    global login_user_e_mail
    global login_user_name
    global login_user_surname
    global window
    
    pass_email = values['email']
    pass_password = values['password']
                        
    if pass_email == '':
        sg.popup('E-Mail cannot be empty')
    elif pass_password == '':
        sg.popup('Password cannot be empty')
    else:
        cur.execute('SELECT e_mail, name, surname FROM User WHERE e_mail = ? AND password = ?', (pass_email,pass_password))
        row = cur.fetchone()
        if row is None:
            sg.popup('ID or password is wrong!')
        else:
            # this is some existing user, let's keep the ID of this user in the global variable
            login_user_e_mail = row[0]
            # we will use the name in the welcome message
            login_user_name = row[1]
            # we will use the surname in the welcome message
            login_user_surname = row[2]
            sg.popup('Welcome, ' + login_user_name + ' ' + login_user_surname)
            window.close()
            window = window_company_owner()

# window = window_login()


# ### Add Tier 

# In[15]:


def window_add_tier(chosen_product):
    
    cur.execute('SELECT PID FROM Product WHERE Product_Name = ?', (chosen_product,))
    row = cur.fetchone()
    pid = row[0]
    
    layout = [[sg.Text('Minimum Amount:', size=(20,1)), sg.Input(key='minimum_amount', size=(20,1))],
              [sg.Text('Title:', size=(20,1)), sg.Input(key='title', size=(20,1))],
              [sg.Text('Description:', size=(20,1)), sg.Input(key='description', size=(50,1))],
              [sg.Button('Add!'), sg.Button("Return to Main Menu")]]
    
    return sg.Window('Products List of This Company', layout), pid

def button_add_tier(values, pid):
    
    layout = [[sg.Text('Minimum Amount:', size=(20,1)), sg.Input(key='minimum_amount', size=(20,1))],
                  [sg.Text('Title:', size=(20,1)), sg.Input(key='title', size=(20,1))],
                  [sg.Text('Description:', size=(20,1)), sg.Input(key='description', size=(50,1))],
                  [sg.Button('Add!'), sg.Button("Return to Main Menu")]]
    
    minimum_amount = values["minimum_amount"]; title = values["title"]; description = values["description"]
    
    global selected_pid
    
    selected_pid = pid
    
    if title  == "":
        sg.popup("Title name cannot be empty!")
    elif description == "":
        sg.popup("Description cannot be empty!")   
    elif not minimum_amount.isnumeric():
        sg.popup("Minimum Amount should be numeric!")
    else:
        min_amount_val = int(minimum_amount)
        if min_amount_val < 0:
            sg.popup("Min Amount cannot be negative!")
        else: # get a tier id ; TID
            cur.execute("SELECT MAX(TID) FROM Tier")
            row = cur.fetchone()
            
            if row is None: #when there is no Tid
                new_tid = 1
            else:
                new_tid = row[0] + 1
                
            #insert to tier table
            cur.execute("INSERT INTO Tier VALUES (?,?,?,?,?)", (new_tid, selected_pid, minimum_amount, title, description))
            sg.popup("Successfully added new tier, " + title + " " + "with TID AND PID: " + str(new_tid) + "&" + str(selected_pid) + ", minimum amount: " + str(minimum_amount))
            
    window.Element('minimum_amount').Update(value='')
    window.Element('title').Update(value='')
    window.Element('description').Update(value='')


# ### Login

# In[16]:


def button_login(values): # login
    
    global login_user_e_mail
    global login_user_name
    global login_user_surname
    global login_user_type
    global window
    
    pass_email = values['email']
    pass_password = values['password']
                        
    if pass_email == '':
        sg.popup('E-Mail cannot be empty')
    elif pass_password == '':
        sg.popup('Password cannot be empty')
    else:
        #check for a valid user
        cur.execute('SELECT e_mail, name, surname FROM User WHERE e_mail = ? AND password = ?', (pass_email,pass_password))
        row = cur.fetchone()
        
        if row is None:
            sg.popup('ID or password is wrong!')
        else:
            # this is some existing user, let's keep the ID of this user in the global variable
            login_user_e_mail = row[0]
            # we will use the name in the welcome message
            login_user_name = row[1]
            # we will use the surname in the welcome message
            login_user_surname = row[2]
            
            #find the type of user
            #check if it is an investor
            cur.execute("SELECT investor_e_mail FROM Investor WHERE investor_e_mail = ?", (pass_email,))
            row_investor = cur.fetchone()
            
            if row_investor is None: #this is not an investor
                cur.execute("SELECT user_e_mail FROM Company Owner WHERE user_e_mail = ?", (pass_email,))
                row_companyowner = cur.fetchone()
                if row_companyowner is None: #this is not a company owner then admin but now now.
                    sg.popup("USER TYPE ERROR REFFER TO LINE 198")
                else: # a company owner
                    login_user_type = "Company Owner"
                    sg.popup('Welcome, ' + login_user_name + ' ' + login_user_surname)
                    window.close()
                    window = window_company_owner()
            else: # an investor
                login_user_type = "Investor"
                window.close()
                window = window_investor()
                sg.popup('Welcome, ' + login_user_name + ' ' + login_user_surname)

window = window_login()


# ### Create New Product

# In[17]:


def window_create_product(chosen_company):
    
    cur.execute('SELECT Company_Name FROM Company WHERE Company_Name = ?', (chosen_company,))
    row = cur.fetchone()
    c_name = row[0]
    
    Products = []
    
    for row in cur.execute('SELECT Product_Name FROM Product WHERE Company_Name = ?',(chosen_company,)):
        Products.append(row)

    layout = [[sg.Text('Product Name:', size=(20,1)), sg.Input(key='Product_Name', size=(20,1))],
              #[sg.Text('Company Name:', size=(20,1)), sg.Input(key='Company_Name', size=(20,1))], ## Maybe we can just draw this !!!!
              [sg.Text('Type:', size=(20,1)), sg.Input(key='Type', size=(20,1))],
              [sg.Text('Donation Goal:', size=(20,1)), sg.Input(key='Donation_Goal', size=(20,1))],
              [sg.Text('End Date DD.MM.YYYY: ', size=(20,1)), sg.Input(key='End_Date', size=(20,1))], #### !!!! SHOULD BE DATE
              [sg.Text('Description:', size=(20,1)), sg.Input(key='Description', size=(50,1))],
              [sg.Button('Create!'), sg.Button("Return to Main Menu")]]
    
    return sg.Window('Products List of This Company', layout), c_name

def button_create_product(values, c_name):
    
    # cur.execute('SELECT Company_Name FROM Company WHERE Company_Name = ?',(chosen_company,))
    # row = cur.fetchone()
    # c_name = row[0]
 
    product_name = values["Product_Name"]; company_name = c_name; typex = values["Type"]; 
    don_goal = values["Donation_Goal"]; end_date = values["End_Date"]; descripto = values["Description"]
    
    
    if product_name  == "":
        sg.popup("Product Name cannot be empty!")  
    elif typex =="":
        sg.popup("Type cannot be empty!")  
    elif end_date == "":
        sg.popup("End Date cannot be empty!")  
    elif descripto == "":
        sg.popup("Description cannot be empty!")
    elif not don_goal.isnumeric():
        sg.popup("Donation Goal should be numeric!")
    else:
        min_don_goal = int(don_goal)
        if min_don_goal < 0:
            sg.popup("Donation Goal cannot be negative!")
        else: # get a product id ; PID
            cur.execute("SELECT MAX(PID) FROM Product")
            row = cur.fetchone()
            
            if row is None: #when there is no pid
                new_pid = 1
            else:
                new_pid = row[0] + 1
                
            #insert to tier table
            cur.execute("INSERT INTO Product VALUES (?,?,?,?,?,?,?)", (new_pid, product_name, descripto, c_name, don_goal, end_date, typex))
            con.commit()
            sg.popup("Successfully added new product: " + product_name + " " + "with PID: " + str(new_pid) + " to Company: " + c_name)
            
#     window.Element('Product_Name').Update(value='')
#     window.Element('Type').Update(value='')
#     window.Element('Donation_Goal').Update(value='')
#     window.Element('End_Date').Update(value='')
#     window.Element('Description').Update(value='')

    layout2 = [[sg.Text('Product Name:', size=(20,1)), sg.Input(key='Product_Name', size=(20,1))],
              #[sg.Text('Company Name:', size=(20,1)), sg.Input(key='Company_Name', size=(20,1))], ## Maybe we can just draw this !!!!
              [sg.Text('Type:', size=(20,1)), sg.Input(key='Type', size=(20,1))],
              [sg.Text('Donation Goal:', size=(20,1)), sg.Input(key='Donation_Goal', size=(20,1))],
              [sg.Text('End Date DD.MM.YYYY: ', size=(20,1)), sg.Input(key='End_Date', size=(20,1))], #### !!!! SHOULD BE DATE
              [sg.Text('Description:', size=(20,1)), sg.Input(key='Description', size=(50,1))],
              [sg.Button('Create!'), sg.Button("Return to Main Menu")]]
    
    return sg.Window('Products List of This Company', layout2)
    
      


# ### Events

# In[18]:


while True:
    event, values = window.read()
    if event == 'Login':
        button_login(values)
    elif event == 'Select Company and Edit':
        window.close()
        if values['chosen_company'] == []: 
            sg.popup("You did not choose any company! Try Again")
            window = window_company_owner()
        else:
            chosen_company = values['chosen_company'][0][0]
            window = edit_company_information(chosen_company)[0]
    elif event == 'Edit':
        window.close()
        if values['new_description'] == "":
            sg.popup("New Description cannot be empty! Try Again")
            window = edit_company_information(chosen_company)[0] #NEW NEW
        elif values['new_description'].isnumeric():
            sg.popup("New Description cannot only be numeric entry! Try Again")
            window = edit_company_information(chosen_company)[0] #NEW NEW
        else:
            new_information = values['new_description']
            chosen_company = edit_company_information(chosen_company)[1]
            window = update_company_information(new_information,chosen_company)
    elif event == 'Return to Main Menu':
        window.close()
        window = window_company_owner()
        print("Return Çalıştı")
    elif event == 'Select Company and See Products':
        window.close()
        if values['chosen_company'] == []:
            sg.popup("You did not choose any company! Try Again")
            window = window_company_owner()
        else:
            chosen_company = values['chosen_company'][0][0]
            window = See_Products(chosen_company)
    elif event == 'Cancel Its Funding':
        window.close()
        if values['chosen_product'] == []:
            sg.popup("You did not choose any product! Try Again")
            window = See_Products(chosen_company) ###NEW
        else:
            chosen_product = values['chosen_product'][0][0]
            window = Cancel_Funding(chosen_product)
    elif event == 'Update Its Donation Goal':
        window.close()
        if values['chosen_product'] == []:
            sg.popup("You did not choose any product! Try Again")
            window = See_Products(chosen_company) ###NEW
        else:
            chosen_product = values['chosen_product'][0][0]
            window = (button_Update_Donation_Goal(chosen_product)[0])
    elif event == 'Update Donation!':
        window.close()
        if values['new_donation_goal'] == "":
            sg.popup("You did not enter a donation! Try Again")
            window = button_Update_Donation_Goal(chosen_product)[0] ###NEW
        elif not values['new_donation_goal'].isnumeric():
            sg.popup("You did not enter a numeric value! Try Again")
            window = button_Update_Donation_Goal(chosen_product)[0] ###NEW            
        else:
            chose_product = (button_Update_Donation_Goal(chosen_product)[1])
            print(chose_product)
            new_donation_goal = values['new_donation_goal']
            window = button_Updated_Table(new_donation_goal,chose_product)
    elif event == "Add Tier":
        window.close()
        if values["chosen_product"] == []:
            sg.popup("You did not choose any product! Try Again")
            window = See_Products(chosen_company) ###NEW
        else:    
            chosen_product = values["chosen_product"][0][0]
            window =(window_add_tier(chosen_product)[0])
    elif event == "Add!":
        sel_pid = (window_add_tier(chosen_product)[1])
        button_add_tier(values, sel_pid)
    elif event == "Select Company and Create New Product":
        window.close()
        if values['chosen_company'] == []:
            sg.popup("You did not choose any company! Try Again")
            window = window_company_owner()       
        else:
            chosen_company = values["chosen_company"][0][0]
            window = (window_create_product(chosen_company)[0])
    elif event == "Create!":
        window.close()
        sel_cname = (window_create_product(chosen_company)[1])
        window = button_create_product(values, sel_cname)
    elif event == 'Select Company and See All Their Products': ###############################
        window.close()
        if values['chosen_company_for_inv'] == []:
            sg.popup("You did not choose any company! Try Again")
            window = window_investor()
        else:
            chosen_comp_for_inv = values['chosen_company_for_inv'][0][0]
            window = window_product_choose(chosen_comp_for_inv)
    elif event == 'Return to Products List':
        window.close()
        window = window_investor()
    elif event == 'Choose This Product and See The Details':
        window.close()
        if values['chosen_product_for_inv'] == []:
            sg.popup("You did not choose any product! Try again")
            window = window_product_choose(chosen_comp_for_inv)
        else:
            chosen_product_for_inv = values['chosen_product_for_inv'][0][0]
            See_The_Details(chosen_product_for_inv)
            window = window_product_choose(chosen_comp_for_inv) #window_investor() idi
    elif event == "Logout":
        window.close()
        window = window_login()
    else:
        break
        
window.close()

con.commit()
con.close()


# In[ ]:




