---
name: Emerald Enterprise
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#3f4944'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#6f7973'
  outline-variant: '#bec9c2'
  surface-tint: '#1b6b51'
  primary: '#004532'
  on-primary: '#ffffff'
  primary-container: '#065f46'
  on-primary-container: '#8bd6b7'
  inverse-primary: '#8bd6b6'
  secondary: '#545f73'
  on-secondary: '#ffffff'
  secondary-container: '#d5e0f8'
  on-secondary-container: '#586377'
  tertiary: '#333f39'
  on-tertiary: '#ffffff'
  tertiary-container: '#4a564f'
  on-tertiary-container: '#becac2'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#a6f2d1'
  primary-fixed-dim: '#8bd6b6'
  on-primary-fixed: '#002116'
  on-primary-fixed-variant: '#00513b'
  secondary-fixed: '#d8e3fb'
  secondary-fixed-dim: '#bcc7de'
  on-secondary-fixed: '#111c2d'
  on-secondary-fixed-variant: '#3c475a'
  tertiary-fixed: '#d9e6dd'
  tertiary-fixed-dim: '#bdcac1'
  on-tertiary-fixed: '#131e19'
  on-tertiary-fixed-variant: '#3e4943'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  display-lg:
    fontFamily: Hanken Grotesk
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Hanken Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Hanken Grotesk
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  title-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  data-tabular:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  container-padding: 32px
  gutter: 24px
  section-gap: 48px
  table-row-height: 56px
---

## Brand & Style

The design system is engineered for **premium enterprise intelligence**. It targets procurement officers, lead engineers, and financial controllers who require precision and authority. The brand personality is rooted in "Analytical Luxury"—combining the high-stakes nature of multi-million dollar Bill of Quantities (BOQ) with a refined, frictionless user experience.

The visual direction follows a **Corporate Modern** style with subtle **Minimalist** influences:
- **Trustworthy & Structured:** Using a strict grid and deep, professional greens to evoke financial stability and growth.
- **High-End SaaS Aesthetic:** Utilizing generous whitespace and high-quality typography to ensure the interface feels "expensive" and intentionally designed.
- **Clarity over Clutter:** Data is the hero. The UI recedes into the background, providing a sophisticated canvas for complex pricing information.

## Colors

The palette pivots from generic utility to executive-grade sophistication.

- **Primary (Emerald Forest):** Used for primary calls to action, active states, and success indicators. It suggests growth and professional vigor.
- **Secondary (Deep Slate):** Used for high-contrast text and structural elements like headers or sidebars. It provides a grounded, "matte" feel.
- **Tertiary (Soft Mint):** An intentional background wash for selected rows, secondary containers, and informational banners.
- **Neutrals:** A scale of cool greys (Slate) to ensure that text remains highly legible without the harshness of pure black, maintaining a "business-matte" appearance.

## Typography

Typography focuses on legibility and information density. 

- **Display & Headlines:** Using **Hanken Grotesk** provides a sharp, contemporary "tech" edge to the enterprise product. It feels precise and modern.
- **Body & Data:** **Inter** is utilized for its exceptional performance in data-heavy environments. 
- **Tabular Data:** For the BOQ tables, use "tnum" (tabular numbers) to ensure columns of figures align perfectly, aiding in quick scanning of price variations.
- **Labels:** Small caps with slight letter-spacing are used for table headers and metadata to distinguish them clearly from interactive data points.

## Layout & Spacing

The system employs a **Fixed Grid** philosophy for desktop to maintain a premium "dashboard" feel, centering content at a maximum width of 1440px.

- **Grid:** 12-column layout with 24px gutters.
- **Rhythm:** An 8px base unit controls all padding and margins. 
- **Density:** While the system is "clean," it maintains a professional density appropriate for procurement work. Table rows are set to a comfortable 56px height to balance readability with data volume.
- **Responsibility:** On mobile, margins shrink to 16px, and 12 columns collapse to 1, with data tables converting to cards or horizontally scrollable containers.

## Elevation & Depth

Visual hierarchy is established through **Tonal Layers** and **Ambient Shadows** rather than heavy borders.

- **Surface 0 (Background):** `surface_matte` (#F8FAFC) creates a soft, non-reflective base.
- **Surface 1 (Cards/Tables):** Pure white (#FFFFFF) with a very soft, diffused shadow (0px 4px 20px rgba(0, 0, 0, 0.04)).
- **Interactive States:** On hover, cards lift slightly with a more pronounced shadow and a 1px border stroke using `primary_color` at 10% opacity.
- **Backdrop:** Modals use a Deep Slate backdrop at 40% opacity with a high-strength background blur (12px) to maintain the "luxurious" feel.

## Shapes

The shape language is refined and approachable. 
- **Standard Radius:** 8px (roundedness 2) is the default for buttons, input fields, and small cards.
- **Large Components:** 16px (rounded-lg) for main container cards and modal windows.
- **Status Badges:** 4px or fully pill-shaped (rounded-full) depending on the context of the tag.

## Components

### Buttons
- **Primary:** Forest Green background with white text. High-contrast, bold, 8px radius.
- **Secondary:** White background with Deep Slate border (1px) and text.
- **Ghost:** No background, Emerald Green text, used for less critical actions.

### Data Tables (Critical)
- **Header:** Slate background with white or light-grey uppercase labels.
- **Rows:** White background with 1px Slate border-bottom. Alternate rows or hover states use the Soft Mint wash.
- **Cells:** Numeric values are right-aligned; status badges are center-aligned.

### Input Fields
- Matte grey background with a subtle inset shadow or 1px border. 
- Focus state: 2px Forest Green outline with a soft glow.

### Status Badges
- **Draft:** Grey/Slate background, dark text.
- **Pending:** Soft amber wash, dark amber text.
- **Approved:** Soft Mint background, Forest Green text.

### Cards
- White background, 8px radius, soft ambient shadow. Used to group "Search Source" controls or "Price Summary" statistics.