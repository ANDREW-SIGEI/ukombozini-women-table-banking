Set up the frontend according to the following prompt:
  <frontend-prompt>
  Create detailed components with these requirements:
  1. Use 'use client' directive for client-side components
  2. Make sure to concatenate strings correctly using backslash
  3. Style with Tailwind CSS utility classes for responsive design
  4. Use Lucide React for icons (from lucide-react package). Do NOT use other UI libraries unless requested
  5. Use stock photos from picsum.photos where appropriate, only valid URLs you know exist
  6. Configure next.config.js image remotePatterns to enable stock photos from picsum.photos
  7. Create root layout.tsx page that wraps necessary navigation items to all pages
  8. MUST implement the navigation elements items in their rightful place i.e. Left sidebar, Top header
  9. Accurately implement necessary grid layouts
  10. Follow proper import practices:
     - Use @/ path aliases
     - Keep component imports organized
     - Update current src/app/page.tsx with new comprehensive code
     - Don't forget root route (page.tsx) handling
     - You MUST complete the entire prompt before stopping
  </frontend-prompt>

  <summary_title>
Ukombozini Financial Management Dashboard UI
</summary_title>

<image_analysis>
1. Navigation Elements:
- Primary navigation: Groups Registration, Field Officers, Savings Management, Loan Management, Loan Collections, Dividends & Interest, Accounting, Booster Agriculture Collection, Member Management
- Left sidebar navigation with collapsible sections
- Logo "UKOMBOZINI" positioned top-left
- "Chat with GPT" button fixed at bottom
- Secondary navigation includes Reports & Analytics, Overview, Settings
- Hierarchical menu structure with icons for each item

2. Layout Components:
- Left sidebar: 250px width, full height
- Main content area: Flexible width (calc(100% - 250px))
- Navigation items: 40px height each
- Content cards: ~300px width, flexible height
- Padding: 16px for content sections, 8px for navigation items

3. Content Sections:
- Dashboard cards with titles and descriptions
- Member Management section
- Loan Management section
- Financial Reports section
- Reports & Analytics section
- Each section contains descriptive text and action links

4. Interactive Controls:
- Expandable/collapsible sidebar menus
- Navigation hover states
- "Go to" action links
- Chat with GPT button (both in sidebar and content area)
- Section cards with hover effects

5. Colors:
- Primary: #1B3A57 (dark blue)
- Secondary: #E74C3C (red accent)
- Background: #F5F6F8
- Text: #333333
- Links: #2980B9
- Hover states: #234B6F

6. Grid/Layout Structure:
- Two-column layout (sidebar + content)
- Card grid system: 2x2 for dashboard items
- Responsive breakpoints at 768px, 1024px, 1440px
- Flexible content container with max-width 1200px
</image_analysis>

<development_planning>
1. Project Structure:
```
src/
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx
│   │   ├── MainContent.tsx
│   │   └── NavigationItem.tsx
│   ├── features/
│   │   ├── MemberManagement/
│   │   ├── LoanManagement/
│   │   └── Reports/
│   └── shared/
├── assets/
├── styles/
├── hooks/
└── utils/
```

2. Key Features:
- User authentication and role management
- Dynamic navigation system
- Financial transaction management
- Reporting and analytics dashboard
- Member and group management
- Loan processing system

3. State Management:
```typescript
interface AppState {
  auth: {
    user: User;
    permissions: string[];
  };
  navigation: {
    currentSection: string;
    expandedMenus: string[];
  };
  financial: {
    loans: Loan[];
    transactions: Transaction[];
  };
  members: {
    groups: Group[];
    individuals: Member[];
  }
}
```

4. Component Architecture:
- Layout components (Header, Sidebar, MainContent)
- Feature-specific components
- Shared UI components (Cards, Buttons, Forms)
- HOCs for authentication and permissions

5. Responsive Breakpoints:
```scss
$breakpoints: (
  'mobile': 320px,
  'tablet': 768px,
  'desktop': 1024px,
  'large': 1440px
);
```
</development_planning>