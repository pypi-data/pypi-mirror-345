"""
Patterns for detecting SSR compatibility issues in Laravel Inertia Vue applications
"""

SSR_ISSUE_PATTERNS = [
    # Browser-specific APIs in global scope
    {
        'type': 'Browser API',
        'pattern': r'(?<!typeof\s+)\b(window|document|navigator|localStorage|sessionStorage)\b(?!\s+!==)(?!\s+===)(?!\s+==)(?!\s+!=)',
        'simple_terms': ['window.', 'document.', 'navigator.', 'localStorage.', 'sessionStorage.'],
        'file_extensions': ['.js', '.jsx', '.ts', '.tsx', '.vue'],
        'message': 'Accessing browser-specific API directly can cause SSR errors since these APIs do not exist on the server',
        'solution': 'Wrap browser API calls in onMounted() or check if window is defined: if (typeof window !== "undefined") { ... }'
    },
    
    # Browser object properties
    {
        'type': 'Browser Object Property',
        'pattern': r'\b(window\.location|window\.history|window\.performance|document\.cookie|document\.referrer|navigator\.userAgent)\b',
        'file_extensions': ['.js', '.jsx', '.ts', '.tsx', '.vue'],
        'message': 'Using browser object properties directly can cause SSR errors',
        'solution': 'Use conditional checks before accessing these properties: if (typeof window !== "undefined") { window.location... }'
    },
    
    # Direct DOM manipulation
    {
        'type': 'DOM Manipulation',
        'pattern': r'\bdocument\.(getElementById|querySelector|querySelectorAll|getElementsBy(TagName|ClassName|Name))\b',
        'file_extensions': ['.js', '.jsx', '.ts', '.tsx', '.vue'],
        'message': 'Direct DOM manipulation is not available during SSR since there is no DOM on the server',
        'solution': 'Use refs instead and access them in onMounted() or nextTick(). For example: const el = ref(null); onMounted(() => { el.value.focus() })'
    },
    
    # Client-side only libraries
    {
        'type': 'Client Library',
        'pattern': r'import\s+.+\s+from\s+[\'"](?!vue|@vue|@inertiajs|@vueuse)(jquery|\$|chart\.js|leaflet|three\.js|mapbox-gl|moment|axios)[\'"]',
        'file_extensions': ['.js', '.jsx', '.ts', '.tsx', '.vue'],
        'message': 'Importing client-side only libraries in the global scope can cause SSR errors',
        'solution': 'Use dynamic import() or import the library in onMounted() hook: onMounted(async () => { const { default: Library } = await import("library") })'
    },
    
    # Specific problematic client libraries
    {
        'type': 'jQuery Library',
        'pattern': r'(?<!\w)(\$\(|jQuery\()',
        'file_extensions': ['.js', '.jsx', '.ts', '.tsx', '.vue'],
        'message': 'Using jQuery can cause SSR issues as it relies on the DOM which is not available during server rendering',
        'solution': 'Avoid jQuery in favor of native DOM APIs wrapped in onMounted(), or use a Vue-compatible library like VueUse'
    },
    
    # Lifecycle hooks in wrong place (Vue 2 style)
    {
        'type': 'Lifecycle Hook',
        'pattern': r'(?:export default|Vue\.component|\{\s*)\s*(?:\{|\(\s*\{\s*)(?:[^}]*,)?\s*(created|mounted|beforeMount)\s*:\s*function',
        'file_extensions': ['.vue', '.js', '.jsx', '.ts', '.tsx'],
        'message': 'Vue 2 lifecycle hooks are not compatible with Vue 3 Composition API which is recommended for SSR',
        'solution': 'Replace with Composition API setup() and lifecycle hooks like onMounted(), onBeforeMount(), etc.'
    },
    
    # Vue 3 lifecycle hooks outside of setup
    {
        'type': 'Lifecycle Hook Scope',
        'pattern': r'(?<!function setup.*\{\s*.*)\b(?<!function.*\{\s*.*)\b(onMounted|onBeforeMount|onUnmounted)\s*\(',
        'simple_terms': ['onMounted(', 'onBeforeMount(', 'onUnmounted('],
        'file_extensions': ['.vue', '.js', '.jsx', '.ts', '.tsx'],
        'message': 'Vue 3 Composition API lifecycle hooks must be called inside setup() or a component function',
        'solution': 'Move the lifecycle hook into the setup() function or ensure it is called during component initialization'
    },
    
    # Incorrect Inertia imports
    {
        'type': 'Inertia Import',
        'pattern': r'import\s+\{\s*(Inertia|InertiaApp)\s*\}\s+from',
        'file_extensions': ['.js', '.jsx', '.ts', '.tsx', '.vue'],
        'message': 'Using incorrect Inertia import pattern which is not compatible with SSR',
        'solution': 'Use createInertiaApp() pattern from @inertiajs/vue3 for SSR compatibility'
    },
    
    # Incorrect Vue usage (Vue 2 style)
    {
        'type': 'Vue Instance',
        'pattern': r'new\s+Vue\s*\(',
        'file_extensions': ['.js', '.jsx', '.ts', '.tsx', '.vue'],
        'message': 'Using Vue 2 instance directly is not compatible with Vue 3 SSR',
        'solution': 'Use createApp() for Vue 3 SSR compatibility: import { createApp } from "vue"; const app = createApp(App);'
    },
    
    # Vue instance mounting (potentially problematic)
    {
        'type': 'Vue Mount',
        'pattern': r'\.\$mount\(|app\.mount\([\'"]#',
        'file_extensions': ['.js', '.jsx', '.ts', '.tsx', '.vue'],
        'message': 'Direct mounting to DOM elements can cause SSR hydration issues',
        'solution': 'For Inertia, use createInertiaApp() pattern and let it handle mounting for both SSR and client'
    },
    
    # Direct event listeners attachment
    {
        'type': 'Event Listener',
        'pattern': r'(?<!onMounted\([^)]*\)\s*{\s*.*)\.(addEventListener|removeEventListener)\(',
        'simple_terms': ['.addEventListener(', '.removeEventListener('],
        'file_extensions': ['.js', '.jsx', '.ts', '.tsx', '.vue'],
        'message': 'Direct event listener attachment is not available during SSR',
        'solution': 'Use v-on directives in templates or add event listeners in onMounted() hook and remove them in onUnmounted()'
    },
    
    # Meta tag manipulation
    {
        'type': 'Meta Tags',
        'pattern': r'document\.head\.appendChild|document\.head\.insertBefore|document\.title\s*=',
        'file_extensions': ['.js', '.jsx', '.ts', '.tsx', '.vue'],
        'message': 'Direct meta tag manipulation is not available during SSR',
        'solution': 'Use @vueuse/head or inertia-vue3 Head component for meta management'
    },
    
    # Timer functions without cleanup or conditional
    {
        'type': 'Timers',
        'pattern': r'(?<!onMounted\([^)]*\)\s*{\s*.*)(?<!if\s*\(\s*typeof\s+window\s*!==\s*[\'"]undefined[\'"]\s*\)\s*{\s*.*)(setTimeout|setInterval)\(',
        'simple_terms': ['setTimeout(', 'setInterval('],
        'file_extensions': ['.js', '.jsx', '.ts', '.tsx', '.vue'],
        'message': 'Using timers without proper lifecycle handling can cause memory leaks in SSR',
        'solution': 'Set timers in onMounted() and clear them in onUnmounted(). Example: onMounted(() => { const timer = setInterval(() => {}, 1000); onUnmounted(() => { clearInterval(timer); }); });'
    },
    
    # Inline scripts in PHP/Blade templates
    {
        'type': 'Inline Script',
        'pattern': r'<script>\s*(?!window\.__INERTIA)',
        'file_extensions': ['.php', '.blade.php', '.html'],
        'message': 'Inline scripts can cause hydration mismatches in SSR',
        'solution': 'Move scripts to Vue components or use @vite directive for proper bundling. For global variables, use window.__INERTIA_SSR = {data} pattern'
    },
    
    # Third-party script tags 
    {
        'type': 'Third-Party Script',
        'pattern': r'<script\s+src=(?!.*\bvite\b)',
        'file_extensions': ['.php', '.blade.php', '.html'],
        'message': 'External script tags can cause hydration mismatches in SSR',
        'solution': 'Load third-party scripts with useHead() or in onMounted(), or use @vite directive with proper module bundling'
    },
    
    # Missing or incorrect key on list items
    {
        'type': 'List Keys',
        'pattern': r'<\w+[^>]*v-for\s*=\s*[\'"][^\'"]+(in|of)[^\'"]+[\'"][^>]*?>',
        'simple_terms': ['v-for='],
        'file_extensions': ['.vue'],
        'message': 'Missing key attribute on v-for can cause hydration errors in SSR',
        'solution': 'Add a unique :key attribute to each v-for item: <div v-for="item in items" :key="item.id">',
        'negative_pattern': r':key\s*=|v-bind:key\s*='
    },
    
    # Direct access to Inertia props 
    {
        'type': 'Inertia Props',
        'pattern': r'\$page\.props|\$inertia\.props',
        'file_extensions': ['.vue'],
        'message': 'Direct access to $page.props can cause issues in SSR mode with Vue 3',
        'solution': 'Use the usePage() composable from @inertiajs/vue3: const { props } = usePage()'
    },
    
    # Using component: option instead of components:
    {
        'type': 'Component Registration',
        'pattern': r'(?:export default|Vue\.component|\{\s*)\s*(?:\{|\(\s*\{\s*)(?:[^}]*,)?\s*component\s*:\s*\{',
        'file_extensions': ['.vue', '.js', '.ts'],
        'message': 'Using "component:" instead of "components:" can cause SSR registration issues',
        'solution': 'Use components: { ComponentName } for component registration'
    },
    
    # Incorrect import paths with case sensitivity issues
    {
        'type': 'Import Path',
        'pattern': r'import\s+[\w{},\s*]+\s+from\s+[\'"](?!@|\.|~)(\.\/|\.\.\/)[^\'"]+[\'"]',
        'file_extensions': ['.js', '.jsx', '.ts', '.tsx', '.vue'],
        'message': 'Import paths with incorrect format or case sensitivity can cause SSR build failures',
        'solution': 'Ensure import paths match exact case of file system paths and use proper alias formats'
    },
    
    # Dynamic component loading without handling
    {
        'type': 'Dynamic Component',
        'pattern': r'<component\s+:is=',
        'file_extensions': ['.vue'],
        'message': 'Dynamic components without proper imports can cause SSR issues',
        'solution': 'Pre-import all potential components or use defineAsyncComponent with proper error handling for dynamic loading'
    },
    
    # Direct DOM access with refs outside lifecycle hooks
    {
        'type': 'Ref DOM Access',
        'pattern': r'(?<!onMounted\([^)]*\)\s*{\s*.*)(?<!nextTick\([^)]*\)\s*{\s*.*)(?<!if\s*\(\s*typeof\s+window\s*!==\s*[\'"]undefined[\'"]\s*\)\s*{\s*.*)\b\w+\.value\.(focus|blur|click|scrollIntoView)',
        'simple_terms': ['.value.focus', '.value.blur', '.value.click', '.value.scrollIntoView'],
        'file_extensions': ['.vue', '.js', '.jsx', '.ts', '.tsx'],
        'message': 'Accessing DOM methods on refs outside of lifecycle hooks is not SSR compatible',
        'solution': 'Access DOM methods on refs inside onMounted() or nextTick(): onMounted(() => { myRef.value.focus() })'
    },
    
    # Inertia form submission without error handling
    {
        'type': 'Inertia Form',
        'pattern': r'(useForm|Inertia\.form)\([^)]*\)\.(post|put|patch|delete)\([^)]*\)(?!\s*\.then|\s*\.catch)',
        'file_extensions': ['.vue', '.js', '.jsx', '.ts', '.tsx'],
        'message': 'Inertia form submissions without error handling can cause issues in SSR',
        'solution': 'Add proper error handling to form submissions: form.post(route).then().catch(error => {})'
    },
    
    # CSS with browser-specific features
    {
        'type': 'CSS Browser Features',
        'pattern': r'@media\s+print|navigator|window\.(?:inner|outer)',
        'file_extensions': ['.css', '.scss', '.sass', '.less', '.vue'],
        'message': 'Using browser-specific CSS features can cause rendering differences in SSR',
        'solution': 'Add class to body in onMounted() and use that for styling browser-specific features'
    },
    
    # Usage of this.$el
    {
        'type': 'Vue Element Access',
        'pattern': r'this\.\$el',
        'file_extensions': ['.vue', '.js', '.jsx', '.ts', '.tsx'],
        'message': 'Accessing this.$el directly can cause issues in SSR since the DOM element might not exist',
        'solution': 'Use refs instead or access this.$el in mounted() or onMounted()'
    },
    
    # Non-SSR compatible Inertia props usage
    {
        'type': 'Inertia Request',
        'pattern': r'Inertia\.visit|Inertia\.replace|Inertia\.reload',
        'file_extensions': ['.vue', '.js', '.jsx', '.ts', '.tsx'],
        'message': 'Direct Inertia navigation methods can cause SSR issues if used outside client lifecycle',
        'solution': 'Use the router() helper for SSR-compatible navigation or wrap in onMounted()'
    },
    
    # Global state without SSR consideration  
    {
        'type': 'Global State',
        'pattern': r'const\s+store\s*=\s*createStore|Vuex\.Store|new\s+Vuex\.Store',
        'file_extensions': ['.js', '.jsx', '.ts', '.tsx', '.vue'],
        'message': 'Global store creation without SSR configuration can cause state hydration issues',
        'solution': 'Ensure stores use factory pattern to prevent cross-request state pollution in SSR: export const createStore = () => new Vuex.Store({...})'
    },
]

# Categories of issues for better reporting
SSR_ISSUE_CATEGORIES = {
    'critical': [
        'Browser API', 
        'DOM Manipulation', 
        'Client Library',
        'jQuery Library',
    ],
    'major': [
        'Lifecycle Hook', 
        'Vue Instance', 
        'Vue Mount',
        'Inertia Import',
        'Event Listener',
        'Dynamic Component',
    ],
    'medium': [
        'Inertia Props',
        'Meta Tags',
        'Timers',
        'List Keys',
        'Component Registration',
        'Ref DOM Access',
    ],
    'minor': [
        'Import Path',
        'CSS Browser Features',
        'Third-Party Script',
        'Inline Script',
    ],
}

# Get severity for an issue type
def get_issue_severity(issue_type: str) -> str:
    """Get the severity level for an issue type"""
    for severity, types in SSR_ISSUE_CATEGORIES.items():
        if issue_type in types:
            return severity
    return 'minor'  # Default severity