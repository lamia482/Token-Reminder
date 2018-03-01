# Token-Reminder
read values of tokens(eth, btc...) from https://www.coingecko.com and remind when necessary

1. replace or add your tokens and the remind limit in the main function
2. replace your sending email address and password in send_email() with the code: 
   msg['From'] = address_here       and 
   s.login(msg['From'], password_here)
3. replace your recieve email address  in the main function with the code:
   reminder = MinerNotaficator(website, address_here, 5)

This reminder will auto-send email every day which records the token values and timestamp, 
and will remind when reachs limit
