# EasyFlix Management System - Part 1 Research & Design

---

## INVESTIGATE

### Timeline and Schedule

| **Phase** | **Task** | **Duration** | **Completion %** |
|-----------|----------|--------------|------------------|
| **Phase 1** | **Research & Design** | 3 days | 100% |
| | Problem analysis | 1 day | |
| | Database design & ERD | 1 day | |
| | Interface mockups | 1 day | |
| **Phase 2** | **Development** | 5 days | 100% |
| | Database implementation | 1 day | |
| | Core functions | 1 day | |
| | User interface | 1 day | |
| | Admin interface | 1 day | |
| | Extra buffer time for unexpected delays | 1 day | |
| **Phase 3** | **Testing & Documentation** | 2 days | 100% |
| | System testing | 1 day | |
| | Final documentation | 1 day | |

Phase 1 - Research and design appropriate solution to the problem. Ensure proper planning and infrastructure to build on is created.

Phase 2 - Begin developement, noting down changes and relevant information during the process. Create programs and database.

Phase 3 - Test system and create final documentation on project and how well it solved the issue.

### Problem Outline

EasyFlix is an online media service, they need a software solution for customers so they can create an account, purchase a subscription, rent shows, e.t.c. They also need a solution to track financial information and record sales. This should be done using a software solution that interacts with an SQL database, reading, storing and removing values.

Note: During developement some ideas and names have changed, such as rent --> buy

### Problem Description

EasyFlix has many movies and tv shows available to watch. It offers two subscription levels, basic and premium. Basic users will have access to all movies that are in the basic access group. EasyFlix offers many shows in the basic subscription but some shows may be marked as premium. These premium shows can be rented for an additional cost. Users who purchase the premium subscription will gain access to all basic and premium shows without needing to rent.

The owners need a software solution that allows users to access the EasyFlix catalogue with a subscription and purchase shows. They need to be able to sign up and log in, and interact with the available shows and more.

They also need an admin software solution for managing the users, tracking sales, statistics, finances, adding/removing available shows and changing show access groups.

This all needs to be done with an SQL database to store the values, ensuring optimal and consistent security, integrity and availability of the data.

#### Planned Solutions:

EasyFlixUser is a python-based application designed for users, giving them the ability to do the following;
- Login or Create an account
- Choose or manage subscription level
- Manage their account (Password changes, account termination)
- Browse show catalogue
- Add shows to account
- Rent or return premium shows (if on basic plan)

EasyFlixAdmin is another Python-based application designed for an administrator of EasyFlix to access all aspects of it's media service including;
- User account management (Account creation, password changes, account termination)
- Subscription management (Price changes)
- Media content managment (add movies/tv shows, modify show access group, modify rent price)
- Access general statistics
- Access financial data
- See current rentals
- See past rentals

#### Detailed Requirements

**Programming Requirements:**
- Python 3.x application with SQLite3 database integration
- Clean, professional UI (will use Textual GUI)
- Modular code structure for better maintainability

**Database Requirements:**
- ~Dual database architecture (Separated sensitive data from non-sensitive)~
- Complete data integrity, ensuring data is accurate, complete and consistent
- Database backup ability, ensuring data safety
- Easily available non-sensitive data, authentication required for sensitive data
- Data security all passwords will be stored as a hash using SHA-256 with salt

**Functional Requirements**
- Users able to manage accounts
     - Create account
     - Delete account
     - Change password
     - Change subscription
- Users able to add, rent and return shows
- Users able to access show catalogue
- Admins able to manage catalogue
     - Change show access group
     - Change show rent cost
- Admins able to see rentals, financial statistics, users, overall information
- Data needs to be easily input-able one way or another (will be done automatically through GUI, hence user application)
- Information readily available to authorised parties
- Information readily editable to authorised parties

#### Ethical, Legal and Security Issues
Requirements and things to keep in mind regarding ethics, laws and security

**Security Issues:**
- Password storage must use SHA-256 hashing with unique salts
     - Hashes must be used to protect the passwords in the database in the rare case of a data breach
     - This ensures passwords aren't just released to the internet in a worst case scenario
     - Salts are used to make the cracking process much harder
- Input validation to prevent SQL injection attacks
     - Use proper sanitisation to prevent sql injection and data breaches
     - The API middleman also helps this and dramatically increases security by adding another step
- Administrative access control and session management
     - Proper login details for admins, will also have a stored hash
- All access to sensitive data requires admin authentication
- Secure communication between programs and API
     - The programs may still be sending sensitive data on it's way to the database. Encrypting the communication between the programs and API will put a shield around that information and an especially strong encryption will be a very protective guard against malicious attacks

**Legal Issues:**
- Compliance with data protection regulations for customer data & No storage of advertising data for opted out users
     - Any merketing data should only be collected with consent
     - If consent is withdrawn the information should be removed
- Secure storage of personal information (names, emails)
     - Ties in with security, look after sensitive data properly
- Administrative responsibility for user data management
     - Use of admin controls should be strictly professional and it would even be a good idea to implement guidelines

**Ethical Issues:**
- Responsible handling of customer personal information
     - Ties in with above and security, proper storage and protection for sensitive data
- Transparent subscription and rental cost management
     - All costs are easily readable and presented for easy understanding
- Fair content access based on subscription levels
     - Reasonable show choices and 'moneys-worth' for subscription levels
- Ethical data collection and usage practices
     - User is opted out by default, respect to the user
- Opt in for data sharing
     - As above

#### Data Quality Factors

**Data Accuracy:**
- Input validation to ensure data meets specific criteria
- Format checking (e.g., email addresses, phone numbers)
- Range validation for numerical data
- Required field validation

**Data Consistency:**
- Referential integrity between customers and rentals
- Synchronized statistics and financial totals
- Consistent naming conventions and data formats
- Real-time updates across all related tables

**Data Security:**
- Encrypted password storage for all users
- Database file protection and access control
- Administrative audit trails and logging
- User authentication and authorization

**Data Types and Constraints**
- Proper data type selection (INTEGER, VARCHAR, DATE, etc.)
- Primary key constraints to ensure uniqueness
- Foreign key constraints to maintain referential integrity
- Check constraints to enforce business rules

**Data Entry Controls**
- User interface design that prevents incorrect data entry
- Drop-down menus and selection lists to limit input options
- Data entry training for users

**Database Design**
- Normalization to reduce data redundancy
- Proper table relationships
- Well-defined entity relationships
- Appropriate indexing strategies

**Backup and Recovery**
- Regular automated backups
     - Would be helpful to implement, will add to future features
- Recovery procedures and testing
- Transaction logs
- Disaster recovery planning

**Human Factors**
- User training and education
- Clear data entry procedures
- Error reporting mechanisms
- Quality assurance processes

---

## DESIGN

### OLD DESIGN (THIS WAS REVAMPED IN DEVELOPEMENT)

### Entity Relation Diagram

<img width="1143" height="1952" alt="image" src="https://github.com/user-attachments/assets/b4c1eeb5-f353-4c68-b9ce-578330a4f8c4" />

### Relational Notation

CUSTOMERS(User_ID, Username, Email, Password_Hash, Salt, Subscription_Level, Shows, Rentals, Total_Spent, Opted_In, Favourite_Genre)
Primary Key: User_ID

SHOWS(Show_ID, Name, Release_Date, Rating, Director, Length, Genre, Access_Group, Cost_To_Rent)
Primary Key: Show_ID

RENTALS(Rental_ID, User_ID, Show_ID, Rental_Date, Return_Date, Expired, Cost)
Primary Key: Rental_ID
Foreign Keys: User_ID references CUSTOMERS(User_ID)
             Show_ID references SHOWS(Show_ID)

STATISTICS(Date, Total_Shows_Rented, Total_Subscriptions, Total_Users, Last_Updated)
Primary Key: Date

FINANCIALS(Date, Total_Revenue_Rent, Total_Revenue_Subscriptions, Total_Combined_Revenue, Last_Updated)
Primary Key: Date

### Data Dictionary

#### CUSTOMERS
Stores user account information including authentication details, subscription level, and user preferences. This table contains sensitive customer data requiring secure access.

#### SHOWS
Contains the complete media catalog with show details, ratings, and access control information. This determines what content is available to different subscription tiers.

#### RENTALS
Records all rental transactions, tracking which users have rented which shows, rental periods, and associated costs. Links customers to shows through rental relationships.

#### STATISTICS
Maintains system-wide statistics for administrative reporting and business intelligence. Updated regularly to provide current system metrics.

#### FINANCIALS
Tracks revenue and financial data across all income streams. Critical for business reporting and financial analysis.

### Detailed Field Descriptions

#### CUSTOMERS Table
| Field Name | Data Type | Length | Constraints | Description |
|------------|-----------|---------|-------------|-------------|
| User_ID | INTEGER | - | PRIMARY KEY, NOT NULL | Unique identifier for each customer |
| Username | VARCHAR | 50 | UNIQUE, NOT NULL | User's chosen display name |
| Email | VARCHAR | 100 | UNIQUE, NOT NULL | User's email address for account |
| Password_Hash | VARCHAR | 64 | NOT NULL | SHA-256 hashed password |
| Salt | VARCHAR | 32 | NOT NULL | Unique salt for password hashing |
| Subscription_Level | VARCHAR | 20 | NOT NULL, CHECK IN ('Basic', 'Premium') | User's current subscription tier |
| Shows | TEXT | - | - | List of shows added to user's account |
| Rentals | TEXT | - | - | History of user's rental activity |
| Total_Spent | DECIMAL | 10,2 | DEFAULT 0.00 | Total amount spent by user |
| Opted_In | BOOLEAN | - | DEFAULT FALSE | Indicates whether user has opted in to share data for marketing |
| Favourite_Genre | VARCHAR | 30 | - | User's preferred content genre, NULL unless Opted_In is TRUE |

#### SHOWS Table
| Field Name | Data Type | Length | Constraints | Description |
|------------|-----------|---------|-------------|-------------|
| Show_ID | INTEGER | - | PRIMARY KEY, NOT NULL | Unique identifier for each show |
| Name | VARCHAR | 100 | NOT NULL | Title of the show or movie |
| Release_Date | DATE | - | NOT NULL | Original release date |
| Rating | VARCHAR | 10 | NOT NULL | Content rating (G, PG, M, MA15+, R18+) |
| Director | VARCHAR | 100 | NOT NULL | Director's name |
| Length | INTEGER | - | NOT NULL | Duration in minutes |
| Genre | VARCHAR | 30 | NOT NULL | Primary genre classification |
| Access_Group | VARCHAR | 20 | NOT NULL, CHECK IN ('Basic', 'Premium') | Subscription level required |
| Cost_To_Rent | DECIMAL | 5,2 | NOT NULL | Rental price for basic subscribers |

#### RENTALS Table
| Field Name | Data Type | Length | Constraints | Description |
|------------|-----------|---------|-------------|-------------|
| Rental_ID | INTEGER | - | PRIMARY KEY, NOT NULL | Unique identifier for each rental |
| User_ID | INTEGER | - | FOREIGN KEY, NOT NULL | References CUSTOMERS(User_ID) |
| Show_ID | INTEGER | - | FOREIGN KEY, NOT NULL | References SHOWS(Show_ID) |
| Rental_Date | DATE | - | NOT NULL | Date rental was initiated |
| Return_Date | DATE | - | - | Date rental was returned (NULL if active) |
| Expired | BOOLEAN | - | DEFAULT FALSE | Whether rental period has expired |
| Cost | DECIMAL | 5,2 | NOT NULL | Amount charged for this rental |

#### STATISTICS Table
| Field Name | Data Type | Length | Constraints | Description |
|------------|-----------|---------|-------------|-------------|
| Date | DATE | - | PRIMARY KEY, NOT NULL | Date for which statistics are recorded |
| Total_Shows_Rented | INTEGER | - | DEFAULT 0 | Count of all rental transactions for this date |
| Total_Subscriptions | INTEGER | - | DEFAULT 0 | Count of active subscriptions on this date |
| Total_Users | INTEGER | - | DEFAULT 0 | Count of registered users on this date |
| Last_Updated | DATETIME | - | NOT NULL | Timestamp of last statistics update |

#### FINANCIALS Table
| Field Name | Data Type | Length | Constraints | Description |
|------------|-----------|---------|-------------|-------------|
| Date | DATE | - | PRIMARY KEY, NOT NULL | Date for which financial data is recorded |
| Total_Revenue_Rent | DECIMAL | 10,2 | DEFAULT 0.00 | Total revenue from rentals for this date |
| Total_Revenue_Subscriptions | DECIMAL | 10,2 | DEFAULT 0.00 | Total revenue from subscriptions for this date |
| Total_Combined_Revenue | DECIMAL | 10,2 | DEFAULT 0.00 | Sum of all revenue streams for this date |
| Last_Updated | DATETIME | - | NOT NULL | Timestamp of last financial update |

### Database Queries

#### User Management Queries

1. **Find all premium subscribers**
   - Query the CUSTOMERS table to retrieve all users who have a subscription level of 'Premium'
   - This helps administrators understand their premium customer base

2. **Get customer spending summary**
   - Query the CUSTOMERS table to find users who have spent more than a specified amount
   - Useful for identifying high-value customers and creating loyalty programs

3. **List customers by favorite genre**
   - Query the CUSTOMERS table to group users by their favorite genre
   - Helps with content recommendation and targeted marketing
   - Applies only to customers who opted in to marketing, else those values will be NULL

#### Content Management Queries

4. **Find all shows available to basic subscribers**
   - Query the SHOWS table to retrieve shows where the access group is 'Basic'
   - Used by the user application to display available content for basic users

5. **Get most expensive shows to rent**
   - Query the SHOWS table to find shows with the highest rental costs
   - Helps administrators analyze pricing strategies

6. **List shows by genre and rating**
   - Query the SHOWS table to filter content by both genre and content rating
   - Useful for content curation and parental controls

#### Rental Analysis Queries

7. **Find currently active rentals**
   - Query the RENTALS table to find all rentals where the return date is NULL
   - Shows which rentals are currently active in the system

8. **Calculate total rental revenue for a specific period**
   - Query the RENTALS table to sum up all rental costs within a date range
   - Essential for financial reporting and business analysis

9. **Find customers with overdue rentals**
   - Query the RENTALS table to find rentals where the expired flag is TRUE and return date is NULL
   - Helps with rental management and customer follow-up

#### Complex Relationship Queries

10. **Get customer rental history with show details**
    - Join CUSTOMERS, RENTALS, and SHOWS tables to show complete rental history
    - Provides comprehensive view of customer activity with show information

11. **Find most popular shows by rental count**
    - Join RENTALS and SHOWS tables, group by show and count rentals
    - Identifies trending content and popular titles

12. **Calculate average spending per customer by subscription type**
    - Join CUSTOMERS with RENTALS, group by subscription level and calculate averages
    - Analyzes spending patterns across different subscription tiers

#### Administrative Reporting Queries

13. **Generate monthly revenue report**
    - Query FINANCIALS table to track revenue trends over time
    - Essential for business performance monitoring

14. **Get system usage statistics**
    - Query STATISTICS table to retrieve current system metrics
    - Provides overview of platform growth and usage

15. **Find customers who haven't rented any shows**
    - Use LEFT JOIN between CUSTOMERS and RENTALS to find users with no rental history
    - Identifies users who might need engagement strategies
    - Make sure to only check Basic users
   
16. **Find inactive accounts**
    - Query the CUSTOMERS table to find users with no show history
    - Identifies users who are inactive

#### Security and Maintenance Queries

17. **Verify data integrity between tables**
    - Check that all foreign key relationships are maintained properly
    - Ensures database consistency and prevents orphaned records

#### Time-Based Analysis Queries

18. **Get financial data for a specific date**
   - Query the FINANCIALS table using the Date primary key to retrieve revenue information for a particular day
   - Essential for daily financial reporting and tracking

19. **Find statistics trends over a date range**
   - Query the STATISTICS table to compare user growth and rental activity across multiple dates
   - Useful for identifying business trends and growth patterns

20. **Calculate monthly revenue totals**
   - Query the FINANCIALS table to sum revenue across all days in a specific month
   - Provides monthly financial summaries for business reporting

21. **Track daily user growth**
   - Query the STATISTICS table to show how Total_Users changes day by day
   - Monitors platform growth and user acquisition rates

22. **Find peak rental days**
   - Query the STATISTICS table to identify dates with the highest Total_Shows_Rented
   - Helps identify popular viewing periods and plan capacity

### NEW DESIGN

### Entity Relation Diagram

<img width="1304" height="2457" alt="image" src="https://github.com/user-attachments/assets/efb0f986-ac64-4b12-af5b-3544686433b9" />

## Relational Notation

**ADMIN_CREDENTIALS**(Admin_ID, Username, Password_Hash, Salt, Role, Created_Date)
- Primary Key: Admin_ID

**CUSTOMERS**(User_ID, Username, Email, Password_Hash, Salt, Subscription_Level, Shows, Total_Spent, Favourite_Genre, Marketing_Opt_In)
- Primary Key: User_ID

**SHOWS**(Show_ID, Name, Release_Date, Rating, Director, Length, Genre, Access_Group, Cost_To_Buy)
- Primary Key: Show_ID

**BUYS**(Buy_ID, User_ID, Show_ID, Buy_Date, Cost)
- Primary Key: Buy_ID
- Foreign Keys: User_ID references CUSTOMERS(User_ID), Show_ID references SHOWS(Show_ID)

**STATISTICS**(Date, Total_Shows_Bought, Total_Subscriptions, Premium_Subscriptions, Basic_Subscriptions, Total_Users, Last_Updated)
- Primary Key: Date

**FINANCIALS**(Date, Total_Revenue_Buys, Total_Revenue_Subscriptions, Premium_Subscription_Revenue, Basic_Subscription_Revenue, Total_Combined_Revenue, Last_Updated)
- Primary Key: Date

## Data Dictionary

### ADMIN_CREDENTIALS
Stores administrator account information with secure authentication credentials for admin portal access.

### CUSTOMERS
Contains user account information including authentication details, subscription level, and user preferences. The Shows field stores comma-separated show IDs representing the user's collection.

### SHOWS
Complete media catalog with show details, ratings, and access control information. Access_Group determines subscription level required, Cost_To_Buy applies when basic users purchase premium content.

### BUYS
Records purchase transactions when basic subscribers buy premium shows. Creates transactional history linking customers to purchased shows.

### STATISTICS
Daily system statistics for administrative reporting and business intelligence. Automatically updated with current system metrics.

### FINANCIALS
Daily financial data tracking revenue from subscriptions and purchases. Separates revenue streams for detailed business analysis.

## Detailed Field Descriptions

### ADMIN_CREDENTIALS Table
| Field Name | Data Type | Length | Constraints | Description |
|------------|-----------|---------|-------------|-------------|
| Admin_ID | INTEGER | - | PRIMARY KEY, AUTOINCREMENT | Unique administrator identifier |
| Username | VARCHAR | 50 | UNIQUE, NOT NULL | Admin login username |
| Password_Hash | VARCHAR | 64 | NOT NULL | SHA-256 hashed password |
| Salt | VARCHAR | 32 | NOT NULL | Unique salt for password hashing |
| Role | VARCHAR | 20 | DEFAULT 'admin' | Administrator role designation |
| Created_Date | DATETIME | - | DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |

### CUSTOMERS Table
| Field Name | Data Type | Length | Constraints | Description |
|------------|-----------|---------|-------------|-------------|
| User_ID | INTEGER | - | PRIMARY KEY, AUTOINCREMENT | Unique customer identifier |
| Username | VARCHAR | 50 | UNIQUE, NOT NULL | User's chosen username |
| Email | VARCHAR | 100 | UNIQUE, NOT NULL | User's email address |
| Password_Hash | VARCHAR | 64 | NOT NULL | SHA-256 hashed password |
| Salt | VARCHAR | 32 | NOT NULL | Unique salt for password hashing |
| Subscription_Level | VARCHAR | 20 | NOT NULL, CHECK IN ('Basic', 'Premium') | Current subscription tier |
| Shows | TEXT | - | - | Comma-separated list of show IDs in collection |
| Total_Spent | DECIMAL | 10,2 | DEFAULT 0.00 | Total amount spent including subscriptions |
| Favourite_Genre | VARCHAR | 30 | - | Auto-calculated preferred genre from viewing history |
| Marketing_Opt_In | BOOLEAN | - | DEFAULT 0 | Marketing communication preference |

### SHOWS Table
| Field Name | Data Type | Length | Constraints | Description |
|------------|-----------|---------|-------------|-------------|
| Show_ID | INTEGER | - | PRIMARY KEY, AUTOINCREMENT | Unique show identifier |
| Name | VARCHAR | 100 | NOT NULL | Title of the show or movie |
| Release_Date | DATE | - | NOT NULL | Original release date |
| Rating | VARCHAR | 10 | NOT NULL | Content rating (G, PG, PG-13, R, TV-14, TV-MA, TV-PG) |
| Director | VARCHAR | 100 | NOT NULL | Director's name |
| Length | INTEGER | - | NOT NULL | Duration in minutes |
| Genre | VARCHAR | 30 | NOT NULL | Primary genre classification |
| Access_Group | VARCHAR | 20 | NOT NULL, CHECK IN ('Basic', 'Premium') | Required subscription level |
| Cost_To_Buy | DECIMAL | 5,2 | NULL | Purchase price for basic users (NULL for Basic tier shows) |

### BUYS Table
| Field Name | Data Type | Length | Constraints | Description |
|------------|-----------|---------|-------------|-------------|
| Buy_ID | INTEGER | - | PRIMARY KEY, AUTOINCREMENT | Unique purchase transaction identifier |
| User_ID | INTEGER | - | FOREIGN KEY, NOT NULL | References CUSTOMERS(User_ID) |
| Show_ID | INTEGER | - | FOREIGN KEY, NOT NULL | References SHOWS(Show_ID) |
| Buy_Date | DATE | - | NOT NULL | Date of purchase transaction |
| Cost | DECIMAL | 5,2 | NOT NULL | Amount charged for this purchase |

### STATISTICS Table
| Field Name | Data Type | Length | Constraints | Description |
|------------|-----------|---------|-------------|-------------|
| Date | DATE | - | PRIMARY KEY, NOT NULL | Date for statistics record |
| Total_Shows_Bought | INTEGER | - | DEFAULT 0 | Count of all purchase transactions |
| Total_Subscriptions | INTEGER | - | DEFAULT 0 | Total active subscriptions |
| Premium_Subscriptions | INTEGER | - | DEFAULT 0 | Count of premium subscribers |
| Basic_Subscriptions | INTEGER | - | DEFAULT 0 | Count of basic subscribers |
| Total_Users | INTEGER | - | DEFAULT 0 | Total registered users |
| Last_Updated | DATETIME | - | NOT NULL | Last statistics update timestamp |

### FINANCIALS Table
| Field Name | Data Type | Length | Constraints | Description |
|------------|-----------|---------|-------------|-------------|
| Date | DATE | - | PRIMARY KEY, NOT NULL | Date for financial record |
| Total_Revenue_Buys | DECIMAL | 10,2 | DEFAULT 0.00 | Revenue from show purchases |
| Total_Revenue_Subscriptions | DECIMAL | 10,2 | DEFAULT 0.00 | Revenue from all subscriptions |
| Premium_Subscription_Revenue | DECIMAL | 10,2 | DEFAULT 0.00 | Revenue from premium subscriptions ($80 each) |
| Basic_Subscription_Revenue | DECIMAL | 10,2 | DEFAULT 0.00 | Revenue from basic subscriptions ($30 each) |
| Total_Combined_Revenue | DECIMAL | 10,2 | DEFAULT 0.00 | Sum of all revenue streams |
| Last_Updated | DATETIME | - | NOT NULL | Last financial update timestamp |

## Database Queries

### User Management Queries

1. **Find all premium subscribers**
   - Query the CUSTOMERS table to retrieve users with Premium subscription level
   - Returns user details for premium customer analysis

2. **Get high-value customers**
   - Query CUSTOMERS table filtering by Total_Spent above threshold
   - Orders by spending amount for VIP customer identification

3. **List customers by favorite genre**
   - Query CUSTOMERS table for users with Marketing_Opt_In enabled
   - Groups by Favourite_Genre for targeted marketing campaigns

### Content Management Queries

4. **Get shows available to basic users**
   - Query SHOWS table filtering by Access_Group equals 'Basic'
   - Returns content accessible without additional purchase

5. **Find premium shows with pricing**
   - Query SHOWS table for Premium access group with Cost_To_Buy values
   - Lists purchasable content for basic subscribers

6. **Search shows by multiple criteria**
   - Query SHOWS table with filters for genre, rating, release year, or name
   - Supports advanced content discovery and filtering

### Purchase Analysis Queries

7. **Get user's purchased content**
   - Join BUYS with SHOWS tables filtered by User_ID
   - Returns complete purchase history with show details

8. **Calculate daily purchase revenue**
   - Sum Cost field from BUYS table for specific date
   - Provides daily purchase revenue totals

9. **Find most popular purchased shows**
   - Join BUYS with SHOWS, group by Show_ID, count purchases
   - Identifies trending premium content

### Complex Relationship Queries

10. **Get complete user profile with purchases**
    - Join CUSTOMERS with BUYS and SHOWS tables
    - Returns comprehensive user activity and spending patterns

11. **Find users without purchases**
    - Left join CUSTOMERS with BUYS to find users with no purchase history
    - Identifies potential customers for marketing campaigns

12. **Calculate subscription conversion rates**
    - Compare basic vs premium subscription counts with purchase activity
    - Analyzes subscription tier effectiveness

### Administrative Reporting Queries

13. **Generate current system statistics**
    - Query latest STATISTICS record by Date
    - Provides real-time system metrics dashboard

14. **Create revenue trend analysis**
    - Query FINANCIALS table over date range
    - Shows revenue growth and seasonal patterns

15. **Find inactive user accounts**
    - Query CUSTOMERS for users with empty Shows field
    - Identifies dormant accounts needing engagement

### Financial Analysis Queries

16. **Validate subscription revenue calculations**
    - Cross-reference CUSTOMERS subscription counts with FINANCIALS revenue
    - Ensures financial data accuracy

17. **Track daily revenue breakdown**
    - Query FINANCIALS for subscription vs purchase revenue comparison
    - Shows revenue stream distribution

18. **Calculate average customer value**
    - Average Total_Spent from CUSTOMERS grouped by subscription level
    - Determines customer lifetime value by tier

### Security and Data Integrity Queries

19. **Verify user show collections**
    - Cross-reference CUSTOMERS Shows field with actual BUYS records
    - Ensures data consistency between purchase history and collections

20. **Audit admin access logs**
    - Query ADMIN_CREDENTIALS for recent access patterns
    - Monitors administrative activity for security

