from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset, ReminderScheduled
import json
import os
import datetime

with open(os.path.realpath(os.path.join(os.getcwd(), 'users.txt'))) as f:
    data = f.read()
USERS = json.loads(data)
print(USERS)

global u
u = None

def U_update():
    with open(os.path.realpath(os.path.join(os.getcwd(), 'users.txt')), 'w') as convert_file:
        convert_file.write(json.dumps(USERS))
        
def user_set(tracker, dispatcher):
    global u
    user = tracker.get_slot("user")
    print("\nUser:",user)
    if user in USERS:
        dispatcher.utter_message(text=f"Welcome back {user}")
    else:
        dispatcher.utter_message(text=f"Nice to meet you {user}")
        USERS[user] = {}
        U_update()
    u = user
    print(u)

class ActionIdentify(Action):
    
    def name(self) -> Text:
        return "action_identify"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
        user_set(tracker, dispatcher)
        return [AllSlotsReset(), SlotSet("user", u), SlotSet("reminder", "unset")]
        
class ActionAdd(Action):
    
    def name(self) -> Text:
        return "action_add"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
        global u
        print(u)
        if u is None:
            user_set(tracker, dispatcher)
        acname = tracker.get_slot("acname")
        deadline = tracker.get_slot("deadline")
        category = tracker.get_slot("category")
        reminder = tracker.get_slot("reminder")
        print("\nAction:",acname)
        print("Deadline:",deadline)
        print("Category:",category)
        print("Reminder:",reminder)
        if acname in USERS[u]:
            dispatcher.utter_message(text="Sorry, the action is already registered")
        else:
            dispatcher.utter_message(text=f"Added action: {acname}")
            USERS[u][acname] = [deadline, category, reminder]
            U_update()
            if reminder == 'Set':
                date = datetime.datetime.strptime(deadline, "%d/%m/%Y %H:%M")
                #date = date.timestamp()
                entities = tracker.latest_message.get("entities")
                reminder = ReminderScheduled(
                    "EXTERNAL_reminder",
                    trigger_date_time=date,
                    entities=entities,
                    name=acname+"_reminder",
                    kill_on_user_message=False
                )
                return [AllSlotsReset(), SlotSet("user", u), SlotSet("reminder", "unset"), reminder]
        return [AllSlotsReset(), SlotSet("user", u), SlotSet("reminder", "unset")]
        
class ActionShow(Action):
    
    def name(self) -> Text:
        return "action_show"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
        global u
        print(u)
        if u is None:
            user_set(tracker, dispatcher)
        if len(USERS[u]) == 0:
            dispatcher.utter_message(text="Sorry, you have no plans")
        else:
            d = USERS[u]
            tmp = {}
            for i in d.keys():
                tmp[i] = datetime.datetime.strptime(d[i][0], "%d/%m/%Y %H:%M")
            sd = dict(sorted(tmp.items(), key=lambda item: item[1]))
            for i in sd.keys():
                dispatcher.utter_message(text=f"{i} - {d[i][0]} - {d[i][1]} - Reminder:{str(d[i][2])}")
        return [AllSlotsReset(), SlotSet("user", u), SlotSet("reminder", "unset")]
        
class ActionRemove(Action):
    
    def name(self) -> Text:
        return "action_remove"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
        global u
        print(u)
        if u is None:
            user_set(tracker, dispatcher)
        acname = tracker.get_slot("acname")
        print("\nAction:",acname)
        if acname not in USERS[u]:
            dispatcher.utter_message(text="Sorry, the action is not registered")
        else:
            dispatcher.utter_message(text=f"Removed action: {acname}")
            USERS[u].pop(acname)
            U_update()
        return [AllSlotsReset(), SlotSet("user", u), SlotSet("reminder", "unset")]
        
class ActionEditCategory(Action):
    
    def name(self) -> Text:
        return "action_edit_category"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
        global u
        print(u)
        if u is None:
            user_set(tracker, dispatcher)
        acname = tracker.get_slot("acname")
        category = tracker.get_slot("category")
        print("\nAction:",acname)
        print("Category:",category)
        if acname not in USERS[u]:
            dispatcher.utter_message(text="Sorry, the action is not registered")
        else:
            dispatcher.utter_message(text=f"Updated action: {acname} with {category}")
            USERS[u][acname][1] = category
            U_update()
        return [AllSlotsReset(), SlotSet("user", u), SlotSet("reminder", "unset")]
        
class ActionEditDeadline(Action):
    
    def name(self) -> Text:
        return "action_edit_deadline"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
        global u
        print(u)
        if u is None:
            user_set(tracker, dispatcher)
        acname = tracker.get_slot("acname")
        deadline = tracker.get_slot("deadline")
        print("\nAction:",acname)
        print("Deadline:",deadline)
        if acname not in USERS[u]:
            dispatcher.utter_message(text="Sorry, the action is not registered")
        else:
            dispatcher.utter_message(text=f"Updated action: {acname} with {deadline}")
            USERS[u][acname][0] = deadline
            U_update()
        return [AllSlotsReset(), SlotSet("user", u), SlotSet("reminder", "unset")]
        
class ActionUnidentify(Action):
    
    def name(self) -> Text:
        return "action_unidentify"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
        dispatcher.utter_message(text="It's been a pleasure. Goodbye!")
        global u
        u = None
            
        return [AllSlotsReset(), SlotSet("reminder", "unset")]
        
class ActionReactReminder(Action):
    
    def name(self) -> Text:
        return "action_react_reminder"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
        global u
        name = tracker.get_slot("user")
        act = tracker.get_slot("acname")
        if name == u:
            dispatcher.utter_message(f"Hey {name}, it's time for {act}!")
            
        return [AllSlotsReset(), SlotSet("user", u), SlotSet("reminder", "unset")]
  
