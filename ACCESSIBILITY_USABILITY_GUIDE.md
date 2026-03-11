# Stock Exchange Board - Accessibility & Usability Guide

**Version**: 1.0.0
**Date**: March 11, 2026
**Status**: Implementation Guide
**Compliance Target**: WCAG 2.1 AA

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Accessibility Standards](#accessibility-standards)
3. [Visual Accessibility](#visual-accessibility)
4. [Keyboard Navigation](#keyboard-navigation)
5. [Screen Reader Support](#screen-reader-support)
6. [Mobile Accessibility](#mobile-accessibility)
7. [Usability Best Practices](#usability-best-practices)
8. [Testing & Validation](#testing--validation)
9. [Common Patterns & Solutions](#common-patterns--solutions)
10. [Accessibility Checklist](#accessibility-checklist)

---

## Executive Summary

This guide ensures the stock exchange board application meets WCAG 2.1 AA standards while remaining intuitive for retail investors of varying technical abilities.

### Key Accessibility Goals

- **Perceivable**: Information and UI components are visible/audible to all users
- **Operable**: Navigation works with keyboard, mouse, touch, and voice
- **Understandable**: Interface is clear and predictable
- **Robust**: Compatible with assistive technologies

### Target Users

- Retail investors aged 25-65
- Vision impairments (color blindness, low vision, blindness)
- Motor impairments (tremors, paralysis, limited dexterity)
- Hearing impairments
- Cognitive impairments (ADHD, dyslexia, learning disabilities)
- Non-native English speakers

---

## Accessibility Standards

### WCAG 2.1 Compliance Levels

**Level A**: Minimum compliance (rarely sufficient alone)
**Level AA**: Industry standard for most digital products (TARGET)
**Level AAA**: Enhanced compliance (aspirational)

### Stock Exchange Board Targets

| Criterion | Level | Target | Status |
|-----------|-------|--------|--------|
| Contrast (text) | AA | 4.5:1 minimum | ✓ |
| Contrast (large text) | AA | 3:1 minimum | ✓ |
| Contrast (UI components) | AA | 3:1 minimum | ✓ |
| Keyboard access | A | All functionality | ✓ |
| Focus visible | AA | Always visible | ✓ |
| Color not sole differentiator | A | Yes | ✓ |
| Text alternatives | A | For all images | ✓ |
| Video captions | AA | All videos | ✓ |
| Audio descriptions | AA | Critical videos | ✓ |
| Motion not essential | A | Or can be disabled | ✓ |
| Meaningful sequence | A | Logical order | ✓ |
| Identify purpose | AA | Clear labels | ✓ |
| Error identification | A | Specific messages | ✓ |
| Error prevention | AA | Confirmation for critical actions | ✓ |
| Label clarity | A | Descriptive labels | ✓ |
| Consistent navigation | AA | Patterns repeat | ✓ |

---

## Visual Accessibility

### Color Contrast Requirements

#### Text Contrast Ratios

**Normal Text** (14px or smaller):
- Minimum: 4.5:1 (AA)
- Enhanced: 7:1 (AAA)

**Large Text** (18px+ bold or 24px+ regular):
- Minimum: 3:1 (AA)
- Enhanced: 4.5:1 (AAA)

**UI Components** (borders, backgrounds):
- Minimum: 3:1 (AA)
- Enhanced: 4.5:1 (AAA)

#### Color Combinations to Use

**Light Mode**:
- Gray-900 (#111827) text on White (#FFFFFF): 18:1 ✓ AAA
- Gray-900 text on Gray-50 (#F9FAFB): 15:1 ✓ AAA
- Gray-600 (#4B5563) on White: 7:1 ✓ AAA
- Green-600 (#16A34A) on Gray-50: 6:1 ✓ AA
- Red-600 (#DC2626) on Gray-50: 6:1 ✓ AA

**Dark Mode**:
- Gray-50 text on Gray-950 (#030712): 18:1 ✓ AAA
- Gray-400 (#9CA3AF) on Gray-900: 7:1 ✓ AAA
- Green-400 (#4ADE80) on Gray-950: 9:1 ✓ AAA
- Red-400 (#F87171) on Gray-950: 8:1 ✓ AAA

#### Color Contrast Testing

Use these tools to verify:
- **WebAIM Contrast Checker** (webaim.org/resources/contrastchecker)
- **Color Contrast Analyzer** (TPGi tool)
- **Axe DevTools** (browser extension)
- **Lighthouse** (built into Chrome DevTools)

#### Avoid These Combinations

- Gray-400 on white (2.5:1) ✗
- Gray-500 on Gray-50 (2.2:1) ✗
- Light colors on light backgrounds ✗
- Dark colors on dark backgrounds ✗

### Color-Blind Friendly Design

#### Don't Rely on Color Alone

**Problem**: User sees green/red in chart, but can't distinguish without additional cue

**Solutions**:
1. Add icons: ↑ (up), ↓ (down), + (gain), − (loss)
2. Add patterns: Solid (gain), striped (loss)
3. Add text labels: Always include percentage text
4. Add badges: Success, Danger, Warning

#### Examples

```
❌ Bad:   [Red bar with no label]
✓ Good:   [Red bar] [−2.5%] [Down arrow icon]

❌ Bad:   [Green candlestick]
✓ Good:   [Green candlestick] [↑ Up] [+1.2%]

❌ Bad:   [Red sell button]
✓ Good:   [Red button] [SELL] [Text: "Sell 100 shares"]
```

#### Simulate Color Blindness

Use **Coblis** (color blindness simulator) to test:
- Deuteranopia (red-green, ~1% males)
- Protanopia (red-green, ~1% males)
- Tritanopia (blue-yellow, <1%)
- Achromatopsia (total, <1%)

### Font & Text Considerations

#### Readable Font Sizes

**Desktop**:
- Body text minimum: 14px
- Labels minimum: 12px
- Headings: 20px+

**Mobile**:
- All text minimum: 16px (prevents auto-zoom)
- Body text: 16px-18px
- Labels: 14px-16px

#### Font Choices

**Recommended**:
- Inter: Excellent readability, metrics optimized
- System fonts: -apple-system, BlinkMacSystemFont, "Segoe UI"
- Roboto: Good fallback for Android

**Avoid**:
- Cursive fonts (hard to read)
- Thin weights (<400)
- Decorative fonts for body text

#### Line Spacing

**Minimum**: 1.5 line-height (WCAG AAA requirement)

```css
/* Good */
body {
  line-height: 1.5;
}

/* Also acceptable */
p {
  line-height: 1.6;
}
```

### Visual Design Patterns

#### Non-Color Differentiators

**For Gains/Losses**:
```
✓ Green + Up arrow + Text "+2.5%"
✓ Green + Up arrow + Positive value
✓ Green + Checkmark + "Profit"
```

**For Alerts**:
```
✓ Red + X icon + "Error"
✓ Yellow + Warning triangle + "Caution"
✓ Blue + Info icon + "Information"
```

#### Icons Accessibility

**Icon-Only Buttons**:
```html
<!-- Good -->
<button aria-label="Set price alert">
  <BellIcon />
</button>

<!-- Also good -->
<button aria-label="Add to watchlist">
  <StarIcon />
</button>

<!-- Bad -->
<button>
  <BellIcon /> <!-- No label -->
</button>
```

**Icons with Text**:
```html
<!-- Good -->
<button>
  <ArrowUpIcon /> +2.5%
</button>

<!-- Also good -->
<span>
  <CheckIcon /> Order confirmed
</span>
```

---

## Keyboard Navigation

### Navigation Model

**Tab Order Flow** (left-to-right, top-to-bottom):
1. Skip to main content link (hidden until focused)
2. Logo/home link
3. Search input
4. Main navigation items
5. User menu
6. Main content area
7. Footer links

### Keyboard Shortcuts

**Global Shortcuts**:
- `Tab`: Move to next element
- `Shift+Tab`: Move to previous element
- `Enter`: Activate button
- `Space`: Toggle checkbox, activate button
- `Escape`: Close modal/dropdown/menu
- `Arrow Keys`: Navigate lists, select options

**Application Shortcuts** (optional, but helpful):
- `/`: Focus search box
- `?`: Show keyboard shortcuts help
- `g`: Go to dashboard
- `w`: Go to watchlist
- `p`: Go to portfolio

### Implementation Example

```html
<!-- Keyboard-accessible dropdown -->
<div class="dropdown">
  <button
    id="dropdown-trigger"
    aria-haspopup="listbox"
    aria-expanded="false"
    aria-controls="dropdown-list"
  >
    Market Type
    <ChevronDownIcon />
  </button>

  <ul
    id="dropdown-list"
    role="listbox"
    class="hidden"
  >
    <li role="option">All Markets</li>
    <li role="option" aria-selected="true">US Only</li>
    <li role="option">International</li>
  </ul>
</div>

<script>
// Keyboard handling
const trigger = document.getElementById('dropdown-trigger');
const list = document.getElementById('dropdown-list');
let selectedIndex = 1; // "US Only" selected

trigger.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault();
    list.classList.toggle('hidden');
  }
});

list.addEventListener('keydown', (e) => {
  const items = list.querySelectorAll('[role="option"]');

  if (e.key === 'ArrowDown') {
    selectedIndex = (selectedIndex + 1) % items.length;
    items[selectedIndex].focus();
  }

  if (e.key === 'ArrowUp') {
    selectedIndex = (selectedIndex - 1 + items.length) % items.length;
    items[selectedIndex].focus();
  }

  if (e.key === 'Enter') {
    items[selectedIndex].click();
    list.classList.add('hidden');
  }

  if (e.key === 'Escape') {
    list.classList.add('hidden');
    trigger.focus();
  }
});
</script>
```

### Focus Management

#### Focus Indicator Style

```css
/* Clear, visible focus indicator */
button:focus-visible,
input:focus-visible,
a:focus-visible {
  outline: 2px solid #2563EB;      /* Blue outline */
  outline-offset: 2px;              /* Space from element */
}

/* Alternative: thick border */
button:focus-visible {
  border: 2px solid #2563EB;
}

/* Avoid: outline-offset: 0 (too close) */
/* Avoid: outline: 1px (too thin) */
```

#### Focus Trap (Modals)

```typescript
// Keep focus inside modal
const focusableElements = modal.querySelectorAll(
  'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
);
const firstElement = focusableElements[0];
const lastElement = focusableElements[focusableElements.length - 1];

modal.addEventListener('keydown', (e) => {
  if (e.key !== 'Tab') return;

  if (e.shiftKey) {
    if (document.activeElement === firstElement) {
      lastElement.focus();
      e.preventDefault();
    }
  } else {
    if (document.activeElement === lastElement) {
      firstElement.focus();
      e.preventDefault();
    }
  }
});
```

#### Focus Restoration

After closing a modal/dialog, return focus to the button that opened it:

```typescript
const openButton = document.getElementById('open-modal-btn');
const modal = document.getElementById('modal');
const closeButton = modal.querySelector('[data-close]');

openButton.addEventListener('click', () => {
  modal.showModal();
});

closeButton.addEventListener('click', () => {
  modal.close();
  openButton.focus(); // Return focus
});
```

---

## Screen Reader Support

### ARIA Labels

**For Icon-Only Elements**:
```html
<!-- Bell icon for alerts -->
<button aria-label="Manage price alerts">
  <BellIcon />
</button>

<!-- Search icon -->
<button aria-label="Search stocks">
  <SearchIcon />
</button>
```

**For Complex Components**:
```html
<!-- Chart with text alternative -->
<figure>
  <svg aria-label="AAPL stock price chart" role="img">
    <!-- Chart code -->
  </svg>
  <figcaption>
    Apple (AAPL) stock price over the last 7 days:
    Monday $170, Tuesday $172, Wednesday $171, Thursday $172.50
  </figcaption>
</figure>
```

### ARIA Descriptions

```html
<!-- Input with helper text -->
<label for="target-price">Target Price</label>
<input
  id="target-price"
  type="number"
  aria-describedby="price-help"
/>
<small id="price-help">
  Set a price target for your alert. Example: $180.00
</small>

<!-- Error messages -->
<input
  id="quantity"
  aria-invalid="true"
  aria-describedby="qty-error"
/>
<div id="qty-error" role="alert">
  Quantity must be at least 1 share
</div>
```

### Live Regions

**For Real-Time Updates**:

```html
<!-- Price updates -->
<div aria-live="polite" aria-atomic="true" id="price-update">
  AAPL updated to $172.50, up 1.25%
</div>

<!-- Urgent alerts -->
<div aria-live="assertive" role="alert" id="price-alert">
  Alert triggered! AAPL reached your target price of $180
</div>

<!-- Status messages -->
<div aria-live="polite" aria-label="Order status" id="order-status">
  Placing order... Please wait
</div>
```

**Update Annoucement in Code**:

```typescript
const updatePrice = (symbol, newPrice, change, changePercent) => {
  // Update DOM
  priceElement.textContent = newPrice;

  // Announce to screen readers
  const announcement = `${symbol} updated to $${newPrice},
    ${change > 0 ? 'up' : 'down'} ${Math.abs(changePercent)}%`;

  const liveRegion = document.getElementById('price-update');
  liveRegion.textContent = announcement;
};
```

### Table Accessibility

**Proper Table Structure**:

```html
<!-- Good -->
<table>
  <thead>
    <tr>
      <th scope="col">Symbol</th>
      <th scope="col">Price</th>
      <th scope="col">Change</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">AAPL</th>
      <td>$172.50</td>
      <td>+1.25%</td>
    </tr>
  </tbody>
</table>

<!-- Bad -->
<table>
  <tr>
    <td>AAPL</td>
    <td>$172.50</td>
    <td>+1.25%</td>
  </tr>
</table>
```

### Form Accessibility

**Label Association**:

```html
<!-- Good -->
<label for="quantity">Quantity</label>
<input id="quantity" type="number" min="1" required />

<!-- Bad -->
<label>Quantity <input type="number" /></label> <!-- Weak association -->

<!-- Also bad -->
<input type="number" placeholder="Quantity" /> <!-- No label -->
```

### Heading Hierarchy

```html
<!-- Good -->
<h1>Dashboard</h1>
<h2>Portfolio Overview</h2>
<h3>Top Holdings</h3>

<!-- Bad -->
<h1>Dashboard</h1>
<h3>Portfolio Overview</h3> <!-- Skips h2 -->

<!-- Also bad -->
<h1>Dashboard</h1>
<h1>Portfolio Overview</h1> <!-- Multiple h1s -->
```

**Rule**: Never skip heading levels (h1 → h2 → h3, not h1 → h3)

### Landmark Navigation

```html
<!-- Header with navigation -->
<header>
  <nav aria-label="Main navigation">
    <ul>
      <li><a href="/">Home</a></li>
      <li><a href="/market">Market</a></li>
      <li><a href="/portfolio">Portfolio</a></li>
    </ul>
  </nav>
</header>

<!-- Main content area -->
<main id="main-content">
  <h1>Page Title</h1>
  <!-- Content -->
</main>

<!-- Footer with additional links -->
<footer>
  <nav aria-label="Footer">
    <ul>
      <li><a href="/about">About</a></li>
      <li><a href="/contact">Contact</a></li>
      <li><a href="/privacy">Privacy</a></li>
    </ul>
  </nav>
</footer>

<!-- Skip to main content link (visible on focus) -->
<a href="#main-content" class="sr-only-focus">
  Skip to main content
</a>
```

**CSS for Screen-Reader-Only, Focus-Visible Links**:

```css
.sr-only-focus {
  position: absolute;
  left: -9999px;
  width: 1px;
  height: 1px;
  overflow: hidden;
}

.sr-only-focus:focus {
  position: relative;
  left: 0;
  width: auto;
  height: auto;
  background: #2563EB;
  color: white;
  padding: 8px 16px;
  z-index: 999;
}
```

---

## Mobile Accessibility

### Touch Target Sizes

**Minimum (WCAG A)**: 44x44 CSS pixels
**Recommended (WCAG AAA)**: 48x48 CSS pixels

```css
/* Button sizing */
button {
  min-width: 44px;
  min-height: 44px;
  padding: 12px 16px; /* Minimum for 44px height */
}

/* Larger on mobile for comfort */
@media (max-width: 768px) {
  button {
    min-height: 48px;
    padding: 14px 16px;
  }
}
```

### Touch Spacing

**Minimum gap between interactive elements**: 8px

```css
button + button {
  margin-left: 8px;
}

.icon-button + .icon-button {
  margin-left: 8px;
}
```

### Mobile Input Best Practices

**Font Size to Prevent Zoom**:
```html
<!-- Good: 16px base font prevents auto-zoom -->
<input
  type="text"
  style="font-size: 16px;"
/>

<!-- Bad: 14px or smaller causes zoom on iOS Safari -->
<input
  type="text"
  style="font-size: 14px;"
/>
```

**Appropriate Input Types**:
```html
<!-- Shows numeric keyboard -->
<input type="number" inputmode="numeric" />

<!-- Shows decimal numeric keyboard -->
<input type="number" step="0.01" />

<!-- Shows email keyboard -->
<input type="email" />

<!-- Shows phone keyboard -->
<input type="tel" />

<!-- Shows decimal keyboard -->
<input type="number" inputmode="decimal" />
```

### Mobile Touch Gestures

**Support These Gestures**:
- Tap (activate button)
- Double-tap (zoom)
- Long-press (context menu)
- Swipe (navigate carousel, dismiss)
- Pinch-zoom (chart zoom)

**Avoid These**:
- Requiring long-press for essential functionality
- Preventing default pinch-zoom on charts
- Complex multi-touch gestures

```typescript
// Example: Swipe to dismiss
let startX = 0;

element.addEventListener('touchstart', (e) => {
  startX = e.touches[0].clientX;
});

element.addEventListener('touchend', (e) => {
  const endX = e.changedTouches[0].clientX;
  const diff = startX - endX;

  if (diff > 50) {
    // Swiped left, dismiss
    element.classList.add('dismiss-animation');
  }
});
```

---

## Usability Best Practices

### Clear Language

**Avoid Financial Jargon** (for beginner investors):

| Complex | Simple |
|---------|--------|
| P/E ratio | Price compared to earnings |
| Dividend yield | Annual payment as % of price |
| Moving average | Average price over time |
| MACD | Momentum indicator |
| Bid-ask spread | Difference between buy and sell price |
| Volatility | Price changes frequency |
| Drawdown | Largest price drop |

**Always Provide Tooltips**:
```html
<label for="pe-ratio">
  P/E Ratio
  <button aria-label="Learn more about P/E Ratio" class="tooltip-trigger">
    ?
  </button>
  <div class="tooltip" hidden>
    P/E Ratio shows the price compared to yearly earnings.
    Lower is cheaper, higher is more expensive.
  </div>
</label>
```

### Error Prevention & Recovery

**Confirmation for Critical Actions**:
```
[BUY AAPL] → Modal: "Buy 100 shares at $172.50?"
             [Confirm] [Cancel]
```

**Clear Error Messages**:

```
❌ Bad:   "Invalid value"
✓ Good:  "Quantity must be between 1 and 10,000 shares"

❌ Bad:   "Error occurred"
✓ Good:  "Order failed: Market is currently closed. Try again after 9:30 AM ET"

❌ Bad:   "Invalid input"
✓ Good:  "Target price must be higher than current price ($172.50)"
```

**Error Prevention**:
```html
<!-- Use input constraints -->
<input
  type="number"
  min="1"
  max="10000"
  step="1"
  placeholder="1-10,000 shares"
/>

<!-- Show validation inline -->
<input
  type="email"
  aria-describedby="email-help"
/>
<small id="email-help">
  Example: investor@example.com
</small>

<!-- Disabled button until ready -->
<button disabled={!form.isValid}>
  Place Order
</button>
```

### Feedback & Confirmation

**For Every Action**:

1. **Visual feedback** (immediate):
   - Button changes color/appearance
   - Spinner appears
   - Content updates

2. **Status message** (concurrent):
   - "Placing order..." (aria-live region)
   - "Order submitted" (announcement)

3. **Confirmation** (completion):
   - Success toast notification
   - Updated portfolio display
   - Order confirmation page

Example:
```typescript
const handleBuyClick = async () => {
  // 1. Visual: button shows loading state
  setIsLoading(true);

  // 2. Status: Live region announces action
  announceStatus("Placing order for 100 shares of AAPL...");

  try {
    const order = await api.placeOrder({
      symbol: 'AAPL',
      quantity: 100,
      side: 'buy'
    });

    // 3. Confirmation: Success notification
    showNotification('success', 'Order placed! Order #12345');
    updatePortfolio(order);

  } catch (error) {
    showNotification('error', error.message);
  } finally {
    setIsLoading(false);
  }
};
```

### Accessibility-Friendly Forms

**Full Example**:
```html
<form>
  <fieldset>
    <legend>Buy Stocks</legend>

    <!-- Stock selection -->
    <div class="form-group">
      <label for="symbol">Stock Symbol</label>
      <input
        id="symbol"
        type="text"
        placeholder="e.g., AAPL"
        aria-describedby="symbol-help"
        required
      />
      <small id="symbol-help">
        Enter the stock ticker, e.g., AAPL for Apple
      </small>
    </div>

    <!-- Quantity -->
    <div class="form-group">
      <label for="quantity">Quantity</label>
      <input
        id="quantity"
        type="number"
        min="1"
        max="10000"
        value="1"
        aria-describedby="quantity-help"
        required
      />
      <small id="quantity-help">
        How many shares? (1-10,000)
      </small>
    </div>

    <!-- Order type -->
    <div class="form-group">
      <fieldset>
        <legend>Order Type</legend>
        <label>
          <input type="radio" name="order-type" value="market" checked />
          Market Order (sell immediately at current price)
        </label>
        <label>
          <input type="radio" name="order-type" value="limit" />
          Limit Order (specify your price)
        </label>
      </fieldset>
    </div>

    <!-- Conditional field -->
    <div class="form-group" id="limit-price-group" hidden>
      <label for="limit-price">Limit Price</label>
      <input
        id="limit-price"
        type="number"
        step="0.01"
        placeholder="$0.00"
        aria-describedby="limit-help"
      />
      <small id="limit-help">
        Maximum price you're willing to pay per share
      </small>
    </div>

    <!-- Summary -->
    <div role="region" aria-live="polite" aria-label="Order summary">
      <p>Estimated cost: <strong>$17,250.00</strong></p>
      <p>Available: <strong>$50,000.00</strong></p>
    </div>

    <!-- Actions -->
    <div class="form-actions">
      <button type="submit" class="primary">
        Place Order
      </button>
      <button type="button" class="secondary" onclick="resetForm()">
        Cancel
      </button>
    </div>
  </fieldset>
</form>
```

---

## Testing & Validation

### Automated Tools

**Browser DevTools**:
- Chrome: DevTools > Lighthouse (Accessibility audit)
- Firefox: Inspector > Accessibility tab
- Safari: Develop > Accessibility Inspector

**Browser Extensions**:
- axe DevTools (comprehensive accessibility audit)
- WebAIM Wave (visual accessibility feedback)
- Color Contrast Analyzer (contrast checking)
- Accessibility Insights (Microsoft)

**NPM Packages**:
```bash
npm install --save-dev jest-axe
npm install --save-dev @testing-library/jest-dom
```

### Manual Testing

**Keyboard Navigation**:
1. Unplug mouse
2. Tab through entire page
3. Verify:
   - Tab order is logical
   - Focus is always visible
   - No keyboard traps
   - All functionality accessible

**Screen Reader Testing**:

**Windows**:
- NVDA (free, open-source)
- JAWS (paid, professional)

**Mac/iOS**:
- VoiceOver (built-in)

**Testing Steps**:
1. Enable screen reader
2. Navigate entire page
3. Verify:
   - All content is announced
   - Headings are identified
   - Form labels are associated
   - Buttons are identified
   - Interactive elements work

**Color Blindness Testing**:
1. Use Coblis simulator
2. Test all color-critical information
3. Verify non-color differentiators work

### Accessibility Test Cases

**Chart Accessibility**:
- [ ] Chart has text alternative (data table or description)
- [ ] Chart navigable with keyboard
- [ ] Contrast meets AA standard
- [ ] Color + pattern/texture (not color alone)
- [ ] Focus indicators visible

**Form Accessibility**:
- [ ] All fields have labels
- [ ] Labels associated with inputs (via `for` attribute)
- [ ] Required fields marked with `*`
- [ ] Error messages linked to fields
- [ ] Placeholder text is NOT a substitute for label
- [ ] Form can be submitted with keyboard

**Modal Accessibility**:
- [ ] Focus trap (can't tab out)
- [ ] Escape key closes modal
- [ ] Focus returns to trigger button
- [ ] Heading present
- [ ] Buttons have clear purpose

**Data Table Accessibility**:
- [ ] Header row uses `<th>` with `scope="col"`
- [ ] Row headers use `<th scope="row">`
- [ ] Table has caption or aria-label
- [ ] Sortable columns announced

---

## Common Patterns & Solutions

### Real-Time Price Updates (Accessible)

**Problem**: Price updates happen frequently; need to announce to screen readers

**Solution**: Use `aria-live` region with rate limiting

```tsx
const PriceDisplay = ({ symbol, price, change }) => {
  const prevPrice = useRef(price);
  const [announcement, setAnnouncement] = useState('');

  useEffect(() => {
    if (price !== prevPrice.current) {
      // Announce change every 5 seconds max (not on every tick)
      setAnnouncement(
        `${symbol} updated to $${price},
         ${change > 0 ? 'up' : 'down'} ${Math.abs(change)}%`
      );
      prevPrice.current = price;

      // Clear after announcement
      const timer = setTimeout(() => setAnnouncement(''), 1000);
      return () => clearTimeout(timer);
    }
  }, [price, change, symbol]);

  return (
    <div>
      <div aria-live="polite" aria-atomic="true">
        {announcement}
      </div>
      <div className={change > 0 ? 'text-green-600' : 'text-red-600'}>
        <span>{symbol}</span>
        <span className="text-3xl">${price}</span>
        <span className="text-lg">
          {change > 0 ? '↑' : '↓'} {Math.abs(change)}%
        </span>
      </div>
    </div>
  );
};
```

### Collapsible Sections (Accessible)

```tsx
const Collapsible = ({ title, children }) => {
  const [isOpen, setIsOpen] = useState(false);
  const contentRef = useRef(null);

  return (
    <div>
      <button
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-controls="collapsible-content"
        className="w-full text-left font-semibold"
      >
        {title}
        <Icon name={isOpen ? 'chevron-up' : 'chevron-down'} />
      </button>
      <div
        id="collapsible-content"
        hidden={!isOpen}
        ref={contentRef}
      >
        {children}
      </div>
    </div>
  );
};
```

### Custom Dropdowns (Accessible)

See [Keyboard Navigation](#keyboard-navigation) section for full example.

### Charts with Data Tables (Accessible)

```html
<figure>
  <figcaption>AAPL Stock Price (Last 5 Days)</figcaption>

  <!-- Visual chart -->
  <svg aria-hidden="true" role="presentation">
    <!-- Chart SVG code -->
  </svg>

  <!-- Data table alternative -->
  <table>
    <caption>AAPL daily closing prices</caption>
    <thead>
      <tr>
        <th scope="col">Date</th>
        <th scope="col">Close</th>
        <th scope="col">Change</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Monday</td>
        <td>$170.00</td>
        <td>−$2.00</td>
      </tr>
      <!-- More rows -->
    </tbody>
  </table>
</figure>
```

---

## Accessibility Checklist

### Before Launch

#### Visual Design
- [ ] Color contrast tested (minimum 4.5:1 text, 3:1 UI)
- [ ] Color-blind friendly (icons/text + color)
- [ ] No flashing/flicker (< 3 per second)
- [ ] Font size minimum 14px (12px for labels OK)
- [ ] Line spacing minimum 1.5
- [ ] Text justification avoided (alignment: left)

#### Structure
- [ ] Semantic HTML used throughout
- [ ] Single `<h1>` per page
- [ ] Heading hierarchy not skipped
- [ ] Lists use proper `<ul>`, `<ol>`, `<li>`
- [ ] Tables use `<thead>`, `<tbody>`, `<th>`, `<td>`
- [ ] Landmarks used: `<header>`, `<main>`, `<footer>`

#### Navigation
- [ ] Tab order is logical
- [ ] Focus always visible (2px outline or equivalent)
- [ ] No keyboard traps
- [ ] Escape closes modals/dropdowns
- [ ] Enter/Space activates buttons
- [ ] Arrow keys navigate lists

#### Forms
- [ ] All inputs have labels
- [ ] Labels associated with `for` attribute
- [ ] Required fields marked
- [ ] Error messages associated with fields
- [ ] Form validation clear and helpful
- [ ] Placeholder text not substitute for label

#### Content
- [ ] Images have alt text
- [ ] Meaningful text (not "click here")
- [ ] Plain language (no jargon without explanation)
- [ ] Tooltips for complex terms
- [ ] Abbreviations explained first use
- [ ] Links obvious (not via color alone)

#### Functionality
- [ ] All features keyboard accessible
- [ ] Real-time updates announced (aria-live)
- [ ] Status changes announced
- [ ] Errors clearly described
- [ ] Confirmation for critical actions
- [ ] Feedback for all interactions

#### Responsiveness
- [ ] Mobile touch targets 44px+ minimum
- [ ] Zoom works up to 200%
- [ ] Content doesn't require horizontal scroll
- [ ] Text readable without magnification
- [ ] Touch spacing 8px minimum

#### Mobile
- [ ] Font size 16px+ (prevents zoom)
- [ ] Appropriate input types (email, number, tel)
- [ ] Gesture support tested
- [ ] No long-press required for essential functions
- [ ] Orientation support (portrait/landscape)

#### Screen Readers
- [ ] ARIA labels on icon-only elements
- [ ] ARIA descriptions on complex elements
- [ ] Live regions for updates
- [ ] Role attributes correct
- [ ] Form validation announced
- [ ] Page structure clear

#### Testing
- [ ] Axe DevTools: No critical issues
- [ ] Lighthouse: Accessibility 90+
- [ ] Keyboard navigation complete
- [ ] NVDA/JAWS tested
- [ ] Color blindness simulator tested
- [ ] Contrast checker passed
- [ ] Real users tested (especially with disabilities)

---

## Resources & References

### Standards
- [WCAG 2.1 Specification](https://www.w3.org/WAI/WCAG21/quickref/)
- [Web Content Accessibility Guidelines](https://www.w3.org/WAI/standards-guidelines/wcag/)
- [ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/)

### Tools
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [axe DevTools](https://www.deque.com/axe/devtools/)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [NVDA Screen Reader](https://www.nvaccess.org/)
- [Color Contrast Analyzer](https://www.tpgi.com/color-contrast-checker/)
- [Coblis Color Blindness Simulator](https://www.color-blindness.com/coblis-color-blindness-simulator/)

### Learning
- [WebAIM Resources](https://webaim.org/resources/)
- [A11y Project](https://www.a11yproject.com/)
- [Inclusive Components](https://inclusive-components.design/)
- [The Accessibility Tree](https://www.w3.org/WAI/fundamentals/accessibility-principles/)

---

## Summary

This comprehensive accessibility guide ensures:

1. **Perceivable**: All content visible/audible to all users
2. **Operable**: Full keyboard navigation, touch-friendly
3. **Understandable**: Clear language, predictable patterns
4. **Robust**: Compatible with assistive technologies

By following these guidelines, the stock exchange board becomes usable for:
- Retail investors of all abilities
- Users with visual impairments
- Users with motor impairments
- Users with cognitive disabilities
- International users (with future i18n support)

---

**Document Version**: 1.0
**Last Updated**: March 11, 2026
**Status**: Implementation Ready
