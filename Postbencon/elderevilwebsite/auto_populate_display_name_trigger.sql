-- Create a trigger function that automatically populates display_name from users table
CREATE OR REPLACE FUNCTION auto_populate_display_name()
RETURNS TRIGGER AS $$
BEGIN
    -- If display_name is NULL or empty, get it from the users table
    IF NEW.display_name IS NULL OR NEW.display_name = '' THEN
        SELECT display_name INTO NEW.display_name
        FROM users 
        WHERE email = NEW.user_email;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger that runs before INSERT on tavern_messages
CREATE TRIGGER trigger_auto_populate_display_name
    BEFORE INSERT ON tavern_messages
    FOR EACH ROW
    EXECUTE FUNCTION auto_populate_display_name();

-- Also create an UPDATE trigger in case display_name is updated to NULL
CREATE TRIGGER trigger_auto_populate_display_name_update
    BEFORE UPDATE ON tavern_messages
    FOR EACH ROW
    EXECUTE FUNCTION auto_populate_display_name();