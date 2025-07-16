/**
 * NutriGenius Design System
 * Centralized design tokens and utilities for consistent theming
 */

// Color tokens
export const colors = {
  emerald: {
    50: 'hsl(142 80% 95%)',
    100: 'hsl(142 76% 90%)',
    200: 'hsl(142 76% 80%)',
    300: 'hsl(142 76% 70%)',
    400: 'hsl(142 76% 60%)',
    500: 'hsl(142 76% 50%)',
    600: 'hsl(142 76% 40%)',
    700: 'hsl(142 76% 30%)',
    800: 'hsl(142 76% 20%)',
    900: 'hsl(142 76% 10%)',
    primary: 'hsl(var(--emerald-primary))',
    'primary-light': 'hsl(var(--emerald-primary-light))',
    'primary-dark': 'hsl(var(--emerald-primary-dark))',
  },
  
  sage: {
    50: 'hsl(120 25% 95%)',
    100: 'hsl(120 20% 90%)',
    200: 'hsl(120 20% 80%)',
    300: 'hsl(120 20% 70%)',
    400: 'hsl(120 20% 60%)',
    500: 'hsl(120 20% 50%)',
    600: 'hsl(120 20% 40%)',
    700: 'hsl(120 20% 30%)',
    800: 'hsl(120 20% 20%)',
    900: 'hsl(120 20% 10%)',
    secondary: 'hsl(var(--sage-secondary))',
    'secondary-light': 'hsl(var(--sage-secondary-light))',
    'secondary-dark': 'hsl(var(--sage-secondary-dark))',
  },
  
  coral: {
    50: 'hsl(15 80% 95%)',
    100: 'hsl(15 80% 90%)',
    200: 'hsl(15 80% 80%)',
    300: 'hsl(15 80% 70%)',
    400: 'hsl(15 80% 60%)',
    500: 'hsl(15 80% 50%)',
    600: 'hsl(15 80% 40%)',
    700: 'hsl(15 80% 30%)',
    800: 'hsl(15 80% 20%)',
    900: 'hsl(15 80% 10%)',
    accent: 'hsl(var(--coral-accent))',
  },
  
  gold: {
    50: 'hsl(45 85% 95%)',
    100: 'hsl(45 85% 90%)',
    200: 'hsl(45 85% 80%)',
    300: 'hsl(45 85% 70%)',
    400: 'hsl(45 85% 60%)',
    500: 'hsl(45 85% 50%)',
    600: 'hsl(45 85% 40%)',
    700: 'hsl(45 85% 30%)',
    800: 'hsl(45 85% 20%)',
    900: 'hsl(45 85% 10%)',
    accent: 'hsl(var(--gold-accent))',
  },
  
  slate: {
    50: 'hsl(var(--slate-50))',
    100: 'hsl(var(--slate-100))',
    200: 'hsl(var(--slate-200))',
    300: 'hsl(var(--slate-300))',
    400: 'hsl(var(--slate-400))',
    500: 'hsl(var(--slate-500))',
    600: 'hsl(var(--slate-600))',
    700: 'hsl(var(--slate-700))',
    800: 'hsl(var(--slate-800))',
    900: 'hsl(var(--slate-900))',
  },
  
  semantic: {
    success: 'hsl(var(--success))',
    warning: 'hsl(var(--warning))',
    error: 'hsl(var(--error))',
    info: 'hsl(var(--info))',
  },
};

// Typography tokens
export const typography = {
  fontFamily: {
    sans: 'var(--font-sans)',
    serif: 'var(--font-serif)',
    mono: 'var(--font-mono)',
  },
  
  fontSize: {
    xs: 'var(--font-size-xs)',
    sm: 'var(--font-size-sm)',
    base: 'var(--font-size-base)',
    lg: 'var(--font-size-lg)',
    xl: 'var(--font-size-xl)',
    '2xl': 'var(--font-size-2xl)',
    '3xl': 'var(--font-size-3xl)',
    '4xl': 'var(--font-size-4xl)',
    '5xl': 'var(--font-size-5xl)',
    '6xl': 'var(--font-size-6xl)',
    '7xl': 'var(--font-size-7xl)',
  },
  
  lineHeight: {
    none: 'var(--line-height-none)',
    tight: 'var(--line-height-tight)',
    snug: 'var(--line-height-snug)',
    normal: 'var(--line-height-normal)',
    relaxed: 'var(--line-height-relaxed)',
    loose: 'var(--line-height-loose)',
  },
  
  letterSpacing: {
    tighter: 'var(--letter-spacing-tighter)',
    tight: 'var(--letter-spacing-tight)',
    normal: 'var(--letter-spacing-normal)',
    wide: 'var(--letter-spacing-wide)',
    wider: 'var(--letter-spacing-wider)',
    widest: 'var(--letter-spacing-widest)',
  },
};

// Spacing tokens
export const spacing = {
  0: 'var(--spacing-0)',
  px: 'var(--spacing-px)',
  0.5: 'var(--spacing-05)',
  1: 'var(--spacing-1)',
  1.5: 'var(--spacing-15)',
  2: 'var(--spacing-2)',
  2.5: 'var(--spacing-25)',
  3: 'var(--spacing-3)',
  3.5: 'var(--spacing-35)',
  4: 'var(--spacing-4)',
  5: 'var(--spacing-5)',
  6: 'var(--spacing-6)',
  7: 'var(--spacing-7)',
  8: 'var(--spacing-8)',
  9: 'var(--spacing-9)',
  10: 'var(--spacing-10)',
  11: 'var(--spacing-11)',
  12: 'var(--spacing-12)',
  14: 'var(--spacing-14)',
  16: 'var(--spacing-16)',
  20: 'var(--spacing-20)',
  24: 'var(--spacing-24)',
  28: 'var(--spacing-28)',
  32: 'var(--spacing-32)',
  36: 'var(--spacing-36)',
  40: 'var(--spacing-40)',
  44: 'var(--spacing-44)',
  48: 'var(--spacing-48)',
  52: 'var(--spacing-52)',
  56: 'var(--spacing-56)',
  60: 'var(--spacing-60)',
  64: 'var(--spacing-64)',
  72: 'var(--spacing-72)',
  80: 'var(--spacing-80)',
  96: 'var(--spacing-96)',
};

// Border radius tokens
export const borderRadius = {
  none: 'var(--radius-none)',
  sm: 'var(--radius-sm)',
  md: 'var(--radius-md)',
  lg: 'var(--radius-lg)',
  xl: 'var(--radius-xl)',
  '2xl': 'var(--radius-2xl)',
  '3xl': 'var(--radius-3xl)',
  full: 'var(--radius-full)',
};

// Shadow tokens
export const shadows = {
  sm: 'var(--shadow-sm)',
  md: 'var(--shadow-md)',
  lg: 'var(--shadow-lg)',
  xl: 'var(--shadow-xl)',
  '2xl': 'var(--shadow-2xl)',
  inner: 'var(--shadow-inner)',
  none: 'var(--shadow-none)',
};

// Transition tokens
export const transitions = {
  none: 'var(--transition-none)',
  all: 'var(--transition-all)',
  colors: 'var(--transition-colors)',
  opacity: 'var(--transition-opacity)',
  shadow: 'var(--transition-shadow)',
  transform: 'var(--transition-transform)',
};

// Duration tokens
export const durations = {
  75: 'var(--duration-75)',
  100: 'var(--duration-100)',
  150: 'var(--duration-150)',
  200: 'var(--duration-200)',
  300: 'var(--duration-300)',
  500: 'var(--duration-500)',
  700: 'var(--duration-700)',
  1000: 'var(--duration-1000)',
};

// Z-index tokens
export const zIndex = {
  0: 'var(--z-0)',
  10: 'var(--z-10)',
  20: 'var(--z-20)',
  30: 'var(--z-30)',
  40: 'var(--z-40)',
  50: 'var(--z-50)',
  auto: 'var(--z-auto)',
  dropdown: 'var(--z-dropdown)',
  sticky: 'var(--z-sticky)',
  fixed: 'var(--z-fixed)',
  'modal-backdrop': 'var(--z-modal-backdrop)',
  modal: 'var(--z-modal)',
  popover: 'var(--z-popover)',
  tooltip: 'var(--z-tooltip)',
};

// Component-specific tokens
export const components = {
  button: {
    primary: {
      bg: 'var(--button-primary-bg)',
      hover: 'var(--button-primary-hover)',
      text: 'var(--button-primary-text)',
    },
    secondary: {
      bg: 'var(--button-secondary-bg)',
      hover: 'var(--button-secondary-hover)',
      text: 'var(--button-secondary-text)',
    },
    ghost: {
      hover: 'var(--button-ghost-hover)',
      text: 'var(--button-ghost-text)',
    },
  },
  
  input: {
    bg: 'var(--input-bg)',
    border: 'var(--input-border)',
    borderFocus: 'var(--input-border-focus)',
    placeholder: 'var(--input-placeholder)',
    text: 'var(--input-text)',
  },
  
  card: {
    bg: 'var(--card-bg)',
    border: 'var(--card-border)',
    shadow: 'var(--card-shadow)',
  },
  
  nav: {
    bg: 'var(--nav-bg)',
    border: 'var(--nav-border)',
    text: 'var(--nav-text)',
    textActive: 'var(--nav-text-active)',
  },
};

// Utility functions
export const utils = {
  // Generate gradient classes
  gradient: (from: string, to: string, via?: string) => {
    if (via) {
      return `bg-gradient-to-r from-${from} via-${via} to-${to}`;
    }
    return `bg-gradient-to-r from-${from} to-${to}`;
  },
  
  // Generate glass effect classes
  glass: (opacity: number = 80) => {
    return `bg-white/${opacity} dark:bg-slate-900/${opacity} backdrop-blur-sm border border-slate-200/50 dark:border-slate-700/50`;
  },
  
  // Responsive container classes
  container: {
    default: 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8',
    sm: 'max-w-3xl mx-auto px-4 sm:px-6 lg:px-8',
    xs: 'max-w-xl mx-auto px-4 sm:px-6 lg:px-8',
  },
};

// Type definitions
export type ColorVariant = keyof typeof colors.emerald;
export type FontSize = keyof typeof typography.fontSize;
export type Spacing = keyof typeof spacing;
export type BorderRadius = keyof typeof borderRadius;
export type Shadow = keyof typeof shadows;

// Export all as default
export default {
  colors,
  typography,
  spacing,
  borderRadius,
  shadows,
  transitions,
  durations,
  zIndex,
  components,
  utils,
};