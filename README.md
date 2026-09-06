# TrackedP Project
### Built With
* Python
* SqLite3

## Purpose
TrackedP is a PyQt6 desktop application Windows native study tracker. The application is designed to act as a study timer and track each session throughout the day. Along with the time tracked, the usage of different applications is tracked as well to analyze.
Each study session when completed, has the option to either create review notes or skip over. If the notes is picked, the user can create a title of the session, topic that was covered, location of study session,  and the actual notes. This is used to go over what was done, and act as a "blurt" to emphasize what was learned. This can also help to see if the session was actually covering material or if it was a weak one, this way we can learn what works or not. 

## Study Hub Sections

#### Activity In Depth
This is a small tab that allows the user to the see the total amount of time spent from all the sessions recorded. As of now, it has no filter for any time stamps such as weekly/monthly; but this will be updated in the future.

#### Productivity Performance
This tab is meant to let the users see their past sessions. This is where you can see each title, notes, topic and the applications that were tracked. The tracked sessions is listed with the time and the percentage per the total applications that was tracked. This allows users to see what they studied during certain days or reflect on the session



## How it Works
* **Event Driven Window Tracking** - Uses Win32 "SetWinEventHook" API to detect foreground window changes as they happen, rather than polling internally
* **Background data collection** - A dedicated "QThread" runs a daemon flush thread that periodically writes tracked activity to SQLite , independent from UI
* **Thread-Safe State Sharing** - Shared tracking state is protected with "thread-locking" and "copy.deepcopy" to avoid race conditions
* **Concurrent Safe Storage** - SQLite runs in WAL mode to support safe concurrent reads/writes across thread, SQLite also provides local saving and not needed for over the internet
  
