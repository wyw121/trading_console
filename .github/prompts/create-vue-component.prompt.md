---
description: "Create a new Vue.js component with Element Plus integration"
mode: "agent"
tools: ["filesystem"]
---

# Create Vue.js Component

Create a new Vue.js component with Element Plus integration and proper state management.

## Component Specifications
- **Component Name**: ${input:name:Component name in PascalCase (e.g., UserProfile)}
- **Purpose**: ${input:purpose:Brief description of the component's purpose}
- **Parent Route**: ${input:route:Parent route path if this is a page component}

## Implementation Requirements

### 1. Component Structure
- Use Vue 3 Composition API with `<script setup>` syntax
- Implement proper template structure with Element Plus components
- Use scoped styles for component-specific styling
- Include proper TypeScript-style prop definitions

### 2. Props and Events
- Define props with proper validation and default values
- Implement event emitting for parent component communication
- Use descriptive event names following Vue.js conventions
- Add JSDoc comments for prop documentation

### 3. State Management
- Use Pinia store if the component needs global state
- Implement local reactive state with ref() and reactive()
- Use computed properties for derived data
- Handle loading and error states appropriately

### 4. API Integration
- Use the centralized API utilities from `src/utils/api.js`
- Implement proper error handling for API calls
- Show loading indicators during async operations
- Handle network errors and timeouts gracefully

### 5. UI/UX Implementation
- Follow Element Plus design system guidelines
- Implement responsive design patterns
- Use proper form validation with clear error messages
- Provide user feedback for all interactive elements
- Implement proper accessibility attributes

### 6. Lifecycle Management
- Use appropriate lifecycle hooks (onMounted, onUnmounted)
- Clean up subscriptions and event listeners
- Handle component destruction gracefully
- Implement proper data fetching patterns

## File Structure
Please create or update the following files:
- `frontend/src/components/${input:name}.vue` or `frontend/src/views/${input:name}.vue`
- `frontend/src/router/index.js` - Add route if it's a page component
- `frontend/src/stores/{store_name}.js` - Update store if needed

## Element Plus Components to Consider
- Forms: el-form, el-form-item, el-input, el-select, el-button
- Data Display: el-table, el-card, el-descriptions, el-tag
- Navigation: el-menu, el-breadcrumb, el-pagination
- Feedback: el-message, el-notification, el-loading, el-dialog

## Testing Considerations
- Ensure proper prop validation
- Test event emission and handling
- Verify API error handling
- Test responsive design on different screen sizes
- Validate form inputs and error messages

Please implement the component following Vue.js 3 best practices and the project's existing patterns.
