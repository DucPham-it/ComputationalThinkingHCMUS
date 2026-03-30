CREATE TABLE reviews (
    id INT PRIMARY KEY,
    user_id INT NOT NULL,
    place_id INT NOT NULL,
    content NVARCHAR(MAX) NOT NULL,
    rating INT NOT NULL
);
