# Part 2 - Developement Notes and Project Evaluation & Retrospective

## Development notes:
This lists changes to the program since the research stage due to unforseen issues or ideas and general fixes.

### Found issues and solutions:
- **Users should not have access to any data except shows**
  - Usually this would be handled by an API middleman as this would all be server hosted. However instead, the user program will call an 'API' program that will perform checks and authentication such as comparing hashes.
    - This turned out to be a major undertaking but worth it
      - The API will communicate through json with the programs
      - Will add encryption
        - AES, SHA256 with PBKDF2HMAC and 10000 iterations along with base64 encoding
      
  - Encrypted database to ensure proper security and protection against unauthorised access attempts.
    - Hypothetically the whole database could be encrypted in to gibberish txt and then decrypted when needed, then re-encrypted after use with whatever changes. This would protect from database reads as well
 
- **Users should not be able to _rent_ basic shows**
  - Fixed
  
- **Users should not be able to rent/add the same show more than once**
  - Fixed
 
- Renting is no longer a thing, users just buy shows they can't access. Also this is "subscription based" but for the purposes of this assignment, the auto-renewal will not be implemented.
- It is also helpful to know that the statistics and finances that are logged are logged day by day, they will be updated unless it is a new day and then they will start a new column, the data should add on, not log only for that day

THE DATABASE LAYOUT HAS CHANGED IN ORDER TO HAVE A MORE OPTIMISED DATABASE WITH BETTER DATA INTEGRITY

  
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
 
- **BECAUSE TEXTUAL IS RETARDED ON SOME TABS, CLICKING THE SAME TAB TRIGGERING A RELOAD WILL CAUSE A CRASH. IM SO DONE. THERE IS NO FIX FOR THIS. WILL BE A FUTURE IMPROVEMENT.**
  - Fun fact, at 3:28AM I found a fix
  - It's fixed.

#### Notes

In order to make this authentic, and to be able to fully use the API and sql commands, I needed to make something proper. So I may have gone a little over the top and this was a bad idea especially considering the time I had to do this, but hopefully it's worth it. 

This project should 100% reflect my abilities and understanding of all the topics so far. Especially security, py programming (its a gui in python for goodness sakes), sql and more.

The API (EFAPI) responds to query's in formatted json.

This is SO INCREDIBLY PAINFUL. THIS SHOULD HAVE BEEN FINISHED AGES AGO!!! GITHUB KEEPS CRASHING MY CHROME ON LINUX, IN ORDER TO STOP LONG GPU HANGS I AM SOFTWARE RENDERING AND THE STUPID RECALCULATE STATISTICS BUTTON WANTS TO CRASH THE WHOLE PROGRAM NO MATTER WHAT I DO FOR NO APPARENT REASON SO IM JUST GOING TO FREAKING GET RID OF IT (IT SHOULDNT EVEN BE NEEDED TECHNICALLY AS EVERYTHING _SHOULD_ UPDATE AFTER EVERY DATABASE ALTERING FUNCTION FROM THE API). GRRR.

Why do I do this... adding animations.
Nevermind, too hard and dodgy in textual.
Adding encrypted comminication for auth.

I know I'm not being assessed on the GUI but this project will be perfect. **I'm gunning for 100% on this.** 

## Requirements Fulfillment Analysis

### Programming Requirements Assessment

**Python 3.x with SQLite3 Integration**
- Successfully implemented using Python 3.x with comprehensive SQLite3 database operations
- Proper database connection management with error handling
- SQL parameterization to prevent injection attacks

**Clean Professional GUI**
- Implemented using Textual framework for modern terminal-based interface
- Consistent color schemes and responsive design
- Professional layout with proper navigation and feedback systems

**Modular Code Structure**
- Well-organized separation of concerns:
  - `EFAPI.py`: API layer with encryption and database operations
  - `EasyFlixUser.py`: User interface application
  - `EasyFlixAdmin.py`: Administrative interface
  - `init.py`: Database initialization and setup

### Database Requirements Assessment

**Data Integrity**
- Primary key constraints ensure uniqueness
- Foreign key relationships maintain referential integrity
- Check constraints enforce business rules (subscription levels, access groups)
- Automatic statistics updates maintain consistency

**Data Security**
- SHA-256 password hashing with unique salts for each user
- Encrypted database connection (PRAGMA key)
- Encrypted API communication using Fernet encryption with PBKDF2HMAC key derivation
- API-only database access prevents direct user manipulation

**❌ Database Backup Capability**
- Not implemented in current version
- Would require additional file system operations and scheduling
- This would be added in future and would ensure better data integrity

### Functional Requirements Assessment

**User Account Management**
- Account creation with email validation and unique constraints
- Password changes with proper security measures
- Subscription level management with automatic billing
- Account deletion functionality (admin only)

**Content Management**
- Show catalog browsing with search and filtering
- Add/remove shows from user collections
- Purchase system for premium content
- Administrative content management (add/edit/delete shows)

**Administrative Features**
- Comprehensive user management interface
- Financial reporting and statistics tracking
- Purchase history monitoring
- Real-time dashboard with system metrics

## Design Changes from Part 1

### Major Architectural Changes

**1. Database Schema Evolution**
- **Original Design**: Separate RENTALS table with rental periods and return dates
- **Current Design**: BUYS table for permanent purchases
- **Reasoning**: Simplified model and easier to implement for this purpose - users buy content permanently rather than temporary rentals

**2. API Security Layer Addition**
- **Original Design**: Direct database access from applications
- **Current Design**: Encrypted API middleman (EFAPI.py)
- **Reasoning**: Enhanced security, centralized data validation, encrypted communication

**3. Enhanced Financial Tracking**
- **Original Design**: Basic revenue tracking
- **Current Design**: Separate tracking for subscription types and purchase revenue
- **Reasoning**: Better business intelligence and financial analysis capabilities

**4. Marketing Opt-in Implementation**
- **Original Design**: Simple opted-in boolean
- **Current Design**: Marketing_Opt_In with automatic favorite genre calculation
- **Reasoning**: Privacy compliance and intelligent data collection

### Field-Level Changes

| Table | Original Field | Current Field | Reason |
|-------|---------------|---------------|---------|
| SHOWS | Cost_To_Rent | Cost_To_Buy | Changed from rental to purchase model |
| CUSTOMERS | Opted_In | Marketing_Opt_In | Clearer field naming |
| CUSTOMERS | Rentals | Buys | Buys now represent owned content |
| STATISTICS | Total_Shows_Rented | Total_Shows_Bought | Reflects purchase model |

### New Tables Added

**ADMIN_CREDENTIALS**
- Added for secure administrative access
- Separate from customer authentication for security isolation

**Enhanced STATISTICS and FINANCIALS**
- Added separate tracking for Basic/Premium subscriptions
- More granular revenue reporting capabilities

## Product Improvements and Limitations

### Current Limitations

**1. Performance Limitations**
- Single-threaded database operations may cause UI blocking
- Large datasets could impact search and filtering performance
- No database indexing implemented for optimization

**2. Security Considerations**
- Admin credentials are hardcoded in source code
- No session timeout implementation
- Limited audit logging for administrative actions

**3. User Experience Issues**
- No bulk operations for administrative tasks
- Limited error recovery mechanisms
- Interface can crash if same navigation tab is clicked repeatedly (Textual framework limitation)

**4. Business Logic Gaps**
- No subscription renewal system
- No content recommendation engine
- Limited reporting date range selection

### Proposed Improvements

**1. Performance Enhancements**
```python
# Add database indexing
CREATE INDEX idx_customers_subscription ON CUSTOMERS(Subscription_Level);
CREATE INDEX idx_shows_access_group ON SHOWS(Access_Group);
CREATE INDEX idx_buys_user_date ON BUYS(User_ID, Buy_Date);
```

**2. Security Improvements**
- Environment variable configuration for database credentials
- Session management with automatic timeout
- Enhanced audit logging system
- Two-factor authentication for admin accounts

**3. Feature Additions**
- Advanced reporting with date range selection
- Content recommendation based on viewing history
- Bulk administrative operations
- Automated backup system
- Email notification system

**4. Technical Improvements**
- Database connection pooling
- Caching layer for frequently accessed data
- Improved error handling and recovery
- Unit testing framework implementation

### Known Bugs

**1. Interface Stability**
- Clicking the same navigation tab multiple times could (past, however still on user application) cause application crash
- Some fixes and protections have been implemented, but rapid switching can also trigger crashes
- **Cause**: Textual framework limitation with event handling
- **Workaround**: User education and interface design to discourage duplicate clicks (lol)

**2. Data Validation**
- Limited client-side validation for date formats
- **Impact**: May cause server-side errors with invalid dates
- **Solution**: Enhanced input validation on both client and server sides

**3. Concurrency Issues**
- No handling for simultaneous administrative modifications
- **Risk**: Data inconsistency with multiple admin users
- **Solution**: Implement database locking mechanisms

## Development Process Evaluation

### Successful Methodologies

**1. Iterative Development**
- Modular approach allowed for independent component development
- Regular testing during development prevented major integration issues
- Flexible architecture accommodated changing requirements

**2. Security-First Design**
- Early implementation of encryption and authentication prevented security debt
- API layer architecture provided natural security boundaries
- Consistent security practices across all components

**3. Documentation and Planning**
- Comprehensive initial design provided clear development roadmap
- Regular documentation updates maintained project clarity
- Database schema documentation facilitated implementation

### Development Challenges

**1. Framework Learning Curve**
- Textual framework required significant learning investment
- Complex event handling and async operations
- Limited community resources and examples

**2. Scope Creep**
- Security requirements expanded significantly during development
- Performance optimization needs emerged during testing
- Additional features requested beyond original scope

**3. Integration Complexity**
- Encrypted communication between components added complexity
- Database initialization and setup required careful coordination
- Error handling across multiple application layers

### Future Development Recommendations

**1. Technology Stack Considerations**
- Consider web-based interface for better cross-platform compatibility
- Evaluate more mature GUI frameworks for desktop applications
- Implement proper logging framework for debugging and monitoring

**2. Development Process Improvements**
- Implement continuous integration/deployment pipeline
- Add comprehensive unit and integration testing
- Establish code review processes for security-critical components

**3. Scalability Planning**
- Design for horizontal scaling with multiple database instances
- Implement caching strategies for improved performance
- Consider microservices architecture for large-scale deployment

## Future Impact Assessment

### Business Value Potential

**1. Operational Efficiency**
- Automated statistics tracking reduces manual reporting overhead
- Centralized user management streamlines customer service
- Real-time financial tracking enables better business decisions

**2. Scalability Opportunities**
- Modular architecture supports feature expansion
- API design allows for third-party integrations
- Database structure accommodates additional content types

**3. Compliance and Security**
- Privacy-compliant data collection practices
- Secure authentication and authorization systems
- Audit trails for regulatory compliance

### Technical Evolution Path

**1. Short-term Enhancements (3-6 months)**
- Performance optimization and indexing
- Enhanced error handling and user feedback
- Mobile application development using API layer

**2. Medium-term Development (6-12 months)**
- Advanced analytics and reporting dashboard
- Content recommendation engine implementation
- Multi-tenant architecture for franchise operations

**3. Long-term Vision (1-2 years)**
- Cloud deployment with auto-scaling capabilities
- Integration with external payment systems
- Advanced AI-driven content curation

### Industry Impact Considerations

**1. Competitive Advantages**
- Privacy-first approach differentiates from data-heavy competitors
- Modular architecture enables rapid feature development
- Secure-by-design principles build customer trust

**2. Market Positioning**
- Suitable for small to medium streaming services
- Educational institutions for content management
- Corporate training platforms

**3. Technology Trends Alignment**
- Privacy regulations compliance (GDPR, CCPA)
- Encrypted communication standards
- Modern terminal-based interfaces for developer tools

## Conclusion

The EasyFlix Management System successfully addresses the core requirements identified in Part 1, with significant enhancements in security and architecture. The transition from a rental-based to purchase-based model, along with the implementation of a secure API layer, represents thoughtful adaptation to real-world constraints and security requirements.

While the system demonstrates solid foundational architecture and security practices, there remain opportunities for performance optimization, feature enhancement, and user experience improvements. The modular design and comprehensive API structure provide a strong foundation for future development and scaling.

The development process highlighted the importance of security-first design and iterative development methodologies, while also revealing the challenges of framework selection and scope management in complex software projects.

**Overall Assessment**: The solution effectively meets business requirements while establishing a robust foundation for future enhancement and scaling.
