# EasyFlix Management System - Part 1 Research & Design

---

Parts of this will be updated and done relevant to the final project in part 2, so if it is not up to par for full marks in a section check over there for anything that may be missing.

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

### Problem Outline

EasyFlix is an online media service, they need a software solution for customers so they can create an account, purchase a subscription, rent shows, e.t.c. They also need a solution to track financial information and record sales. This should be done using a software solution that interacts with an SQL database, reading, storing and removing values.

### Problem Description

EasyFlix has many movies and tv shows available to watch. It offers two subscription levels, basic and premium. Basic users will have access to all movies that are in the basic access group. EasyFlix offers many shows in the basic subscription but some shows may be marked as premium. These premium shows can be rented for an additional cost. Users who purchase the premium subscription will gain access to all basic and premium shows without needing to rent.

The owners need a software solution that allows users to access the EasyFlix catalogue with a subscription and purchase shows. They need to be able to sign up and log in, and interact with the available shows and more.

They also need an admin software solution for managing the users, tracking sales, statistics, finances, adding/removing available shows and changing show access groups.

This all needs to be done with an SQL database to store the values, ensuring optimal and consistent security, integrity and availability of the data.

#### Solutions:

EasyFlixUser is a python-based application designed for users, giving them the ability to do the following;
- Login or Create an account
- Choose or manage subscription level
- Manage their account (Password changes, account termination)
- Browse show catalogue
- Add shows to account
- Rent or return premium shows (if on basic plan)

EasyManagement is another Python-based application designed for an administrator of EasyFlix to access all aspects of it's media service including;
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
- Clean, professional GUI using Textual
- Modular code structure for better maintainability

**Database Requirements:**
- Dual database architecture (Separated sensitive data from non-sensitive)
- Complete data integrity, ensuring data is accurate, complete and consistent
- Database backup ability, ensuring data safety
- Easily available non-sensitive data, authentication required for sensitive data
- Data security all passwords will be stored as a hash using SHA-256 with salt


#### Ethical, Legal and Security Issues

**Security Issues:**
- Password storage must use SHA-256 hashing with unique salts
- Separation of sensitive customer data from content data
- Input validation to prevent SQL injection attacks
- Administrative access control and session management
- All access to sensitive data requires admin authentication

**Legal Issues:**
- Compliance with data protection regulations for customer data
- Secure storage of personal information (names, emails)
- Proper handling of financial transaction data -- hypothetical, will not be integrated
- Administrative responsibility for user data management
- No storage of advertising data for opted out users

**Ethical Issues:**
- Responsible handling of customer personal information
- Transparent subscription and rental cost management
- Fair content access based on subscription levels
- Ethical data collection and usage practices
- Opt in for data sharing

#### Data Quality Factors

**Data Accuracy:**
- Email validation to ensure correct format
- Date validation for release dates and rental periods
- Numerical validation for financial amounts and user IDs

**Data Consistency:**
- Referential integrity between customers and rentals
- Synchronized statistics and financial totals
- Consistent naming conventions and data formats
- Real-time updates across all related tables

**Data Security:**
- Encrypted password storage for all users
- Database file protection and access control
- Administrative audit trails and logging

---

## DESIGN

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

