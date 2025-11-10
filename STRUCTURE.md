# Project Structure Documentation

## Overview
This is an Energy Settlement Dashboard for Ghana Grid Company built with Dash/Plotly. The application uses a **single-page architecture** with show/hide logic for different sections.

## Architecture Decision: Single-Page vs Dash Pages

### ✅ Current Approach: Single-Page Layout
We're using a single-page layout with visibility toggling between upload and dashboard sections.

**Why this approach?**
- Dashboard-focused application with interconnected sections
- Shared state between upload and analytics sections
- Simpler state management with `dcc.Store`
- All data flows from upload → analytics
- Better UX for this specific use case (no page refreshes)

**When to switch to Dash Pages:**
- If you need completely independent sections (Admin Panel, Settings, etc.)
- If users need to bookmark specific analysis pages
- If the app grows to 5+ distinct pages with different purposes

## Project Structure

```
gencon/
├── app.py                      # Main application entry point
│   └── Defines layout, initializes Dash app
│
├── callbacks/                  # Business logic layer
│   ├── __init__.py            # Callback registration
│   ├── upload.py              # Upload and view switching callbacks
│   └── data_loader.py         # Data processing utilities
│
├── ui/                        # Presentation layer
│   ├── __init__.py           # UI component exports
│   ├── upload.py             # Upload section UI
│   └── dashboard.py          # Dashboard section UI (analytics)
│
├── assets/                    # Static files
│   └── styles.css            # Custom CSS styles
│
├── pyproject.toml            # Project dependencies
└── README.md                 # Project documentation
```

## Component Responsibilities

### `app.py` - Application Entry Point
- Initializes the Dash application
- Defines the overall layout structure
- Manages session stores for data persistence
- Registers all callbacks

### `callbacks/` - Business Logic
- **`upload.py`**: Handles file upload, validation, and view switching
- **`data_loader.py`**: Processes Excel files and validates data structure
- **`__init__.py`**: Centralizes callback registration

### `ui/` - User Interface Components
- **`upload.py`**: Upload interface with drag-and-drop
- **`dashboard.py`**: Dashboard layout with sections for:
  - Summary statistics
  - Generation/consumption charts
  - Detailed data tables

### `assets/` - Static Resources
- CSS for custom styling
- Future: images, fonts, etc.

## Data Flow

```
1. User uploads Excel file
   ↓
2. callbacks/upload.py processes file
   ↓
3. callbacks/data_loader.py validates and transforms data
   ↓
4. Data stored in dcc.Store (session storage)
   ↓
5. View switches to dashboard
   ↓
6. Dashboard callbacks read from stores
   ↓
7. UI components display analytics
```

## State Management

### Session Stores
- `generations-store`: Generation data (hourly aggregated)
- `consumptions-store`: Consumption data (hourly aggregated)
- `plant-consumer-store`: Contract/relationship data
- `data-name-store`: Currently loaded filename

### Why Stores?
- Persist data across view switches
- Avoid re-uploading data
- Enable client-side state management
- Support browser refresh (session storage)

## Best Practices Being Followed

### ✅ Separation of Concerns
- UI components separated from logic
- Data processing isolated in utilities
- Clear module boundaries

### ✅ Documentation
- Module-level docstrings
- Function docstrings explaining purpose
- Inline comments for complex logic

### ✅ Scalability
- Modular structure allows easy expansion
- New dashboard sections can be added to `ui/dashboard.py`
- New callbacks can be added as separate files in `callbacks/`

### ✅ Maintainability
- Clear naming conventions
- Consistent code style
- Logical file organization

## Future Expansion Recommendations

### Adding New Dashboard Features
1. Create new callback file in `callbacks/` (e.g., `callbacks/analytics.py`)
2. Import in `callbacks/__init__.py`
3. Add corresponding UI components to `ui/dashboard.py`
4. Add new Store if needed for feature-specific state

### Adding New Data Sources
1. Extend `callbacks/data_loader.py` with new loader methods
2. Add validation logic
3. Create new Store in `app.py`
4. Update upload callback to handle new data type

### Adding Filters/Controls
1. Add filter UI components to `ui/dashboard.py`
2. Create callback in `callbacks/` to handle filter logic
3. Use existing stores or create new ones for filter state

## When to Consider Dash Pages

Consider migrating to Dash Pages if:
- [ ] You need 5+ completely independent pages
- [ ] Different user roles need different page access
- [ ] Users need to bookmark/share specific analysis URLs
- [ ] Pages don't share state/data
- [ ] You need different layouts per page

## Quick Start for New Developers

1. **Understanding the app flow:**
   - Start with `app.py` to see overall structure
   - Check `ui/` to understand what users see
   - Review `callbacks/` to understand business logic

2. **Adding a new chart:**
   - Add placeholder div in `ui/dashboard.py`
   - Create callback in `callbacks/analytics.py` (new file)
   - Read from existing stores
   - Return plotly figure

3. **Modifying upload logic:**
   - Update `callbacks/upload.py`
   - If data format changes, update `callbacks/data_loader.py`

## Code Quality Standards

- ✅ All modules have docstrings
- ✅ Functions have clear purposes and documentation
- ✅ No linter errors
- ✅ Consistent naming conventions
- ✅ Comments explain "why", not "what"

## Technology Stack

- **Dash**: Web framework
- **Plotly**: Visualizations
- **Pandas**: Data processing
- **Dash Bootstrap Components**: UI components
- **Font Awesome**: Icons

