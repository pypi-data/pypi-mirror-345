# Base HTML Template Overview

## 1. Overview
**Name**: base.html (Flask Jinja2 Template)

**Purpose**: This template is designed to reflect the panel layout of Visual Studio Code, incorporating a fixed top navigation bar, fixed sidebar on the left for choosing various application-sepcific functions, a seletables_view area on the left for identifying content of interest, a central editable content area, and an optional embedded iframe panel for interactive chat functionality on the left.

### Key Features:
- Single top navigation bar spanning the entire width of the page
- Four horizontally resizable panels beneath the navigation bar:
  - Left Panel – A vertical sidebar
  - Second Panel – A “selectables_view” area
  - Third Panel – The main content area
  - Right Panel – An iframe for a Chainlit interface or other embedded application

## 2. Functional Requirements
### Top Navigation Bar
- Must include navigation links or buttons for:
  - Home
  - New Card
  - Configuration
- Should support additional nav items if needed (e.g., user settings, help link).
- The style should be consistent across the application (e.g., dark theme, VS Code-like color scheme).

### Four Resizable Panels
- The layout beneath the nav bar must split horizontally into four sections:
  - Left Panel (Vertical Sidebar)
  - Second Panel (selectables_view)
  - Third Panel (Main Content)
  - Right Panel (Chainlit Iframe)
- Panels must be draggable (resizable) using a library such as Split.js.
- Each panel must have a sensible minimum width to remain functional and not collapse to zero.

### Look and Feel
- Overall appearance should closely resemble VS Code:
  - Panels with subtle separators
  - Resizable vertical panels
  - A dark (or light) theme that visually separates sections
  - Responsive design is optional, but the page should degrade gracefully on smaller screens or allow horizontal scrolling as needed.

### Extensibility
- Developers using base.html should be able to override named Jinja2 blocks for each panel.
- Additional style or script blocks should be available for customization in child templates.

## 3. Non-Functional Requirements
### Performance
- The template must load efficiently in modern browsers.
- Resizing via Split.js should not introduce significant overhead or lag.

### Maintainability
- HTML structure and CSS classes should be intuitive and organized.
- The layout must be easily modifiable (e.g., reorganizing panels, adjusting default sizes).

### Browser Compatibility
- Must work consistently in the latest versions of Chrome, Firefox, Edge, and Safari.
- Degraded (but functional) behavior is acceptable in older browsers.

## 4. Technical Specification / Implementation
Below is a proposed base.html template illustrating how to implement the requirements using Tailwind CSS and Split.js. The same approach can be adapted to other CSS frameworks or resizing libraries.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>{% block title %}VS Code-Like App{% endblock %}</title>
  <!-- Tailwind CSS -->
  <link
    href="https://cdn.jsdelivr.net/npm/tailwindcss@3.3.2/dist/tailwind.min.css"
    rel="stylesheet"
  />
  <!-- Split.js -->
  <script src="https://unpkg.com/split.js/dist/split.min.js"></script>

  {% block head_extra %}{% endblock %}
</head>
<body class="h-screen w-screen flex flex-col">

  <!-- Top Navigation Bar -->
  <nav class="bg-gray-800 text-white flex items-center justify-between p-4">
    <div class="flex items-center space-x-4">
      <!-- Home Button -->
      <a href="{{ url_for('home') }}" class="text-white hover:text-gray-200">
        Home
      </a>
      <!-- New Card Button -->
      <a href="{{ url_for('new_card') }}" class="text-white hover:text-gray-200">
        New Card
      </a>
      <!-- Configuration Button -->
      <a href="{{ url_for('config') }}" class="text-white hover:text-gray-200">
        Configuration
      </a>
    </div>
    <!-- Additional Nav Items -->
    <div>
      {% block nav_extra %}{% endblock %}
    </div>
  </nav>

  <!-- Main Container: Split into 4 Horizontal Panels -->
  <div id="horizontal-split" class="flex flex-grow overflow-hidden">
    <!-- 1. Left Panel: Vertical Sidebar -->
    <div
      id="panel1"
      class="bg-gray-900 text-white p-4 overflow-auto"
      style="min-width: 80px;"
    >
      {% block sidebar %}
      <h2 class="font-semibold text-lg mb-2">Sidebar</h2>
      <!-- Sidebar content goes here -->
      {% endblock %}
    </div>

    <!-- 2. Second Panel: selectables_view -->
    <div
      id="panel2"
      class="bg-gray-100 p-4 overflow-auto"
      style="min-width: 120px;"
    >
      {% block selectables_view %}
      <h2 class="font-semibold text-lg mb-2">Selectables View</h2>
      <!-- Tree-like or list UI goes here -->
      {% endblock %}
    </div>

    <!-- 3. Third Panel: Main Content (focused_area) -->
    <div
      id="panel3"
      class="bg-white p-4 overflow-auto"
      style="min-width: 200px;"
    >
      {% block main_content %}
      <h2 class="font-semibold text-lg mb-2">Main Content</h2>
      <!-- Main workspace or editor area -->
      {% endblock %}
    </div>

    <!-- 4. Right Panel: Chainlit Iframe -->
    <div
      id="panel4"
      class="bg-gray-100 p-4 overflow-auto"
      style="min-width: 150px;"
    >
      {% block chainlit_iframe %}
      <h2 class="font-semibold text-lg mb-2">Chainlit</h2>
      <iframe 
        src="https://your-chainlit-app-url"
        class="w-full h-full border-0"
      >
      </iframe>
      {% endblock %}
    </div>
  </div>

  <!-- Split.js Configuration -->
  <script>
    document.addEventListener("DOMContentLoaded", function () {
      Split([
        "#panel1",
        "#panel2",
        "#panel3",
        "#panel4"
      ], {
        direction: "horizontal",
        sizes: [10, 20, 40, 30],    // Adjust to set default panel widths
        minSize: [80, 120, 200, 150],
        gutterSize: 5,
        cursor: "col-resize",
      });
    });
  </script>

  {% block body_extra %}{% endblock %}
</body>
</html>

## Data Dictionary

### 1. Top Navigation Bar
- **Description**: A fixed navigation bar at the top of the application.
- **Attributes**:
  - Links: Home, New Card, Configuration, etc.
  - Style: Consistent across the application (dark theme).
- **Functionality**: Provides quick access to various application functionalities.

### 2. Left Sidebar
- **Description**: A vertical sidebar for navigation and actions.
- **Attributes**:
  - Buttons: Quick action buttons for common operations.
  - Content: Settings and configuration options.
- **Functionality**: Allows users to navigate and perform actions related to MCards.

### 3. Selectables View
- **Description**: An area for identifying content of interest.
- **Attributes**:
  - Structure: Tree-like or list UI.
  - Content: Displays MCard categories and folders.
- **Functionality**: Facilitates easy navigation through content categories.

### 4. Main Content Area
- **Description**: The central area for displaying detailed content.
- **Attributes**:
  - View Modes: Table View and Grid View.
  - Editable Content: Rich text editing capabilities.
- **Functionality**: Displays detailed information about selected MCards.

### 5. Chainlit Iframe
- **Description**: An embedded iframe for interactive chat functionality.
- **Attributes**:
  - Source: URL for the Chainlit application.
  - Size: Responsive to the panel size.
- **Functionality**: Provides an interactive chat interface within the application.

## 4.1. File Structure
- Place base.html in the Flask application’s /templates/ directory.
- Child templates (e.g., index.html) extend from base.html, overriding relevant Jinja2 blocks to fill each panel with content.

## 4.2. Jinja2 Blocks
- **title**: For setting the page title.
- **sidebar**: Content for the left panel.
- **selectables_view**: Content for the second panel.
- **main_content**: Primary workspace or editor view.
- **chainlit_iframe**: Embedded content or extension-like tools, including Chainlit.
- **nav_extra** and **head_extra**: Optional placeholders to insert extra navigation items or additional scripts/styles.
- **body_extra**: A place for injecting page-specific scripts or additional HTML at the end of the body.

## 5. Usage
### Extending the Base Template
In your child templates, extend base.html and override the blocks you need:
```jinja
{% extends "base.html" %}
{% block title %}My Home Page{% endblock %}
{% block sidebar %}
<p>Custom sidebar content...</p>
{% endblock %}
```

## Related Documentation
- [Main Application README](../README.md)

This specification provides a structured, VS Code-inspired base template (base.html) for a Flask + Jinja2 application. By offering a top navigation bar, four draggable panels, and clear content blocks, it enables developers to quickly build a multi-panel, split-based interface. Future enhancements can introduce even more advanced VS Code-like functionalities (collapsing panels, command palette, theming), ensuring a robust and familiar user experience.