import os
import uvicorn.config as uvicorn
from tbmail.database import Database
from tbmail.user import User
from tbmail.mail import Mail
from trollbot import Bot
import contextlib, threading, time, math, uvicorn

bot = Bot('TBMail (?)', 'lime', '?', False)
db = Database()

helpmsg = '''TBMail Resurrected Beta
This is NOT the official tbmail, but instead a remake by mewhenthe.
I promise not to do any funny stuff

?help - Shows this message, <required> [optional]
?about - Obtain additional information.
?register <address@tbmail> - Registers a new account
?send <recipient> <message...> - Send mail to somebody
?togglewelcome - Toggles welcome message
?inbox [page] - Read inbox
?view <index> - Lets you read a mail
?link <code> - Link your tbmail to an external password, this is recommended
?recover <code> - Recover your tbmail account, your account must be linked to do this

--- WIP ---
There is no dashboard on the website.
-----------'''

welcomemsg = '''Welcome back, &user.
You have &count unread mail&edgecase.
You can disable this welcome message with ?togglewelcome.
'''

aboutmsg = '''This bot is a recreation/resurrection of TBMail.
TBMail was, on the surface, a normal mail service designed for trollbox.
However, the creator of TBMail exploited the popularity of TBMail to spread malware.
This remake is unofficial and therefor will attempt to avoid such behaviour.

Front-end website used for linking and recovery: http://tbmail.codersquack.nl 
Github repository: https://github.com/mewhenthegit/tbmail 

made by mewhenthe
'''

@bot.event("ready")
def ready():
    print("Joined atrium")
@bot.event("user join")
def join(tbuser):
    user = User.search(db, home = tbuser.home)
    if not user or not user.welcoming or tbuser.nick == bot.name:
        return
    
    unreadmails = Mail.search(db, receiver = user.username, read = False)
    msg = welcomemsg.replace('&user', tbuser.nick).replace('&count', str(len(unreadmails))).replace('&edgecase', '' if len(unreadmails) == 1 else 's')
    bot.send(msg)

@bot.unknown_command
def unknown_command(ctx, cmd):
     bot.send(f"Unknown command {cmd}!")

@bot.command()
def help(ctx):
    bot.send(helpmsg)

@bot.command()
def about(ctx):
    bot.send(aboutmsg)

@bot.command()
def recover(ctx, code):
    db.load()
    
    if not code in db.data["recovercodes"].keys():
        bot.send("Invalid recovery code!")
        return

    address = db.data["recovercodes"][code]
    del db.data["recovercodes"][code]
    db.write()

    user = User.search(db, home=ctx.user.home)
    if user:
         bot.send("You already have an account!")
         return
    
    user = User.search(db, username=address)
    user.home = ctx.user.home
    idx, user = user.serialize()
    db.data["users"][idx] = user
    db.write()

    bot.send("Account recovered succesfully!")

@bot.command()
def link(ctx, code):
    db.load()
    
    if not code in db.data["linkcodes"].keys():
        bot.send("Invalid link code!")
        return

    passwd = db.data["linkcodes"][code]
    del db.data["linkcodes"][code]
    db.write()

    user = User.search(db, home=ctx.user.home)
    if not user:
         bot.send("You do not have an account!")
         return
    
    user.password = passwd
    idx, user = user.serialize()
    db.data["users"][idx] = user
    db.write()

    bot.send("Account linked!")

@bot.command()
def send(ctx, recipient, *message):
    msg = ' '.join(message)
    user = User.search(db, username = recipient)
    if not user:
        bot.send('Recipient does not exist!')
        return
    
    user = User.search(db, home = ctx.user.home)
    if not user:
        bot.send("You are not registered")
        return
    
    mail = Mail(None, user.username, recipient, msg, False)
    _, rawmail = mail.serialize()
    db.data["mails"].append(rawmail)
    db.write()
    bot.send("Mail sent!")

@bot.command()
def togglewelcome(ctx):
    user = User.search(db, home=ctx.user.home)
    if not user:
        bot.send("You're not registered!")
        return
    
    user.welcoming = not user.welcoming
    idx, data = user.serialize()
    db.data["users"][idx] = data
    db.write()
    bot.send(f"Welcome message has been set to: {user.welcoming}")

@bot.command()
def inbox(ctx, page=1):
    page = int(page)
    user = User.search(db, home=ctx.user.home)
    if not user:
        bot.send("You're not registered!")
        return
    
    inboxmsg = f"================{ctx.user.nick}'s inbox================\n\n"
    mails = Mail.search(db, receiver = user.username)
    pagecount = math.ceil(len(mails) /5)

    if page > pagecount and pagecount > 0:
        bot.send("That page does not exist!")
        return
    
    digestion = 5 if page < pagecount else len(mails) - (page -1) * 5

    if pagecount > 0: # lazy and it sucks but who cares
        for i in range((page-1)*5, (page-1)*5+digestion):
            mail = mails[i]
            truncate = mail.body[0:12]+"..." if len(mail.body)>15 else mail.body
            inboxmsg += f"[{i}]{' *NEW*' if not mail.read else ''} {mail.sender}: {truncate}\n"

    if pagecount == 0: pagecount = 1
    inboxmsg += f"\npage {page}/{pagecount}\nUse ?view <index> to view an email in full"
    bot.send(inboxmsg)

@bot.command()
def view(ctx, index):
    index = int(index)
    user = User.search(db, home=ctx.user.home)
    if not user:
        bot.send("You're not registered!")
        return

    mails = Mail.search(db, receiver=user.username)
    if index >= len(mails):
        bot.send('Mail does not exist!')

    mail = mails[index]
    bot.send(f"==============================\nSender: {mail.sender}\nRecipient: {mail.receiver}\n\n{mail.body}")
    mail.read = True
    idx, data = mail.serialize()
    db.data['mails'][idx] = data
    db.write()

@bot.command()
def register(ctx, address):
    if not address.endswith('@tbmail'):
        bot.send('Your address must end with @tbmail!')
        return 
    
    if address.split('@')[0] == '':
        bot.send('bruh')
        return
    
    if len(address.split('@')) > 2:
        bot.send('You cannot have more than one @ in your mail address!')
        return 
    user = User.search(db, username = address)
    if user:
        bot.send('Address is already taken!')
        return 
    user = User.search(db, home = ctx.user.home)
    if user:
        bot.send('You are already logged into an account!')
        return 
    
    user = User(None, address, None, True, ctx.user.home)
    _, serialized = user.serialize()
    db.data['users'].append(serialized)
    db.write()
    
    bot.send('Registered!')

 
# VOODOO SHIT ALERT!
def register_error(ctx, error):
    bot.send('You have supplied an incorrect amount of arguments!')
    print(error, str(error))

bot.error('register')(register_error)
bot.error('send')(register_error)
bot.error('togglewelcome')(register_error)
bot.error('inbox')(register_error)
bot.error('view')(register_error)
bot.error('link')(register_error)
bot.error('recover')(register_error)
bot.error('about')(register_error)

class Server(uvicorn.Server):
	def install_signal_handlers(self):
		pass

	@contextlib.contextmanager
	def run_in_thread(self):
		thread = threading.Thread(target=self.run)
		thread.start()
		try:
			while not self.started:
				time.sleep(1e-3)
			yield
		finally:
			self.should_exit = True
			thread.join()

# uconfig = uvicorn.Config("tbmail.api:app", host="0.0.0.0", port=8000, reload=True)
# server = Server(config=uconfig)

def run():
    bot.connect(blocking=False)
    uvicorn.run("tbmail.api:app", host='0.0.0.0', port=5004, reload=True)
    # with server.run_in_thread():
    #     bot.connect()