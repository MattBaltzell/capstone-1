### Capstone 1 Project Proposal

# **Find Musicians App**

In past years, musicians were able to visit their local guitar shops or music stores to socialize with other musicians, post ads on the bulletin boards, and find collaborations by being in the local music scene. While this method still works for some musicians, the popularity of music genres can differ greatly from city to city, making it difficult for many musicians to find their fit.

## Project Goals

The Find Musicians App allows musicians and bands to search within their desired genres for other musicians in an area. While the main goal is to help users locate nearby musicians, the app also aims to bring a social aspect to the local music scene.

---

## User Demographics

Any local musicians and bands can benefit from using the Find Musicians App, but the main target demographic are those that play less popular genres of music for their area. For example, a hard rock guitarist that lives in an area where country music is the primary genre in the music scene.

---

## Data and API Usage

### **Geolocation**
This app will make use of the **Google Maps API** or something similar in order to help users locate musicians. Users will be able to:
- Search for musicians within a distance radius. 
- Search for musicians within a specific location in the US.

### **Chat/Messaging** (if time permits)
Chat and messaging will play an important role in the social aspect of this app, as users will need a way to communicate with others. Therefore, the app will also use **Telegram API** or something similar to create fast and reliable direct messaging between users.

---

## Project Approach

My approach for creating the Find Musicians App will be to develop an MVP focused on the geolocation features first, and then adding the messaging features as the app evolves.

### **Database Schema**
Database models will consist of the following: 
- User
- Instrument
- Genre
- Connections

The Instrument, Genre, and Connection models will have many-to-many relationships with the User model.  

![database schema](/database-schema_FM.png)

### **Potential Issues**
1. This should not be an issue, but if enough calls are made to the Google maps api, Google would start charging my card. If this happens, I will monitor and disable the search features for the rest of the month if charges get too high.
2. There's always a chance that an API can go down. Google downtime is usually very short. Telegram outages and slowdowns happen occasionally, and will be something to look out for.

### **Security & Sensitive Information**
- User email addresses will be stored for registering a new user. 
- Password security will be handled with Bcrypt.
- Only a User's City and State will be used to locate musicians. Therefore, User addresses and precise locations will not be available. 
- Telegram prioritizes security and privacy. Read more in the [Telegram Privacy Policy](https://telegram.org/privacy). I am currently researching alternative messaging/chat apis to see if there is an even more secure option.
- The app does not have any payment features to worry about.

### **Functionality**
- Audio playback
- Audio uploads
- Clean UI
- Connection requests
- Custom news feeds based on connections (time permitting)
- Geolocation/Mapping Distances
- Image uploads
- Messaging/Comments
- Search
- Simple Navigation 

### **User Flow**
User Searching for Musician
![user flow diagram](/user-flow_FM.png)

### **Stretch Goals**
1. Adding a chat feature (with Telegram)
2. Custom news feeds based on connections
3. Push Notifications
