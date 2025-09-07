#### Click links below for research and evaluation
### [Part 1 - Research and Investigation](https://github.com/ZProLegend007/Project-Data-Management-SQL/blob/main/Part1.md)

## Development notes:
This lists changes to the program since the research stage due to unforseen issues or ideas

### Found issues and solutions:
- **Users should not have access to any data except shows**

  - Usually this would be handled by an API middleman as this would all be server hosted. However instead, the user program will call an 'API' program that will perform checks and authentication such as comparing hashes.
    - This turned out to be a major undertaking but worth it
      
  - Encrypted database to ensure proper security and protection against unauthorised access attempts.
 
- **Users should not be able to _rent_ basic shows**
  - Fixed
  
- **Users should not be able to rent/add the same show more than once**
  - Fixed
  
- **Subscription level should update immediately on account page after being changed**
  - Fixed
  
- **EasyUserFlix is very laggy currently**
  - Will implement more asynchronous tasks and loading symbols
  - Fixed, Originally had over 250 shows for authenticity, now it's around 30. Python doesn't have the performance for that.
 
- **Communication with API may not be secure**
  - Add encrypted communication for sensitive commands
 
#### Notes

In order to make this authentic, and to be able to fully use the API and sql commands, I needed ot make something proper. So I may have gone a little over the top and this was a bad idea especially considering the time I had to do this, but hopefully it's worth it. 

This project should 100% reflect my abilities and understanding of all the topics so far. Especially security, py programming (its a gui in python for goodness sakes), sql and more.

The API (EFAPI) responds to query's in formatted json.

Adding encrypted comminication for auth.
