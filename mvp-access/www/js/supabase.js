/**
 * FraudShield Uganda - Supabase Authentication
 *
 * This module handles all authentication and user management
 * using Supabase as the backend-as-a-service.
 *
 * Setup Instructions:
 * 1. Create a Supabase project at https://supabase.com
 * 2. Replace SUPABASE_URL and SUPABASE_ANON_KEY below
 * 3. Enable Email auth in Supabase Dashboard > Authentication > Providers
 */

// ============================================
// CONFIGURATION - UPDATE THESE VALUES
// ============================================

// Get these from: Supabase Dashboard > Settings > API
const SUPABASE_URL = 'YOUR_SUPABASE_URL';  // e.g., 'https://abcdefgh.supabase.co'
const SUPABASE_ANON_KEY = 'YOUR_SUPABASE_ANON_KEY';  // e.g., 'eyJhbGciOiJIUzI1NiIs...'

// ============================================
// SUPABASE CLIENT INITIALIZATION
// ============================================

let supabase = null;

/**
 * Initialize Supabase client
 * Must be called before using any auth functions
 */
async function initSupabase() {
    // Check if configuration is set
    if (SUPABASE_URL === 'YOUR_SUPABASE_URL' || SUPABASE_ANON_KEY === 'YOUR_SUPABASE_ANON_KEY') {
        console.warn('⚠️ Supabase not configured. Running in demo mode.');
        return false;
    }

    try {
        // Dynamically import Supabase from CDN
        const { createClient } = await import('https://esm.sh/@supabase/supabase-js@2');
        supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
        console.log('✅ Supabase client initialized');
        return true;
    } catch (error) {
        console.error('❌ Failed to initialize Supabase:', error);
        return false;
    }
}

// ============================================
// AUTHENTICATION FUNCTIONS
// ============================================

/**
 * Sign up a new user with email and password
 * @param {string} email - User's email address
 * @param {string} password - User's password (min 6 characters)
 * @param {object} metadata - Additional user data (organization, phone, etc.)
 * @returns {object} - { user, error }
 */
async function signUp(email, password, metadata = {}) {
    if (!supabase) {
        return { user: null, error: { message: 'Supabase not configured' } };
    }

    try {
        const { data, error } = await supabase.auth.signUp({
            email,
            password,
            options: {
                data: {
                    organization_name: metadata.organization || '',
                    phone: metadata.phone || '',
                    full_name: metadata.fullName || '',
                    role: 'user',
                    created_at: new Date().toISOString()
                }
            }
        });

        if (error) {
            console.error('Sign up error:', error);
            return { user: null, error };
        }

        console.log('✅ User signed up:', data.user?.email);
        return { user: data.user, error: null };
    } catch (err) {
        console.error('Sign up exception:', err);
        return { user: null, error: { message: err.message } };
    }
}

/**
 * Sign in an existing user with email and password
 * @param {string} email - User's email address
 * @param {string} password - User's password
 * @returns {object} - { user, session, error }
 */
async function signIn(email, password) {
    if (!supabase) {
        return { user: null, session: null, error: { message: 'Supabase not configured' } };
    }

    try {
        const { data, error } = await supabase.auth.signInWithPassword({
            email,
            password
        });

        if (error) {
            console.error('Sign in error:', error);
            return { user: null, session: null, error };
        }

        console.log('✅ User signed in:', data.user?.email);
        return { user: data.user, session: data.session, error: null };
    } catch (err) {
        console.error('Sign in exception:', err);
        return { user: null, session: null, error: { message: err.message } };
    }
}

/**
 * Sign out the current user
 * @returns {object} - { error }
 */
async function signOut() {
    if (!supabase) {
        return { error: { message: 'Supabase not configured' } };
    }

    try {
        const { error } = await supabase.auth.signOut();

        if (error) {
            console.error('Sign out error:', error);
            return { error };
        }

        console.log('✅ User signed out');
        return { error: null };
    } catch (err) {
        console.error('Sign out exception:', err);
        return { error: { message: err.message } };
    }
}

/**
 * Get the currently logged in user
 * @returns {object} - { user, error }
 */
async function getCurrentUser() {
    if (!supabase) {
        return { user: null, error: { message: 'Supabase not configured' } };
    }

    try {
        const { data: { user }, error } = await supabase.auth.getUser();

        if (error) {
            return { user: null, error };
        }

        return { user, error: null };
    } catch (err) {
        return { user: null, error: { message: err.message } };
    }
}

/**
 * Get the current session
 * @returns {object} - { session, error }
 */
async function getSession() {
    if (!supabase) {
        return { session: null, error: { message: 'Supabase not configured' } };
    }

    try {
        const { data: { session }, error } = await supabase.auth.getSession();
        return { session, error };
    } catch (err) {
        return { session: null, error: { message: err.message } };
    }
}

/**
 * Send password reset email
 * @param {string} email - User's email address
 * @returns {object} - { error }
 */
async function resetPassword(email) {
    if (!supabase) {
        return { error: { message: 'Supabase not configured' } };
    }

    try {
        const { error } = await supabase.auth.resetPasswordForEmail(email, {
            redirectTo: window.location.origin + '/reset-password.html'
        });

        if (error) {
            console.error('Password reset error:', error);
            return { error };
        }

        console.log('✅ Password reset email sent');
        return { error: null };
    } catch (err) {
        return { error: { message: err.message } };
    }
}

/**
 * Update user password (after reset)
 * @param {string} newPassword - New password
 * @returns {object} - { user, error }
 */
async function updatePassword(newPassword) {
    if (!supabase) {
        return { user: null, error: { message: 'Supabase not configured' } };
    }

    try {
        const { data, error } = await supabase.auth.updateUser({
            password: newPassword
        });

        if (error) {
            return { user: null, error };
        }

        return { user: data.user, error: null };
    } catch (err) {
        return { user: null, error: { message: err.message } };
    }
}

/**
 * Listen for auth state changes
 * @param {function} callback - Function to call on auth state change
 * @returns {object} - Subscription object with unsubscribe method
 */
function onAuthStateChange(callback) {
    if (!supabase) {
        console.warn('Supabase not configured, auth state changes not available');
        return { unsubscribe: () => {} };
    }

    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
        console.log('Auth state changed:', event);
        callback(event, session);
    });

    return subscription;
}

// ============================================
// ROUTE PROTECTION
// ============================================

/**
 * Check if user is authenticated and redirect if not
 * Call this at the start of protected pages
 * @param {string} redirectTo - URL to redirect to if not authenticated
 * @returns {object|null} - User object if authenticated, null otherwise
 */
async function requireAuth(redirectTo = 'login.html') {
    const initialized = await initSupabase();

    // If Supabase not configured, allow access (demo mode)
    if (!initialized) {
        console.warn('⚠️ Auth check skipped - Supabase not configured');
        return { id: 'demo-user', email: 'demo@example.com' };
    }

    const { user, error } = await getCurrentUser();

    if (error || !user) {
        console.log('🔒 Authentication required, redirecting...');
        window.location.href = redirectTo;
        return null;
    }

    console.log('✅ User authenticated:', user.email);
    return user;
}

/**
 * Redirect if user is already authenticated
 * Call this on login/register pages to redirect logged-in users
 * @param {string} redirectTo - URL to redirect to if authenticated
 */
async function redirectIfAuthenticated(redirectTo = 'index.html') {
    const initialized = await initSupabase();

    if (!initialized) {
        return; // Supabase not configured, don't redirect
    }

    const { user } = await getCurrentUser();

    if (user) {
        console.log('✅ Already authenticated, redirecting...');
        window.location.href = redirectTo;
    }
}

// ============================================
// USER PROFILE FUNCTIONS
// ============================================

/**
 * Update user profile metadata
 * @param {object} metadata - User metadata to update
 * @returns {object} - { user, error }
 */
async function updateProfile(metadata) {
    if (!supabase) {
        return { user: null, error: { message: 'Supabase not configured' } };
    }

    try {
        const { data, error } = await supabase.auth.updateUser({
            data: metadata
        });

        if (error) {
            return { user: null, error };
        }

        return { user: data.user, error: null };
    } catch (err) {
        return { user: null, error: { message: err.message } };
    }
}

/**
 * Get user profile data
 * @returns {object} - User metadata or empty object
 */
async function getProfile() {
    const { user, error } = await getCurrentUser();

    if (error || !user) {
        return {};
    }

    return user.user_metadata || {};
}

// ============================================
// DATABASE FUNCTIONS (for storing analysis results)
// ============================================

/**
 * Save an analysis session to the database
 * @param {object} analysisData - Analysis results to save
 * @returns {object} - { data, error }
 */
async function saveAnalysisSession(analysisData) {
    if (!supabase) {
        console.warn('Supabase not configured, analysis not saved');
        return { data: null, error: { message: 'Supabase not configured' } };
    }

    const { user } = await getCurrentUser();
    if (!user) {
        return { data: null, error: { message: 'Not authenticated' } };
    }

    try {
        const { data, error } = await supabase
            .from('analysis_sessions')
            .insert({
                user_id: user.id,
                file_name: analysisData.fileName || 'Unknown',
                loans_analyzed: analysisData.summary?.total_records || 0,
                alerts_generated: (analysisData.summary?.critical_alerts || 0) +
                                  (analysisData.summary?.high_alerts || 0) +
                                  (analysisData.summary?.medium_alerts || 0),
                risk_score: analysisData.summary?.risk_score || 0,
                results: analysisData,
                created_at: new Date().toISOString()
            })
            .select()
            .single();

        if (error) {
            console.error('Save analysis error:', error);
            return { data: null, error };
        }

        console.log('✅ Analysis saved:', data.id);
        return { data, error: null };
    } catch (err) {
        return { data: null, error: { message: err.message } };
    }
}

/**
 * Get user's analysis history
 * @param {number} limit - Maximum number of records to return
 * @returns {object} - { data, error }
 */
async function getAnalysisHistory(limit = 10) {
    if (!supabase) {
        return { data: [], error: { message: 'Supabase not configured' } };
    }

    const { user } = await getCurrentUser();
    if (!user) {
        return { data: [], error: { message: 'Not authenticated' } };
    }

    try {
        const { data, error } = await supabase
            .from('analysis_sessions')
            .select('*')
            .eq('user_id', user.id)
            .order('created_at', { ascending: false })
            .limit(limit);

        if (error) {
            return { data: [], error };
        }

        return { data: data || [], error: null };
    } catch (err) {
        return { data: [], error: { message: err.message } };
    }
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Check if Supabase is properly configured
 * @returns {boolean}
 */
function isSupabaseConfigured() {
    return SUPABASE_URL !== 'YOUR_SUPABASE_URL' &&
           SUPABASE_ANON_KEY !== 'YOUR_SUPABASE_ANON_KEY';
}

/**
 * Get configuration status for UI display
 * @returns {object} - { configured, url }
 */
function getConfigStatus() {
    return {
        configured: isSupabaseConfigured(),
        url: isSupabaseConfigured() ? SUPABASE_URL : null
    };
}

// ============================================
// EXPORTS
// ============================================

// Make functions available globally
window.FraudShieldAuth = {
    // Initialization
    init: initSupabase,
    isConfigured: isSupabaseConfigured,
    getConfigStatus,

    // Authentication
    signUp,
    signIn,
    signOut,
    getCurrentUser,
    getSession,
    resetPassword,
    updatePassword,
    onAuthStateChange,

    // Route protection
    requireAuth,
    redirectIfAuthenticated,

    // Profile
    updateProfile,
    getProfile,

    // Database
    saveAnalysisSession,
    getAnalysisHistory
};

// Auto-initialize on module load
initSupabase();
