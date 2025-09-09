# Program Outlines
Outline of the capabilities of each textual program

## EasyFlixAdmin
EasyFlixAdmin is a comprehensive administrative interface for the EasyFlix streaming service. It provides secure, encrypted communication with the backend database through EFAPI and offers a modern terminal-based user interface built with Textual.

## Features Tree Structure

### 🔐 Authentication System
- **Login Screen**
  - Secure admin authentication using stored credentials
  - Credentials are hashed and salted in the database
  - Encrypted communication with API backend
  - Session management for logged-in admins

### 📊 Dashboard
- **System Overview**
  - Total users count
  - Premium subscribers count
  - Basic subscribers count
  - Total shows purchased count
- **Financial Summary**
  - Total combined revenue
  - Subscription revenue breakdown
  - Purchase revenue tracking
  - Last update timestamp

### 👥 User Management
- **User Display & Filtering**
  - View all users with detailed information
  - Filter users by subscription level (All/Basic/Premium)
  - Real-time data refresh capabilities
- **User Information Display**
  - Username and email
  - Subscription level
  - Total amount spent
  - Favorite genre
  - Marketing opt-in status
- **User Account Management**
  - **Password Management**
    - Change user passwords
    - Secure password hashing and salting
  - **Subscription Management**
    - Upgrade/downgrade subscription levels
    - Automatic billing calculation for upgrades
  - **Account Deletion**
    - Permanent user account removal
    - Confirmation dialogs for safety
    - Cascade deletion of user data (purchases, etc.)

### 🎬 Content Management
- **Show Catalog Display**
  - View all shows in grid layout
  - Comprehensive show information display
- **Show Information**
  - Name, genre, rating, director
  - Length, release date
  - Access group (Basic/Premium)
  - Purchase cost
- **Add New Shows**
  - **Basic Information**
    - Name, director, genre selection
    - Rating selection (G, PG, PG-13, R, TV-14, TV-MA, TV-PG)
    - Release date, length in minutes
  - **Access & Pricing**
    - Access group assignment (Basic/Premium)
    - Cost configuration for Premium shows
    - Automatic cost handling for Basic shows (free)
- **Edit Existing Shows**
  - **Access Control**
    - Change access group (Basic ↔ Premium)
  - **Pricing Management**
    - Update purchase costs
    - Dynamic cost visibility based on access group
- **Show Deletion**
  - Permanent show removal
  - Confirmation dialogs
  - Automatic cleanup of related data

### 💰 Financial Reports
- **Revenue Tracking**
  - Total combined revenue
  - Subscription revenue breakdown
  - Purchase revenue tracking
  - Premium vs Basic subscription revenue
- **Historical Data**
  - Date-wise financial records
  - Revenue trend analysis
  - Last update timestamps

### 📈 System Statistics
- **Current Statistics**
  - Real-time system metrics
  - User distribution data
  - Purchase activity tracking
- **Data Points**
  - Total users
  - Subscription breakdowns
  - Total shows purchased
  - System update timestamps

### 🛒 Purchase History
- **Transaction Management**
  - Complete purchase history tracking
  - User-show purchase relationships
- **Purchase Details**
  - Purchase ID and date
  - User information (username, ID)
  - Show information (name, ID)
  - Transaction cost

## Technical Features

### 🔒 Security
- **Encryption**
  - End-to-end encrypted communication
  - PBKDF2 key derivation with SHA256
  - Fernet symmetric encryption
  - Base64 encoding for transport
- **Authentication**
  - Secure admin credential storage
  - Password hashing with salt
  - Session management

### 🖥️ User Interface
- **Modern Terminal UI**
  - Built with Textual framework
  - Responsive design
  - Dark theme with color coding
- **Navigation**
  - Sidebar menu system
  - Modal dialogs for actions
  - Loading indicators
  - Real-time notifications
- **Data Display**
  - Grid layouts for content
  - Filtered views
  - Search capabilities
  - Pagination support

### 🔄 Data Management
- **Real-time Updates**
  - Automatic statistics refresh
  - Live data synchronization
  - Asynchronous operations
- **Error Handling**
  - Comprehensive error messages
  - Graceful failure handling
  - User-friendly notifications

### 🔧 API Integration
- **EFAPI Communication**
  - RESTful API calls
  - JSON data exchange
  - Command-based operations
- **Supported Operations**
  - User CRUD operations
  - Show management
  - Financial data retrieval
  - Statistics generation
  - Authentication services

## Modal Dialogs

### Confirmation Modals
- **User Deletion**: Requires explicit confirmation
- **Show Deletion**: Requires explicit confirmation
- **Data Updates**: Success/failure notifications

### Management Modals
- **User Management**: Password change, subscription updates
- **Show Addition**: Complete show information entry
- **Show Editing**: Access group and pricing updates

## Color Coding System
- **Primary Actions**: Red (#e94560)
- **User Data**: Blue (#3498db)
- **Content Data**: Orange (#f39c12)
- **Financial Data**: Green (#27ae60)
- **Purchase Data**: Purple (#9b59b6)
- **Statistics**: Red (#e74c3c)
- **Success**: Green variations
- **Warning**: Orange variations
- **Error**: Red variations

## Data Validation
- **Input Validation**: All forms include validation
- **Type Checking**: Numeric fields validated
- **Required Fields**: All mandatory fields enforced
- **Date Formats**: Proper date format validation
- **Business Rules**: Subscription logic, pricing rules

## EasyFlixUser
EasyFlixUser is a comprehensive user interface for the EasyFlix streaming service. It provides secure, encrypted communication with the backend database through EFAPI and offers a modern terminal-based user interface built with Textual for customers to manage their streaming experience.

## Features Tree Structure

### 🔐 Authentication & Account Creation
- **Welcome Screen**
  - Login option for existing users
  - Account creation for new users
- **Login System**
  - Secure user authentication using stored credentials
  - Credentials are hashed and salted in the database
  - Encrypted communication with API backend
  - Session management for logged-in users
- **Account Creation**
  - **User Information**
    - Username selection
    - Email address
    - Password creation (securely hashed)
  - **Subscription Selection**
    - Basic subscription ($30) - Access to basic content
    - Premium subscription ($80) - Access to all content
  - **Marketing Preferences**
    - Optional marketing communication opt-in
    - GDPR-compliant preference management
  - **Automatic Billing**
    - Immediate subscription charge processing
    - Real-time cost calculation and display

### 🎬 Content Discovery & Management
- **Browse Shows**
  - **Show Catalog Display**
    - Grid layout with responsive design
    - Comprehensive show information display
    - Visual distinction between Basic and Premium content
  - **Advanced Search & Filtering**
    - **Text Search**
      - Real-time search with debounced input
      - Search by show name
      - Instant results as you type
    - **Genre Filtering**
      - Dropdown with all available genres
      - Dynamic genre list from database
      - Clear filter options
    - **Rating Filtering**
      - Filter by content ratings (G, PG, PG-13, R, TV-14, TV-MA, TV-PG)
      - Age-appropriate content discovery
    - **Combined Filtering**
      - Multiple filters can be applied simultaneously
      - Real-time results update
  - **Show Information Display**
    - Name, genre, rating, director
    - Length, release date
    - Access level (Basic/Premium)
    - Purchase cost for Premium shows (Basic users)
  - **Content Access Management**
    - **Basic Subscription Users**
      - Free access to Basic content
      - Purchase option for Premium shows
      - Clear pricing display
      - Confirmation dialogs for purchases
    - **Premium Subscription Users**
      - Free access to all content
      - No additional charges
      - Clear access indicators

### 📺 Personal Library Management
- **My Shows**
  - **Collection Display**
    - Grid view of owned content
    - Show details and metadata
    - Visual confirmation of ownership
  - **Show Management**
    - **Add Shows**
      - One-click addition for accessible content
      - Purchase flow for Premium content (Basic users)
      - Real-time library updates
    - **Remove Shows**
      - Safe removal with confirmation dialogs
      - Permanent removal from personal collection
      - No refunds for purchased content
  - **Collection Status**
    - Visual indicators for owned content
    - Clear ownership status in browse view
    - Disabled buttons for already-owned shows

### 👤 Account Management
- **Account Information Display**
  - Username and email
  - Current subscription level
  - Total amount spent
  - Favorite genre (auto-calculated)
  - Marketing opt-in status
- **Password Management**
  - **Change Password**
    - Secure password update
    - Password confirmation validation
    - Immediate effect across all sessions
- **Subscription Management**
  - **Upgrade/Downgrade Options**
    - Basic to Premium upgrade ($80 charge)
    - Premium to Basic downgrade (free)
    - Real-time billing calculation
    - Immediate access level changes
  - **Billing Transparency**
    - Clear cost display before changes
    - Confirmation of charges
    - Updated spending totals
- **Marketing Preferences**
  - **Opt-in/Opt-out Management**
    - Toggle marketing communications
    - GDPR compliance
    - Immediate preference updates
    - Clear current status display

## Technical Features

### 🔒 Security & Privacy
- **End-to-End Encryption**
  - PBKDF2 key derivation with SHA256
  - Fernet symmetric encryption
  - Base64 encoding for secure transport
  - Master key management
- **Secure Authentication**
  - Password hashing with unique salts
  - Session management
  - Automatic logout capabilities
- **Data Protection**
  - Encrypted API communications
  - Secure credential storage
  - Privacy-compliant data handling

### 🖥️ User Interface & Experience
- **Modern Terminal UI**
  - Built with Textual framework
  - Responsive grid layouts
  - Professional dark theme
  - Intuitive navigation
- **Interactive Elements**
  - **Navigation**
    - Sidebar menu system
    - Clear section indicators
    - Smooth transitions
  - **Modal Dialogs**
    - Purchase confirmations
    - Removal confirmations
    - Loading indicators
    - Error/success notifications
  - **Real-time Feedback**
    - Instant search results
    - Live filter updates
    - Immediate status changes
    - Progress indicators

### 🔄 Data Management
- **Asynchronous Operations**
  - Non-blocking API calls
  - Smooth user experience
  - Background data loading
  - Graceful error handling
- **Real-time Updates**
  - Immediate library synchronization
  - Live account information updates
  - Dynamic content availability
  - Session state management
- **Caching System**
  - Local data caching for performance
  - Intelligent cache invalidation
  - Reduced API calls
  - Faster content browsing

### 🎨 Visual Design System
- **Color Coding**
  - **Primary Orange (#FF8C00)**: Main branding and primary actions
  - **Gold (#FFD700)**: Premium content and pricing
  - **Green (#32CD32)**: Owned content and success states
  - **Red (#DC143C)**: Remove actions and errors
  - **Gray (#696969)**: Disabled states and secondary info
- **Content Categorization**
  - **Basic Content**: Orange border accent
  - **Premium Content**: Gold border accent
  - **Owned Content**: Green border with background tint
  - **Unavailable Content**: Grayed out with disabled state

## User Workflows

### New User Journey
1. **Welcome Screen** → Create Account
2. **Account Creation** → Fill details, select subscription, set preferences
3. **Automatic Login** → Account created with immediate access
4. **Browse Shows** → Discover content based on subscription level
5. **Build Library** → Add shows to personal collection

### Existing User Journey
1. **Welcome Screen** → Login
2. **Authentication** → Secure credential verification
3. **Browse/My Shows** → Content discovery or library management
4. **Account Management** → Update preferences as needed

### Content Discovery Workflow
1. **Browse Shows** → View all available content
2. **Apply Filters** → Narrow down by genre, rating, or search
3. **Review Show Details** → Check information and access requirements
4. **Add to Library** → Free addition or purchase flow
5. **Confirmation** → Success notification and library update

### Account Management Workflow
1. **Account Section** → View current information
2. **Select Action** → Password, subscription, or marketing preferences
3. **Update Details** → Make desired changes with confirmations
4. **Confirmation** → Immediate updates with success feedback

## Modal Dialog System

### Purchase Confirmation
- **Premium Show Purchase**
  - Show name and cost display
  - Clear purchase/cancel options
  - Billing confirmation
  - Library update on completion

### Removal Confirmation
- **Show Removal**
  - Show name confirmation
  - Permanent removal warning
  - Safe cancellation option
  - Immediate library update

### Account Updates
- **Password Changes**
  - Password confirmation validation
  - Secure update process
  - Success/error feedback

- **Subscription Changes**
  - Current and new level display
  - Cost implications clearly shown
  - Immediate access updates

## Error Handling & User Feedback

### Notification System
- **Success Messages**: Green notifications for completed actions
- **Warning Messages**: Yellow notifications for validation issues
- **Error Messages**: Red notifications for failures
- **Information Messages**: Blue notifications for updates

### Graceful Degradation
- **API Failures**: Clear error messages with retry options
- **Network Issues**: Timeout handling with user feedback
- **Data Validation**: Client-side validation before API calls
- **Loading States**: Clear indicators during processing

## Content Access Logic

### Basic Subscription Users
- **Free Access**: All Basic-tier content
- **Purchase Required**: Premium content with clear pricing
- **Billing Integration**: Automatic charge processing
- **Access Upgrade**: Immediate Premium content access after purchase

### Premium Subscription Users
- **Full Access**: All content at no additional cost
- **Clear Indicators**: Visual confirmation of included access
- **No Hidden Fees**: Transparent pricing model

## Data Validation & Business Rules

### Input Validation
- **Account Creation**: Username/email uniqueness, password strength
- **Search Filters**: Valid filter combinations
- **Form Submission**: Required field validation
- **Password Changes**: Confirmation matching

### Business Logic
- **Subscription Pricing**: Basic ($30), Premium ($80), Upgrade ($80)
- **Content Access**: Subscription-based access control
- **Purchase Rules**: No duplicate purchases, immediate access
- **Library Management**: Personal collection limits and rules
