# Hook - Find Musicians

Hook allows musicians to easily locate and communicate with other musicians or bands within a given search radius. Currently, this app is for portfolio purposes only. The API used is on a free plan and limited to only 10 API calls per hour, and it does not use a CDN to store image uploads. I hope to continue development on this project and eventually get it to a point where it can be used as an actual tool to help musicians in the future.

## Deployed Website
You can view the deployed app at [Hook Musician Finder](https://hook-musician-finder.herokuapp.com/). 

## User Flow

### Sign Up:
Sign up with Username, Email, Password, and Location. Your password is hashed using bcrypt.

### Update Profile:
You can update your profile with a cover image and profile image to show off your style. Choose which instruments you can play as well as your favorite genres. Add a bio with your musical goals, past musical experiences, and more in order to help other users decide if you would be a good match.

### Search For Musicians or Bands:
The main priority of this app is to give users the ability to find musicians and bands nearby. To get started on the search page, you can choose whether to search for a musician or band. Then select an instrument and a genre. Finally, type in a zip code and choose a search radius and a list of users fitting your criteria will appear in the search results after submitting. From there you can view their profiles to see if they would be a good fit.

### Follow and Message Others:
Once you visit another user's profile you can choose to follow them, which will add them to the "Following" list you can access from your own profile. You also have the ability to send them a message. Fill out the subject line and message and send. A message notification will be sent to that user in the 'Messages' tab of the header.

## External Api:
This app uses the [ZipCodeAPI](https://www.zipcodeapi.com/API#radius). On the search page, a user can type in a zip code and choose a search radius. This API uses these two parameters to create a list of zip codes within the given radius of the zip code.

The app also uses [SlimSelectjs](https://slimselectjs.com/) to enhance the select fields throughout.

## Technology Stack:
PostgreSQL, Flask, Python, JavaScript 
