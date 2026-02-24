import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://umlsrrxjhejbtrcsetvc.supabase.co';
const supabaseKey = 'sb_publishable_TeuSZRDheMeFNhUiUrlMNw_UYAaHz2g';

export const supabase = createClient(supabaseUrl, supabaseKey);
