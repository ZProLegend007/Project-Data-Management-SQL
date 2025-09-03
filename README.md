# EasyFlix Management System - Part 1 Research & Design

**Project Name**: EasyFlix Management System  
**Date**: 2025-09-03  
**Student**: ZProLegend007  

---

## INVESTIGATE

### Timeline and Schedule

| **Phase** | **Task** | **Duration** | **Completion %** |
|-----------|----------|--------------|------------------|
| **Phase 1** | Research & Design | 3 days | 40% |
| | Problem analysis | 1 day | |
| | Database design & ERD | 1 days | |
| | Interface mockups | 1 days | |
| **Phase 2** | Development | 3 days | 0% |
| | Database implementation | 1 days | |
| | Core functions | 1 days | |
| | Admin interface | 1 days | |
| **Phase 3** | Testing & Documentation | 2 days | 0% |
| | System testing | 1 day | |
| | Final documentation | 1 day | |

### Problem Outline

EasyFlix Management System is a Python-based desktop application designed for administrators to manage all aspects of a streaming service including users, subscriptions, content, and financial data. The system provides complete administrative control over the EasyFlix platform through a single, comprehensive interface.

### Problem Description

#### Scenario
EasyFlix is a streaming service offering basic and premium subscription tiers. The company requires an administrative management system that allows complete control over user accounts, content library, subscription management, and financial tracking. All operations are performed by administrators who have full access to manage the entire platform.

#### Detailed Requirements

**Programming Requirements:**
- Python 3.x application with SQLite3 database integration
- Secure password hashing using SHA-256 with salt for all users
- Single administrative interface with complete system access
- Real-time data updates and validation
- Clean, professional GUI using Tkinter
- Modular code structure for maintainability

**Database Requirements:**
- Dual database architecture (protected user data, content data)
- Complete customer management with subscription tracking
- Content catalog with administrative control
- Financial tracking and statistics monitoring
- Data integrity and referential constraints

**Functional Requirements:**
- Admin can create, modify, and delete user accounts
- Admin can manage all user subscriptions and passwords
- Admin can add, edit, and remove shows/movies from catalog
- Admin can process premium content rentals for users
- Admin can view comprehensive financial reports and statistics
- Admin can manage user rental returns and account modifications

#### Ethical, Legal and Security Issues

**Security Issues:**
- Password storage must use SHA-256 hashing with unique salts
- Separation of sensitive customer data from content data
- Input validation to prevent SQL injection attacks
- Administrative access control and session management

**Legal Issues:**
- Compliance with data protection regulations for customer data
- Secure storage of personal information (names, emails)
- Proper handling of financial transaction data
- Administrative responsibility for user data management

**Ethical Issues:**
- Responsible handling of customer personal information
- Transparent subscription and rental cost management
- Fair content access based on subscription levels
- Ethical data collection and usage practices

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

### Entity-Relationship Diagram

```
[CUSTOMERS] ----< [RENTALS] >---- [SHOWS]
     |                               |
     |                               |
[STATISTICS]                   [CATEGORIES]
     |
[FINANCIALS]
```

**Detailed ERD with Keys:**

- **CUSTOMERS** (User_ID(PK), Names, Email, Password_Hash, Salt, Subscription_Level, Total_Spent)
- **SHOWS** (Show_ID(PK), Name, Release_Date, Rating, Director, Length, Type, Category_ID(FK), Access_Group, Cost_To_Rent)
- **RENTALS** (Rental_ID(PK), User_ID(FK), Show_ID(FK), Rental_Date, Return_Date, Cost)
- **CATEGORIES** (Category_ID(PK), Category_Name, Description)
- **STATISTICS** (Stat_ID(PK), Total_Shows_Rented, Total_Subscriptions, Total_Users, Last_Updated)
- **FINANCIALS** (Finance_ID(PK), Total_Revenue_Rent, Total_Revenue_Subscriptions, Total_Combined_Revenue, Last_Updated)

### Relational Notation

- **CUSTOMERS** (User_ID, Names, Email, Password_Hash, Salt, Subscription_Level, Premium_Shows_Renting, Total_Spent)
- **SHOWS** (Show_ID, Name, Release_Date, Rating, Director, Length, Type, Category_ID, Access_Group, Cost_To_Rent)
  - **Foreign Key:** Category_ID references CATEGORIES(Category_ID)
- **RENTALS** (Rental_ID, User_ID, Show_ID, Rental_Date, Return_Date, Cost)
  - **Foreign Key:** User_ID references CUSTOMERS(User_ID)
  - **Foreign Key:** Show_ID references SHOWS(Show_ID)
- **CATEGORIES** (Category_ID, Category_Name, Description)
- **STATISTICS** (Stat_ID, Total_Shows_Rented, Total_Subscriptions, Total_Users, Last_Updated)
- **FINANCIALS** (Finance_ID, Total_Revenue_Rent, Total_Revenue_Subscriptions, Total_Combined_Revenue, Last_Updated)

### Data Dictionary

| **Table** | **Purpose** | **Fields** |
|-----------|-------------|------------|
| **CUSTOMERS** | Stores all user account information managed by admin | User_ID (INT, PK), Names (TEXT), Email (TEXT), Password_Hash (TEXT), Salt (TEXT), Subscription_Level (TEXT), Premium_Shows_Renting (INT), Total_Spent (REAL) |
| **SHOWS** | Contains all content managed by admin with access control | Show_ID (INT, PK), Name (TEXT), Release_Date (TEXT), Rating (TEXT), Director (TEXT), Length (TEXT), Type (TEXT), Category_ID (INT, FK), Access_Group (TEXT), Cost_To_Rent (REAL) |
| **RENTALS** | Tracks all premium content rentals processed by admin | Rental_ID (INT, PK), User_ID (INT, FK), Show_ID (INT, FK), Rental_Date (TEXT), Return_Date (TEXT), Cost (REAL) |
| **CATEGORIES** | Defines content categories managed by admin | Category_ID (INT, PK), Category_Name (TEXT), Description (TEXT) |
| **STATISTICS** | System-wide usage statistics monitored by admin | Stat_ID (INT, PK), Total_Shows_Rented (INT), Total_Subscriptions (INT), Total_Users (INT), Last_Updated (TEXT) |
| **FINANCIALS** | Complete financial data accessible to admin | Finance_ID (INT, PK), Total_Revenue_Rent (REAL), Total_Revenue_Subscriptions (REAL), Total_Combined_Revenue (REAL), Last_Updated (TEXT) |

### Database Queries (Plain English)

1. **Find all users with overdue rentals** - Retrieve customers who have rentals where return date is null and rental date exceeds the allowed period
2. **Calculate monthly revenue breakdown** - Sum rental revenue and subscription revenue separately for a specified month
3. **List all premium content available for rental** - Display shows where access group is 'premium' and rental cost is greater than zero
4. **Show complete user profile with rental history** - Join customers and rentals tables to display full user information and all their rental transactions
5. **Generate most popular content report** - Count rentals by show and category, ordered by frequency to identify trending content
6. **Find users eligible for subscription upgrades** - Identify basic subscribers who frequently rent premium content
7. **Calculate total platform statistics** - Count total users, active subscriptions, and total content available across all categories
8. **List recently added content** - Filter shows by release date or addition date to show newest additions to the platform
