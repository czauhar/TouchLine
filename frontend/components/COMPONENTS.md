# TouchLine Component Library

A comprehensive, type-safe component library built with React, TypeScript, and Tailwind CSS.

## Design Philosophy

- **Consistent**: All components follow the same patterns and conventions
- **Accessible**: Built with accessibility in mind
- **Type-Safe**: Full TypeScript support with proper interfaces
- **Flexible**: Customizable through props and className overrides
- **Performant**: Optimized for speed and minimal re-renders

## UI Components (`/components/ui/`)

### Card
A flexible container component with multiple variants.

```tsx
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/Card'

<Card variant="glass" hover>
  <CardHeader>
    <CardTitle>Title</CardTitle>
    <CardDescription>Description</CardDescription>
  </CardHeader>
  <CardContent>Content here</CardContent>
  <CardFooter>Footer actions</CardFooter>
</Card>
```

**Variants**: `default`, `glass`, `bordered`
**Props**: `hover` (boolean) - adds hover effects

### Button
Standardized button component with loading states.

```tsx
import { Button } from '@/components/ui/Button'

<Button variant="primary" size="md" isLoading={false}>
  Click Me
</Button>
```

**Variants**: `primary`, `secondary`, `success`, `danger`, `ghost`, `outline`
**Sizes**: `sm`, `md`, `lg`

### Badge
Status and label badges with semantic colors.

```tsx
import { Badge, StatusBadge } from '@/components/ui/Badge'

<Badge variant="success">Active</Badge>
<StatusBadge status="live" />
```

**Variants**: `default`, `success`, `warning`, `danger`, `info`, `primary`

### LoadingSpinner
Loading indicators and skeleton loaders.

```tsx
import { LoadingSpinner, FullPageLoading, Skeleton } from '@/components/ui/LoadingSpinner'

<LoadingSpinner size="md" text="Loading..." />
<FullPageLoading text="Loading application..." />
<Skeleton variant="rectangular" className="h-24" />
```

### EmptyState
Display when no data is available.

```tsx
import { EmptyState } from '@/components/ui/EmptyState'
import { Inbox } from 'lucide-react'

<EmptyState
  icon={<Inbox className="w-16 h-16" />}
  title="No items found"
  description="Try creating your first item"
  action={{
    label: "Create Item",
    onClick: () => handleCreate()
  }}
/>
```

### StatCard
Dashboard statistics card with trend indicators.

```tsx
import { StatCard } from '@/components/ui/StatCard'
import { Activity } from 'lucide-react'

<StatCard
  title="Active Users"
  value={1234}
  icon={<Activity className="w-6 h-6" />}
  color="blue"
  change={{ value: 12, period: 'vs last month' }}
/>
```

**Colors**: `blue`, `green`, `yellow`, `red`, `purple`, `default`

### Modal
Dialog modals with backdrop and animations.

```tsx
import { Modal, ConfirmModal } from '@/components/ui/Modal'

<Modal isOpen={isOpen} onClose={onClose} title="Modal Title" size="md">
  <p>Modal content</p>
</Modal>

<ConfirmModal
  isOpen={isOpen}
  onClose={onClose}
  onConfirm={handleConfirm}
  title="Confirm Action"
  description="Are you sure?"
  variant="danger"
/>
```

**Sizes**: `sm`, `md`, `lg`, `xl`

### Input & TextArea
Form input components with validation.

```tsx
import { Input, TextArea } from '@/components/ui/Input'
import { Mail } from 'lucide-react'

<Input
  label="Email"
  type="email"
  placeholder="you@example.com"
  error={errors.email}
  helperText="We'll never share your email"
  leftIcon={<Mail className="w-5 h-5" />}
  required
/>

<TextArea
  label="Description"
  rows={4}
  error={errors.description}
/>
```

### Select
Dropdown select component.

```tsx
import { Select } from '@/components/ui/Select'

<Select
  label="Country"
  options={[
    { value: 'us', label: 'United States' },
    { value: 'uk', label: 'United Kingdom' }
  ]}
  error={errors.country}
/>
```

## Feature Components

### Matches (`/components/matches/`)

#### MatchCard
Display individual match information.

```tsx
import { MatchCard } from '@/components/matches/MatchCard'

<MatchCard
  match={matchData}
  onClick={() => handleMatchClick(matchData)}
/>
```

#### MatchList
Grid of match cards with empty state.

```tsx
import { MatchList } from '@/components/matches/MatchList'

<MatchList
  matches={matches}
  onMatchClick={handleMatchClick}
  emptyMessage="No matches available today"
/>
```

#### LiveIndicator
Animated live match indicator.

```tsx
import { LiveIndicator } from '@/components/matches/LiveIndicator'

<LiveIndicator isLive={true} showText={true} />
```

### Alerts (`/components/alerts/`)

#### AlertCard
Display alert with actions.

```tsx
import { AlertCard } from '@/components/alerts/AlertCard'

<AlertCard
  alert={alertData}
  onToggle={handleToggle}
  onDelete={handleDelete}
  onEdit={handleEdit}
/>
```

#### AlertStats
Display alert statistics.

```tsx
import { AlertStats } from '@/components/alerts/AlertStats'

<AlertStats stats={{ total_alerts: 10, active_alerts: 7, inactive_alerts: 3 }} />
```

### Dashboard (`/components/dashboard/`)

#### QuickActions
Quick action cards with gradients.

```tsx
import { QuickActions } from '@/components/dashboard/QuickActions'
import { Plus } from 'lucide-react'

<QuickActions
  actions={[
    {
      title: "Create Alert",
      description: "Set up a new alert",
      icon: <Plus className="w-6 h-6" />,
      href: "/alerts/create",
      color: "from-blue-500 to-blue-600",
      hoverColor: "from-blue-600 to-blue-700"
    }
  ]}
/>
```

#### SystemHealth
Display system health metrics.

```tsx
import { SystemHealth, SystemMetrics } from '@/components/dashboard/SystemHealth'
import { Database } from 'lucide-react'

<SystemHealth
  services={[
    {
      name: "Database",
      status: "healthy",
      icon: <Database className="w-5 h-5" />,
      details: "Response time: 12ms"
    }
  ]}
/>

<SystemMetrics
  metrics={{
    cpu_percent: 45.2,
    memory_percent: 62.8,
    disk_percent: 38.1
  }}
/>
```

## Utilities (`/lib/utils.ts`)

```tsx
import { cn, formatDate, formatTime, truncate, capitalize } from '@/lib/utils'

// Merge Tailwind classes
const className = cn('bg-blue-500', 'hover:bg-blue-600', customClass)

// Format dates
formatDate('2024-01-15') // "Jan 15, 2024"
formatTime('2024-01-15T14:30:00') // "02:30 PM"

// String utilities
truncate('Long text here', 20) // "Long text here..."
capitalize('hello') // "Hello"
```

## Best Practices

### 1. Always Import from Component Library
```tsx
// ✅ Good
import { Button, Card } from '@/components/ui'

// ❌ Bad - Don't create inline buttons
<button className="bg-blue-500...">Click</button>
```

### 2. Use Semantic Variants
```tsx
// ✅ Good
<Button variant="danger">Delete</Button>
<Badge variant="success">Active</Badge>

// ❌ Bad
<Button className="bg-red-600">Delete</Button>
```

### 3. Proper Error Handling
```tsx
// ✅ Good
<Input
  label="Email"
  error={errors.email}
  helperText="Enter your email address"
/>

// ❌ Bad
{errors.email && <p className="text-red-500">{errors.email}</p>}
```

### 4. Loading States
```tsx
// ✅ Good
{loading ? <LoadingSpinner /> : <Content />}

// ❌ Bad
{loading && <div>Loading...</div>}
```

### 5. Empty States
```tsx
// ✅ Good
{data.length === 0 ? (
  <EmptyState title="No data" description="..." />
) : (
  <List data={data} />
)}

// ❌ Bad
{data.length === 0 && <p>No data</p>}
```

## Customization

All components accept a `className` prop for customization:

```tsx
<Card className="bg-gradient-to-r from-purple-500 to-pink-500">
  Custom styled card
</Card>

<Button className="w-full" variant="primary">
  Full width button
</Button>
```

The `cn()` utility intelligently merges Tailwind classes, allowing overrides.

## Accessibility

All components are built with accessibility in mind:
- Proper ARIA labels
- Keyboard navigation support
- Focus management
- Screen reader support
- Semantic HTML

## Performance

Components are optimized for performance:
- Proper use of React.memo where needed
- Efficient re-render prevention
- Lazy loading support
- Optimized bundle size

