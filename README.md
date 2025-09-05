#### Click links below for research and evaluation
### [Part 1 - Research and Investigation](https://github.com/ZProLegend007/Project-Data-Management-SQL/blob/main/Part1.md)

## Development notes:
This lists changes to the program since the research stage due to unforseen issues or ideas

### Found issues and solutions:
- **Users should not have access to any data except shows**

  - Usually this would be handled by an API middleman as this would all be server hosted. However instead, the user program will call an 'API' program that will perform checks and authentication such as comparing hashes.
  - Encrypted database to ensure proper security and protection against unauthorised access attempts.
 
- **Users should not be able to _rent_ basic shows**
  
- **Users should not be able to rent/add the same show more than once**
  
- **Subscription level should update immediately on account page after being changed**
  
- **EasyUserFlix is very laggy currently**
  - Will implement more asynchronous tasks and loading symbols
