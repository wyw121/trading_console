---
description: "Frontend Vue.js component development guidelines"
applyTo: "frontend/src/**/*.{vue,js}"
---

# Frontend Vue.js Development Instructions

## Vue.js 3 Component Development
- Use Vue 3 Composition API with `<script setup>` syntax
- Use Element Plus components following their design system
- Implement proper prop validation with TypeScript-style definitions
- Use computed properties for derived data
- Implement proper event handling with emit()
- Use ref() for reactive primitive values and reactive() for objects

## State Management with Pinia
- Create stores for different data domains (auth, exchanges, strategies)
- Use actions for async operations
- Implement proper error handling in store actions
- Use getters for computed state values
- Persist sensitive data securely (not in localStorage for API keys)

## API Integration
- Use axios for HTTP requests with proper error handling
- Implement request/response interceptors for authentication
- Handle loading states and error messages
- Implement proper timeout handling
- Use environment variables for API base URLs

## UI/UX Best Practices
- Follow Element Plus design system
- Implement responsive design patterns
- Use proper loading indicators during async operations
- Provide user feedback for all actions
- Implement form validation with clear error messages
- Use consistent spacing and typography

## Component Structure
- Keep components focused and single-purpose
- Use composition API for better logic reuse
- Implement proper lifecycle hooks (onMounted, onUnmounted)
- Use props for parent-child communication
- Emit events for child-parent communication
- Use provide/inject for deep component communication when needed

## Performance Optimization
- Use lazy loading for routes and large components
- Implement proper key attributes for v-for loops
- Use computed properties instead of methods for expensive operations
- Optimize bundle size with proper imports
- Use v-show vs v-if appropriately
