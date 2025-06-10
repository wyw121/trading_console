# Vue.js Component Development

Your goal is to create a new Vue.js component for the trading console frontend.

## Requirements

Ask for component details if not provided:
- Component purpose and functionality
- Props and data requirements
- User interactions and events
- Integration with existing components
- State management needs

## Implementation Guidelines

### Vue 3 Composition API Structure
- Use `<script setup>` syntax for modern Vue.js development
- Implement reactive data with `ref()` and `reactive()`
- Use `computed()` for derived state
- Implement `watch()` for side effects
- Use lifecycle hooks appropriately (`onMounted`, `onUnmounted`)

### Element Plus Integration
- Use Element Plus components following design system
- Implement proper form validation with `el-form`
- Use consistent spacing and layout patterns
- Follow Element Plus theming and styling
- Implement responsive design with Element Plus grid

### State Management
- Use Pinia stores for shared state
- Implement proper action dispatching
- Handle loading and error states
- Cache data appropriately
- Sync with backend APIs

### Component Structure
```vue
<template>
  <div class="component-wrapper">
    <el-card class="component-card">
      <template #header>
        <span>{{ title }}</span>
      </template>
      
      <!-- Component content -->
      
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

// Props definition
const props = defineProps({
  title: {
    type: String,
    required: true
  }
})

// Emits definition
const emit = defineEmits(['update', 'error'])

// Reactive data
const loading = ref(false)
const data = ref([])

// Computed properties
const processedData = computed(() => {
  // Process data here
})

// Methods
const handleAction = async () => {
  try {
    loading.value = true
    // API call or action
    ElMessage.success('Action completed successfully')
    emit('update', result)
  } catch (error) {
    ElMessage.error(error.message)
    emit('error', error)
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(() => {
  // Initialize component
})
</script>

<style scoped>
.component-wrapper {
  padding: 20px;
}

.component-card {
  /* Component styles */
}
</style>
```

## Best Practices
- [ ] Use TypeScript-style prop definitions
- [ ] Implement proper error handling with user feedback
- [ ] Add loading states for async operations
- [ ] Use Element Plus design tokens for styling
- [ ] Implement accessibility features (ARIA labels, keyboard navigation)
- [ ] Add proper validation for user inputs
- [ ] Use consistent naming conventions
- [ ] Implement responsive design

## API Integration
- Use composables for reusable API logic
- Handle authentication and authorization
- Implement proper error handling and retry logic
- Cache API responses when appropriate
- Show loading indicators during API calls

## Testing Considerations
- Write unit tests for component logic
- Test user interactions and events
- Test error scenarios and edge cases
- Verify accessibility compliance
- Test responsive design on different screen sizes

## Performance Optimization
- Use `v-memo` for expensive list rendering
- Implement lazy loading for heavy components
- Use `defineAsyncComponent` for code splitting
- Optimize bundle size with proper imports
- Implement virtual scrolling for large datasets
