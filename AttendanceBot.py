# How to use
# Enter : Token/ChatID/ICSurl.
# Note : Within the same team, you can share URLs, but across teams with different schedules, not so much

# lets store our chatID and Token and telegram handle ---------------------------------------------------------

Token = "ENTER YOUR TOKEN"
ChatID = "ENTER YOUR CHATID" # This is the group chat ID

# Lets store our NTU calendar link, email and password ------------------------------------------

url = "ENTER YOUR ICS URL"


# Lets import our standard modules ------------------------------------------------------------------------

from datetime import datetime, timezone, timedelta
import icalendar
import urllib.request
import time
import random
import traceback

# Lets import our telegram modules ---------------------------------------------------------------

import requests # Note, we will not be using pythontelegrambot, it is too difficult for me
                # instead, we will use a simple web requester that goes to the telegram website 
                # and controls the bot from there instead

# lets define our send message function 

def Send_Message(message):
    try :
        url = f"https://api.telegram.org/bot{Token}/sendMessage"
        requests.post(url, json={"chat_id": ChatID, "text": message})
    except Exception as Telegram_Error :
        print(Telegram_Error)
        time.sleep(20)

# Here is a program that will randomize our ping and refresh timings -------------------------
def RandomSleepTiming():
    sleep_time = random.randint(240,480)
    return sleep_time

    # Now lets Define our main loop of code ---------------------------------------------------------
    # This loop will check if there is any lessons going on every 5 minutes ------------------------
    # if there is a lesson, it will attempt to mark attendance -------------------------------------
 
Time_Since_Calendar_Data_Last_Grabbed = datetime.now(timezone.utc) - timedelta(days=2) # to rate limit calendar downloads (this got me banned before)

while True :
    try :
        time.sleep(RandomSleepTiming())

        # Lets grab our calendar data (only once every 2 days MAX)
        elapsed = datetime.now(timezone.utc) - Time_Since_Calendar_Data_Last_Grabbed
        if  elapsed > timedelta(days=2) :

            req = urllib.request.Request(
                url,
                headers=({"User-Agent": "Mozilla/5.0"})
            )
            with urllib.request.urlopen(req) as response:
                calendar_data = response.read()
            print("Calendar data grabbed")
            Time_Since_Calendar_Data_Last_Grabbed = datetime.now(timezone.utc)

        # then lets feed the data into the calendar module
        calendar = icalendar.Calendar.from_ical(calendar_data) # we cannot directly feed the url as the calendar module does not support it

        # Lets take the current time
        now = datetime.now(timezone.utc)

        # lets check if there is currently any events, and grab its metadata
        for event in calendar.events:
            Start_Time = event.get("DTSTART").dt #.dt functions to format the time appropriately
            End_Time = event.get("DTEND").dt
            summary = event.get("SUMMARY")
            Location = event.get("location")
            description = event.get("DESCRIPTION")
            Link_To_Event = event.get("URL")
            if now < End_Time and now > Start_Time :
                time.sleep(300) # Note, this time delay is purposely added on the request of a teammate, saying that if the reminder is sent too close to the Irat, they miss the notification
                print("The current event is", summary,"and it is located at", Location)
                Send_Message(f"The current event is {summary} and it is located at {Location}")
                if "ATTENDANCE: Optional" in description :
                    Send_Message("Attendance is OPTIONAL for this event")
                else :
                    Send_Message(f"Remember to mark your attendance at {Link_To_Event}")
                Time_Until_End_of_Event = End_Time - now
                Seconds_Until_End_of_Event = Time_Until_End_of_Event.total_seconds()
                time.sleep(Seconds_Until_End_of_Event) #the bot will rest until the event ends
                break
        else : # If there is no event, lets go back to the start of the loop
            print("there are no events occuring right now ")
            continue # this will send us back to the start of this while loop
    except Exception as error :
        print(f"Some error occured during the execution of the code {error}")
        traceback.print_exc()
        print("The loop will restart ")
        # Note, no error messages will be sent to telegram!
        time.sleep(120)

