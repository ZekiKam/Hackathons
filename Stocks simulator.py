#Complete version
import yfinance as yf
import time
money=1000
day=1


companies=['Techno','Aether','Pixelo','Meta','Microx']
techno1=0
aether1=0
pixelo1=0
meta1=0
microx1=0
stocks1=[techno1,aether1,pixelo1,meta1,microx1]
auth=['1','2','3','4','5','x']


n=0
stocks=[]
previous_price=[]
userchoices=[]
price_difference=[]
price_difference_percent=[]
gain_loss_amount=[]
gain_loss_name=[]
company_num=['TSLA','AAPL','AMZN','META','MSFT']


print('Welcome to the virtual stock market 2023.')


#Authentication
users=['Gertie','Khalil']
password=['Pigeon_010','Car_drifting01']
memorable_name=['respect','sidekick']

def validity(password):
   for i in password:
       if any([x.isupper() for x in password]) and any([y.islower() for y in password]) and any([z.isdigit() for z in password]):
           return 'valid'
       else:
           return False


def reset_password(name1):
   memory=input('\nEnter memorable name to reset password: ')
   while memory!=memorable_name[name1]:
       memory=input('Wrong memorable name, enter again: ')
   print('\nPlease enter password with at least 1 UPPERCASE, LOWERCASE and NUMBER')
   new_password=input('Enter new password: ')
   while validity(new_password) != 'valid':
       new_password=input('Password not valid, enter new password again: ')
   password[name1]=new_password
   return new_password


def password1(name):
   password2=input('Enter password: ')
   while password2!=password[name]:
       print('''\nWrong password\nEnter (1) to enter password again\nEnter (2) to RESET password''')
       e=input('Enter: ')
       f=['1','2']
       while e not in f:
           e=input('Invalid input, enter again: ')
       if e=='1':
           password2=input('Enter password again: ')
       elif e=='2':
           password2=reset_password(name)
           print('...Password has been resetted...')
           username1()
   print('\nLoading...\n','-'*100,'\n')
   time.sleep(1)


def username1():
   print('-'*100+'\nLOG IN')
   username=input('Enter username: ')
   while username not in users:
       b=input("\nUsername not found\nEnter (1) to enter username again\nDon't have an account? Enter (2) to SIGN UP now!: ")
       c=['1','2']
       while b not in c:
           b=input('\nInvalid input, enter again: ')
       if b=='1':
           username=input('Enter username again: ')
       elif b=='2':
           username=sign_up()
   d=users.index(username)
   password1(d)


def sign_up():
   #Username
   print('-'*100+'\nSIGN UP')
   user_name=input('Enter username: ')
   score=0
   while score!=3:
       while len(user_name)>20:
           user_name=input('Maximum 20 characters, enter username again: ')
       score+=1
       while len(user_name)<4:
           user_name=input('Minimum 4 characters, enter username again: ')
       score+=1
       while user_name in users:
           user_name=input('Username unavailable, enter username again: ')
       score+=1
   users.append(user_name)


   #Password
   print('\nPlease enter password with at least 1 UPPERCASE, LOWERCASE and NUMBER')
   password3=input('Enter password: ')
   while validity(password3)!='valid':
       password3=input('Password not valid, enter new password again: ')
   confirm_password=input('Confirm password: ')
   while confirm_password!=password3:
       confirm_password=input("Passwords don't match, confirm again: ")
   password.append(password3)
   print('\n\nAccount successfully created\nLoading...\n'+'-'*100+'\n')
   return user_name



print('''
Enter (1) to LOG IN\nEnter (2) to SIGN UP
''')
a=input('Enter: ')
while a!='1' and a!='2':
   a=input('\nInvalid input, enter again: ')
if a=='1':
   username1()
elif a=='2':
   sign_up()



#Get shares price 11 days ago as previous_price to calculate net change for the 1st day
def eleven():
   def stocks_price(company,s):
       stock=yf.Ticker(company)
       n=str(s)+'d'       
       last_data=stock.history(period=n)
       return last_data['Close'][0]
   for i in company_num:
       previous_price.append(round(stocks_price(i,11),2))
eleven()


def stocks_owned(num,name):
   owned_list=''
   for i in range(5):
       if num[i]>0:
           owned_list+=str(num[i])
           owned_list+=' '
           owned_list+=name[i]
           owned_list+=' '
   if owned_list=='':
       return 'none'
   else:
       return owned_list


def gain_loss(amount,name1,i):
   if len(amount)>0:
       if amount[i]>0:
           text='You have gained $',round(amount[i],3),'from',name1[i]
           return str(text).replace('(','').replace(')','').replace(',','').replace("'",'')           
       elif amount[i]<0:
           text1='You have lost $',round(amount[i],3),'from',name1[i]
           return str(text1).replace('(','').replace(')','').replace(',','').replace("'",'').replace('-','')
       else:
           pass
   else:
       pass


#Start trading
for k in range(10):


   print('\n\nDay', str(day))
   #Get shares price of specific day (i)
   def stocks_price(company,s):
       stock=yf.Ticker(company)
       n=str(s)+'d'
       last_data=stock.history(period=n)
       return last_data['Close'][0]      #Closing price
   for i in company_num:
       stocks.append(round(stocks_price(i,day),2))
  
   for i in range(len(stocks)):
       price_difference.append(stocks[i]-previous_price[i])
   for i in range(len(stocks)):           
       price_difference_percent.append(price_difference[i]/previous_price[i]*100)


   for i in range(len(stocks1)):
       if stocks1[i] != 0:
           money+=price_difference[i]*stocks1[i]
           gain_loss_amount.append(price_difference[i]*stocks1[i])
           gain_loss_name.append(companies[i])
       else:
           pass
  
   print('Account balance: $',round(money,5))
   number=0
   for i in range(len(stocks1)):
       if stocks1[i]>0:
           number+=1


   for x in range(number):
       print(gain_loss(gain_loss_amount,gain_loss_name,x))
   print('Stocks you currently own:',stocks_owned(stocks1,companies),'\n')
   print('1\t\t2\t\t3\t\t4\t\t5')
   print('Techno\t\tAether\t\tPixelo\t\tStark\t\tMicrox')


   for i in range(len(stocks)):
       print('$',stocks[i],'\t',end='')
   print('\n')
   for i in range(len(stocks)):
       print(round(price_difference[i],2),'({}%)'.format(round(price_difference_percent[i],2)),'\t',end='')
   print('\n')


   if money>0:
       company=input("\nEnter which company would you like to buy stocks from (1,2,3,4 or 5) or 'x' to sell or skip: ")
       while company not in auth:
           print('\nInvalid input, please enter again')
           company=input("\nEnter which company would you like to buy stocks from (1,2,3,4 or 5) or 'x' to sell or skip: ")


       if company=='x':
           yn=input("Do you want to sell your stocks? (Enter 'y' to sell or 'n' to skip): ")
           while yn!='y' and yn!='n':
               print('\nInvalid input, please enter again')
               yn=input("Do you want to sell your stocks? (Enter 'y' to sell or 'n' to skip): ")



#Sell
           if yn=='y':
               choice=input("\nEnter which stock you would like to sell (1,2,3,4 or 5) or x to skip: ")
               while choice not in auth:
                   print('\nInvalid input, please enter again')
                   choice=input("\nEnter which stock you would like to sell (1,2,3,4 or 5) or x to skip: ")

               if choice!='x':
                   choice=int(choice)
                   print('The price of a stock from', companies[choice-1],'is $', str(stocks[choice-1]))
                   print('You have', str(stocks1[choice-1]), companies[choice-1],'stocks')

                   amount=input('How much stocks would you like to sell: ')
                   while not amount.isdigit():
                       print('\nInvalid input, please enter again')
                       amount=input('How much stocks would you like to sell: ')
                   amount=int(amount)

                   choice=str(choice)
                   count=userchoices.count(choice)

                   if count>=amount and choice in userchoices:
                       if choice=='1':
                           for i in range(amount):
                               userchoices.remove('1')
                       elif choice=='2':
                           for i in range(amount):
                               userchoices.remove('2')
                       elif choice=='3':
                           for i in range(amount):
                               userchoices.remove('3')
                       elif choice=='4':
                           for i in range(amount):
                               userchoices.remove('4')
                       elif choice=='5':
                           for i in range(amount):
                               userchoices.remove('5')


                       choice=int(choice)
                       value=amount*stocks[choice-1]
                       money+=value
                       print('You now have $', str(money))
                       stocks1[choice-1]-=amount
                       print('You now have', str(stocks1[choice-1]), companies[choice-1],'stocks')
                       print('\n','-'*50,'Transaction successful','-'*50)

                   else:
                       print('You do not own that stock')
                       print('\n','-'*50,'Transaction failed','-'*50)

               else:
                   pass

           elif yn=='n':
               exit


#Buy
       else:
           company=int(company)
           print('Price for a stock from', companies[company-1],'is $', str(stocks[company-1]))
           print('You have $',str(money))

           amount1=input('How many stocks would you like to buy?: ')
           while not amount1.isdigit():
               print('\nInvalid input, please enter again')
               amount1=input('How many stocks would you like to buy?: ')
           amount1=int(amount1)

           company=str(company)

           if company=='1':
               for i in range(amount1):
                   userchoices.extend('1')
           elif company=='2':
               for i in range(amount1):
                   userchoices.extend('2')
           elif company=='3':
               for i in range(amount1):
                   userchoices.extend('3')
           elif company=='4':
               for i in range(amount1):
                   userchoices.extend('4')
           elif company=='5':
               for i in range(amount1):
                   userchoices.extend('5')

           company=int(company)
           cost=amount1*stocks[company-1]
           if cost>money:
               print("Not enough money")
               print('\n','-'*50,'Transaction failed','-'*50)

           else:
               money-=cost
               print('\n')
               print('You now have $', str(money),'left')
               stocks1[company-1]+=amount1
               print('You have purchased', amount1, companies[company-1],'stocks')
               print('\n','-'*50,'Transaction successful','-'*50)
               print('\n')

       previous_price.clear()
       price_difference.clear()
       price_difference_percent.clear()
       gain_loss_amount.clear()
       gain_loss_name.clear()
       for i in stocks:
           previous_price.append(i)
       stocks.clear()
       day+=1

   else:
       print('Your $1000 is used up')
       day+=1

print('End')
