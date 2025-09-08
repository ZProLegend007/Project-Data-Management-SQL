#### Click links below for research and evaluation
### [Part 1 - Research and Investigation](https://github.com/ZProLegend007/Project-Data-Management-SQL/blob/main/Part1.md)

## Development notes:
This lists changes to the program since the research stage due to unforseen issues or ideas and general fixes.

### Found issues and solutions:
- **Users should not have access to any data except shows**
  - Usually this would be handled by an API middleman as this would all be server hosted. However instead, the user program will call an 'API' program that will perform checks and authentication such as comparing hashes.
    - This turned out to be a major undertaking but worth it
      - The API will communicate through json with the programs
      - Will add encryption 
      
  - Encrypted database to ensure proper security and protection against unauthorised access attempts.
 
- **Users should not be able to _rent_ basic shows**
  - Fixed
  
- **Users should not be able to rent/add the same show more than once**
  - Fixed
 
- Renting is no longer a thing, users just buy shows they can't access. Also this is "subscription based" but for the purposes of this assignment, the auto-renewal will not be implemented.
- It is also helpful to know that the statistics and finances that are logged are logged day by day, they will be updated unless it is a new day and then they will start a new column, the data should add on, not log only for that day

- **THE DATABASE LAYOUT HAS CHANGED IN ORDER TO HAVE A MORE OPTIMISED DATABASE WITH BETTER DATA INTEGRITY**
  - 
  
- **Subscription level should update immediately on account page after being changed**
  - Fixed
  
- **EasyUserFlix is very laggy currently**
  - Will implement more asynchronous tasks and loading symbols
  - Fixed, Originally had over 250 shows for authenticity, now it's around 30. Python doesn't have the performance for that.
 
- **Communication with API may not be secure**
  - Add **fully** encrypted communication between programs and API
    - Should be relatively simple, just modify the main connection method

- **When a user opts out of marketing, their data is still in the database**
  - Ensure marketing data is cleared on opt out
 
#### Notes

In order to make this authentic, and to be able to fully use the API and sql commands, I needed to make something proper. So I may have gone a little over the top and this was a bad idea especially considering the time I had to do this, but hopefully it's worth it. 

This project should 100% reflect my abilities and understanding of all the topics so far. Especially security, py programming (its a gui in python for goodness sakes), sql and more.

The API (EFAPI) responds to query's in formatted json.

This is SO INCREDIBLY PAINFUL. THIS SHOULD HAVE BEEN FINISHED AGES AGO!!! GITHUB KEEPS CRASHING MY CHROME ON LINUX, IN ORDER TO STOP LONG GPU HANGS I AM SOFTWARE RENDERING AND THE STUPID RECALCULATE STATISTICS BUTTON WANTS TO CRASH THE WHOLE PROGRAM NO MATTER WHAT I DO FOR NO APPARENT REASON SO IM JUST GOING TO FREAKING GET RID OF IT (IT SHOULDNT EVEN BE NEEDED TECHNICALLY AS EVERYTHING _SHOULD_ UPDATE AFTER EVERY DATABASE ALTERING FUNCTION FROM THE API). GRRR.

Adding encrypted comminication for auth.

I know I'm not being assessed on the GUI but this project will be perfect. **I'm gunning for 100% on this.** 
