-- Alternative approach: Create a function that gets display_name by user_email
CREATE OR REPLACE FUNCTION get_display_name_by_email(email_param TEXT)
RETURNS TEXT AS $$
DECLARE
    result TEXT;
BEGIN
    SELECT display_name INTO result
    FROM users 
    WHERE email = email_param;
    
    RETURN COALESCE(result, 'Unknown User');
END;
$$ LANGUAGE plpgsql;

-- Then we could modify the table to have a computed column (but this is more complex)
-- For now, the trigger approach is better