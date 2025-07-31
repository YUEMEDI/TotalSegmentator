# 🎨 Unified Design System Documentation

## 📋 **Project Overview**

This document outlines the unified design system approach for the TotalSegmentator ecosystem, ensuring consistent UI/UX across all components (YUETransfer, YUEUpload, TotalSegmentator).

## 🏗️ **Design System Architecture**

### **📁 File Structure**
```
TotalSegmentator/
├── shared/
│   ├── styles/
│   │   ├── design-tokens.css          # Single source of truth for all design values
│   │   ├── components.css             # Shared component styles
│   │   ├── layout.css                 # Shared layout styles
│   │   ├── typography.css             # Font and text styles
│   │   ├── animations.css             # Shared animations and transitions
│   │   └── themes/
│   │       ├── light.css              # Light theme variables
│   │       └── dark.css               # Dark theme variables
│   ├── components/
│   │   ├── buttons.html               # Reusable button components
│   │   ├── cards.html                 # Reusable card components
│   │   ├── forms.html                 # Reusable form components
│   │   ├── navigation.html            # Shared navigation components
│   │   ├── modals.html                # Modal and dialog components
│   │   └── alerts.html                # Alert and notification components
│   ├── scripts/
│   │   ├── design-system.js           # Shared JavaScript utilities
│   │   ├── theme-switcher.js          # Theme management
│   │   └── component-loader.js        # Dynamic component loading
│   └── assets/
│       ├── icons/                     # SVG icons
│       ├── images/                    # Shared images
│       └── fonts/                     # Custom fonts
├── yuetransfer/
│   └── templates/
│       └── base.html                  # Extends shared base
├── yueupload/
│   └── templates/
│       └── base.html                  # Extends shared base
└── totalsegmentator/
    └── templates/
        └── base.html                  # Extends shared base
```

## 🎨 **Design Tokens (Single Source of Truth)**

### **🎨 Colors**
```css
/* shared/styles/design-tokens.css */
:root {
  /* Primary Colors */
  --primary-color: #2563eb;
  --primary-light: #3b82f6;
  --primary-dark: #1d4ed8;
  
  /* Secondary Colors */
  --secondary-color: #64748b;
  --secondary-light: #94a3b8;
  --secondary-dark: #475569;
  
  /* Semantic Colors */
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --error-color: #ef4444;
  --info-color: #3b82f6;
  
  /* Neutral Colors */
  --white: #ffffff;
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-300: #d1d5db;
  --gray-400: #9ca3af;
  --gray-500: #6b7280;
  --gray-600: #4b5563;
  --gray-700: #374151;
  --gray-800: #1f2937;
  --gray-900: #111827;
  --black: #000000;
  
  /* Background Colors */
  --bg-primary: var(--white);
  --bg-secondary: var(--gray-50);
  --bg-tertiary: var(--gray-100);
  
  /* Text Colors */
  --text-primary: var(--gray-900);
  --text-secondary: var(--gray-600);
  --text-tertiary: var(--gray-500);
  --text-inverse: var(--white);
}
```

### **📝 Typography**
```css
/* Typography Scale */
:root {
  /* Font Families */
  --font-family-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-family-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
  
  /* Font Sizes */
  --font-size-xs: 0.75rem;    /* 12px */
  --font-size-sm: 0.875rem;   /* 14px */
  --font-size-base: 1rem;     /* 16px */
  --font-size-lg: 1.125rem;   /* 18px */
  --font-size-xl: 1.25rem;    /* 20px */
  --font-size-2xl: 1.5rem;    /* 24px */
  --font-size-3xl: 1.875rem;  /* 30px */
  --font-size-4xl: 2.25rem;   /* 36px */
  
  /* Font Weights */
  --font-weight-light: 300;
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  
  /* Line Heights */
  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;
}
```

### **📏 Spacing**
```css
/* Spacing Scale */
:root {
  --spacing-0: 0;
  --spacing-1: 0.25rem;   /* 4px */
  --spacing-2: 0.5rem;    /* 8px */
  --spacing-3: 0.75rem;   /* 12px */
  --spacing-4: 1rem;      /* 16px */
  --spacing-5: 1.25rem;   /* 20px */
  --spacing-6: 1.5rem;    /* 24px */
  --spacing-8: 2rem;      /* 32px */
  --spacing-10: 2.5rem;   /* 40px */
  --spacing-12: 3rem;     /* 48px */
  --spacing-16: 4rem;     /* 64px */
  --spacing-20: 5rem;     /* 80px */
  --spacing-24: 6rem;     /* 96px */
}
```

### **🎯 Component Properties**
```css
/* Component Design Tokens */
:root {
  /* Border Radius */
  --border-radius-sm: 0.25rem;   /* 4px */
  --border-radius-md: 0.375rem;  /* 6px */
  --border-radius-lg: 0.5rem;    /* 8px */
  --border-radius-xl: 0.75rem;   /* 12px */
  --border-radius-2xl: 1rem;     /* 16px */
  --border-radius-full: 9999px;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  
  /* Transitions */
  --transition-fast: 150ms ease-in-out;
  --transition-normal: 250ms ease-in-out;
  --transition-slow: 350ms ease-in-out;
  
  /* Z-Index Scale */
  --z-dropdown: 1000;
  --z-sticky: 1020;
  --z-fixed: 1030;
  --z-modal-backdrop: 1040;
  --z-modal: 1050;
  --z-popover: 1060;
  --z-tooltip: 1070;
}
```

## 🧩 **Component System**

### **🔘 Buttons**
```css
/* shared/styles/components/buttons.css */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-4);
  border-radius: var(--border-radius-lg);
  font-family: var(--font-family-primary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  line-height: var(--line-height-normal);
  text-decoration: none;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: var(--shadow-sm);
  user-select: none;
}

.btn:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn:active {
  transform: translateY(0);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* Button Variants */
.btn--primary {
  background: var(--primary-color);
  color: var(--text-inverse);
  border-color: var(--primary-color);
}

.btn--primary:hover {
  background: var(--primary-dark);
  border-color: var(--primary-dark);
}

.btn--secondary {
  background: var(--secondary-color);
  color: var(--text-inverse);
  border-color: var(--secondary-color);
}

.btn--outline {
  background: transparent;
  color: var(--primary-color);
  border-color: var(--primary-color);
}

.btn--outline:hover {
  background: var(--primary-color);
  color: var(--text-inverse);
}

/* Button Sizes */
.btn--sm {
  padding: var(--spacing-1) var(--spacing-3);
  font-size: var(--font-size-xs);
}

.btn--lg {
  padding: var(--spacing-3) var(--spacing-6);
  font-size: var(--font-size-base);
}
```

### **📋 Cards**
```css
/* shared/styles/components/cards.css */
.card {
  background: var(--bg-primary);
  border: 1px solid var(--gray-200);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  transition: box-shadow var(--transition-fast);
}

.card:hover {
  box-shadow: var(--shadow-md);
}

.card__header {
  padding: var(--spacing-4);
  border-bottom: 1px solid var(--gray-200);
  background: var(--bg-secondary);
}

.card__title {
  margin: 0;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.card__body {
  padding: var(--spacing-4);
}

.card__footer {
  padding: var(--spacing-4);
  border-top: 1px solid var(--gray-200);
  background: var(--bg-secondary);
}
```

### **📝 Forms**
```css
/* shared/styles/components/forms.css */
.form-group {
  margin-bottom: var(--spacing-4);
}

.form-label {
  display: block;
  margin-bottom: var(--spacing-2);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
}

.form-input {
  width: 100%;
  padding: var(--spacing-2) var(--spacing-3);
  border: 1px solid var(--gray-300);
  border-radius: var(--border-radius-md);
  font-family: var(--font-family-primary);
  font-size: var(--font-size-sm);
  line-height: var(--line-height-normal);
  transition: border-color var(--transition-fast);
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-input:invalid {
  border-color: var(--error-color);
}

.form-help {
  margin-top: var(--spacing-1);
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.form-error {
  margin-top: var(--spacing-1);
  font-size: var(--font-size-xs);
  color: var(--error-color);
}
```

## 🎨 **Theme System**

### **🌞 Light Theme**
```css
/* shared/styles/themes/light.css */
[data-theme="light"] {
  --bg-primary: var(--white);
  --bg-secondary: var(--gray-50);
  --bg-tertiary: var(--gray-100);
  
  --text-primary: var(--gray-900);
  --text-secondary: var(--gray-600);
  --text-tertiary: var(--gray-500);
  
  --border-color: var(--gray-200);
  --border-color-hover: var(--gray-300);
}
```

### **🌙 Dark Theme**
```css
/* shared/styles/themes/dark.css */
[data-theme="dark"] {
  --bg-primary: var(--gray-900);
  --bg-secondary: var(--gray-800);
  --bg-tertiary: var(--gray-700);
  
  --text-primary: var(--gray-100);
  --text-secondary: var(--gray-300);
  --text-tertiary: var(--gray-400);
  
  --border-color: var(--gray-700);
  --border-color-hover: var(--gray-600);
}
```

## 🧭 **Layout System**

### **📐 Grid System**
```css
/* shared/styles/layout/grid.css */
.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-4);
}

.grid {
  display: grid;
  gap: var(--spacing-4);
}

.grid--cols-1 { grid-template-columns: repeat(1, 1fr); }
.grid--cols-2 { grid-template-columns: repeat(2, 1fr); }
.grid--cols-3 { grid-template-columns: repeat(3, 1fr); }
.grid--cols-4 { grid-template-columns: repeat(4, 1fr); }

@media (max-width: 768px) {
  .grid--cols-2,
  .grid--cols-3,
  .grid--cols-4 {
    grid-template-columns: 1fr;
  }
}
```

### **📱 Responsive Breakpoints**
```css
/* shared/styles/layout/responsive.css */
:root {
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
  --breakpoint-2xl: 1536px;
}

@media (min-width: 640px) { /* sm */ }
@media (min-width: 768px) { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
@media (min-width: 1536px) { /* 2xl */ }
```

## 🎭 **Animation System**

### **🔄 Transitions**
```css
/* shared/styles/animations/transitions.css */
.fade-in {
  animation: fadeIn var(--transition-normal);
}

.fade-out {
  animation: fadeOut var(--transition-normal);
}

.slide-in {
  animation: slideIn var(--transition-normal);
}

.slide-out {
  animation: slideOut var(--transition-normal);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeOut {
  from { opacity: 1; }
  to { opacity: 0; }
}

@keyframes slideIn {
  from { transform: translateY(-20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

@keyframes slideOut {
  from { transform: translateY(0); opacity: 1; }
  to { transform: translateY(-20px); opacity: 0; }
}
```

## 🛠️ **JavaScript Utilities**

### **🎨 Theme Management**
```javascript
// shared/scripts/theme-switcher.js
class ThemeManager {
  constructor() {
    this.currentTheme = localStorage.getItem('theme') || 'light';
    this.init();
  }
  
  init() {
    this.applyTheme(this.currentTheme);
    this.setupListeners();
  }
  
  applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    this.currentTheme = theme;
  }
  
  toggleTheme() {
    const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
    this.applyTheme(newTheme);
  }
  
  setupListeners() {
    // Theme toggle button listener
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
      themeToggle.addEventListener('click', () => this.toggleTheme());
    }
  }
}

// Initialize theme manager
const themeManager = new ThemeManager();
```

### **🎨 Design System Utilities**
```javascript
// shared/scripts/design-system.js
class DesignSystem {
  static updatePrimaryColor(color) {
    document.documentElement.style.setProperty('--primary-color', color);
  }
  
  static updateFontSize(size) {
    document.documentElement.style.setProperty('--font-size-base', size);
  }
  
  static updateSpacing(scale) {
    const spacingValues = {
      compact: '0.75rem',
      normal: '1rem',
      spacious: '1.25rem'
    };
    document.documentElement.style.setProperty('--spacing-4', spacingValues[scale]);
  }
  
  static getComputedValue(property) {
    return getComputedStyle(document.documentElement).getPropertyValue(property);
  }
}
```

## 📋 **Implementation Guide**

### **1. Setup Shared Styles**
```html
<!-- In each system's base template -->
<head>
  <!-- Design tokens first -->
  <link rel="stylesheet" href="/shared/styles/design-tokens.css">
  
  <!-- Theme -->
  <link rel="stylesheet" href="/shared/styles/themes/light.css">
  <link rel="stylesheet" href="/shared/styles/themes/dark.css">
  
  <!-- Components -->
  <link rel="stylesheet" href="/shared/styles/components/buttons.css">
  <link rel="stylesheet" href="/shared/styles/components/cards.css">
  <link rel="stylesheet" href="/shared/styles/components/forms.css">
  
  <!-- Layout -->
  <link rel="stylesheet" href="/shared/styles/layout/grid.css">
  <link rel="stylesheet" href="/shared/styles/layout/responsive.css">
  
  <!-- Animations -->
  <link rel="stylesheet" href="/shared/styles/animations/transitions.css">
  
  <!-- System-specific styles last -->
  <link rel="stylesheet" href="/styles/main.css">
</head>
```

### **2. Use Shared Components**
```html
<!-- In any template -->
{% include "shared/components/button.html" with 
   text="Upload Files"
   variant="primary"
   size="lg"
   icon="upload" %}

{% include "shared/components/card.html" with 
   title="File Upload"
   content=upload_form %}
```

### **3. Extend Base Template**
```html
<!-- yuetransfer/templates/base.html -->
{% extends "shared/base.html" %}

{% block content %}
  <div class="container">
    <div class="grid grid--cols-2">
      <div class="card">
        <!-- YUETransfer specific content -->
      </div>
    </div>
  </div>
{% endblock %}
```

## 🔄 **Making Design Changes**

### **🎨 Change Primary Color (Affects All Systems)**
```css
/* Edit: shared/styles/design-tokens.css */
:root {
  --primary-color: #059669; /* Changed from blue to green */
}
```
**Result:** All buttons, links, progress bars, and highlights across YUETransfer, YUEUpload, and TotalSegmentator instantly update to green theme.

### **📝 Change Typography (Affects All Systems)**
```css
/* Edit: shared/styles/design-tokens.css */
:root {
  --font-family-primary: 'Roboto', sans-serif; /* Changed from Inter to Roboto */
  --font-size-base: 18px; /* Increased from 16px */
}
```
**Result:** All text across all systems updates to use Roboto font and larger base size.

### **📏 Change Spacing (Affects All Systems)**
```css
/* Edit: shared/styles/design-tokens.css */
:root {
  --spacing-4: 1.5rem; /* Increased from 1rem */
}
```
**Result:** All padding, margins, and gaps across all systems become more spacious.

## 🎯 **Benefits of This Approach**

1. **🎨 Consistency**: All systems look and feel the same
2. **⚡ Performance**: No heavy frameworks, optimized CSS
3. **🔧 Maintainability**: Single source of truth for design
4. **🚀 Scalability**: Easy to add new components
5. **🎭 Flexibility**: Easy theme switching and customization
6. **📱 Responsive**: Mobile-first design approach
7. **♿ Accessibility**: Built-in accessibility features
8. **🔍 SEO**: Clean, semantic HTML

## 📚 **Documentation Maintenance**

This document should be updated whenever:
- New design tokens are added
- New components are created
- Theme changes are made
- New systems are added to the ecosystem

**Last Updated:** [Current Date]
**Version:** 1.0.0
**Maintainer:** [Your Name]

---

**🎨 This unified design system ensures consistent, maintainable, and beautiful UI across all TotalSegmentator components!**