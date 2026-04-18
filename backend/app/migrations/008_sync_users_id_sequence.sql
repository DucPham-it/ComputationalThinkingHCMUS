DO $$
DECLARE
    seq_name text;
    max_id bigint;
BEGIN
    seq_name := pg_get_serial_sequence('users', 'id');
    IF seq_name IS NULL THEN
        RETURN;
    END IF;

    SELECT MAX(id) INTO max_id FROM users;

    IF max_id IS NULL THEN
        EXECUTE 'SELECT setval(' || quote_literal(seq_name) || ', 1, false)';
    ELSE
        EXECUTE 'SELECT setval(' || quote_literal(seq_name) || ', ' || max_id || ', true)';
    END IF;
END $$;
