# NutriGenius Design System

A comprehensive design system for the NutriGenius AI-powered nutrition application, featuring elegant typography, consistent color schemes, and reusable components.

## 🎨 Color Palette

### Primary Colors
- **Emerald** - Primary brand color representing health and nutrition
  - Light: `hsl(142, 76%, 45%)`
  - Base: `hsl(142, 76%, 36%)`
  - Dark: `hsl(142, 76%, 30%)`

### Secondary Colors
- **Sage** - Secondary color for supporting elements
  - Light: `hsl(120, 20%, 95%)`
  - Base: `hsl(120, 20%, 90%)`
  - Dark: `hsl(120, 20%, 80%)`

### Accent Colors
- **Coral** - Warm accent for CTAs and highlights
- **Gold** - Premium accent for special features
- **Lavender** - AI/tech accent for intelligent features

### Neutral Colors
- **Slate** - Complete neutral scale from 50-900
- **Semantic** - Success, warning, error, info colors

## 📝 Typography

### Font Families
- **Primary**: Inter (Sans-serif) - Body text, UI elements
- **Secondary**: Playfair Display (Serif) - Headings, titles
- **Monospace**: Source Sans 3 - Code, data display

### Font Weights
- Light: 300
- Normal: 400
- Medium: 500
- Semibold: 600
- Bold: 700
- Extrabold: 800

### Type Scale
- xs: 0.75rem (12px)
- sm: 0.875rem (14px)
- base: 1rem (16px)
- lg: 1.125rem (18px)
- xl: 1.25rem (20px)
- 2xl: 1.5rem (24px)
- 3xl: 1.875rem (30px)
- 4xl: 2.25rem (36px)
- 5xl: 3rem (48px)
- 6xl: 3.75rem (60px)
- 7xl: 4.5rem (72px)

## 🎯 Design Tokens

### Spacing
Based on 0.25rem (4px) increments:
- 0-96 (0-384px) in logical steps

### Border Radius
- sm: 0.125rem (2px)
- md: 0.375rem (6px)
- lg: 0.5rem (8px)
- xl: 0.75rem (12px)
- 2xl: 1rem (16px)
- 3xl: 1.5rem (24px)
- full: 9999px

### Shadows
- sm: Subtle elevation
- md: Default elevation
- lg: Prominent elevation
- xl: High elevation
- 2xl: Maximum elevation

## 🧩 Components

### PageWrapper
Consistent page layout with customizable backgrounds:
```tsx
<PageWrapper 
  background="gradient" 
  showPattern
  container="default"
>
  {/* Content */}
</PageWrapper>
```

### Button
Enhanced button component with variants:
- `default` - Primary emerald
- `secondary` - Sage secondary
- `premium` - Gradient for premium features
- `destructive` - Error states
- `ghost` - Minimal style

### Card
Reusable card component with variants:
- `default` - Standard card
- `elevated` - With enhanced shadow
- `outline` - Border emphasis

## 🔄 CSS Variables

All colors and spacing are defined as CSS custom properties for easy theming:

```css
:root {
  --emerald-primary: 142 76% 36%;
  --sage-secondary: 120 20% 90%;
  --coral-accent: 15 80% 50%;
  /* ... more variables */
}
```

## 📱 Responsive Design

### Breakpoints
- sm: 640px
- md: 768px
- lg: 1024px
- xl: 1280px
- 2xl: 1536px

### Container Sizes
- `container` - max-w-7xl (1280px)
- `container-sm` - max-w-3xl (768px)
- `container-xs` - max-w-xl (576px)

## 🎭 Dark Mode Support

Complete dark mode support with automatic color inversion:
- Background colors
- Text colors
- Border colors
- Component states

## 🚀 Usage Examples

### Basic Page Structure
```tsx
import { PageWrapper, PageHeader, Section, Card } from '@/components/layout/PageWrapper';

export default function MyPage() {
  return (
    <PageWrapper background="gradient">
      <PageHeader 
        title="My Page" 
        description="Page description here"
      />
      
      <Section title="Section Title">
        <Card>
          <p>Content goes here</p>
        </Card>
      </Section>
    </PageWrapper>
  );
}
```

### Custom Button Usage
```tsx
import { Button } from '@/components/ui/button';
import { Sparkles } from 'lucide-react';

<Button variant="premium" size="lg" leftIcon={<Sparkles />}>
  Get Premium Plan
</Button>
```

## 🎨 Customization

### Changing Primary Color
Update the CSS variables in `globals.css`:
```css
:root {
  --emerald-primary: 200 80% 50%; /* Change to blue */
}
```

### Adding New Font
1. Import in `layout.tsx`
2. Add to CSS variables
3. Update Tailwind config

### Custom Spacing
Modify the spacing scale in `variables.css`:
```css
:root {
  --spacing-custom: 2.75rem;
}
```

## 📁 File Structure
```
dietapp-frontend/
├── src/
│   ├── app/
│   │   └── globals.css          # Global styles
│   ├── components/
│   │   ├── ui/
│   │   │   └── button.tsx       # Button component
│   │   └── layout/
│   │       └── PageWrapper.tsx  # Layout components
│   ├── styles/
│   │   └── variables.css        # CSS variables
│   └── lib/
│       └── design-system.ts     # Design tokens
└── DESIGN_SYSTEM.md            # This file
```

## 🎯 Best Practices

1. **Use CSS Variables**: Always use CSS variables for colors and spacing
2. **Component Reusability**: Use PageWrapper for consistent page layouts
3. **Responsive Design**: Use container classes for responsive layouts
4. **Dark Mode**: Test all components in both light and dark modes
5. **Accessibility**: Ensure proper contrast ratios and focus states
6. **Performance**: Use font-display: swap for web fonts
7. **Consistency**: Follow the established spacing and sizing scale

## 🔧 Development Tools

### Tailwind CSS
Extended with custom colors and utilities matching the design system.

### TypeScript
Full TypeScript support with proper type definitions for all components.

### Responsive Testing
Use browser dev tools to test responsive behavior across all breakpoints.