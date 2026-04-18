INSERT INTO places (name, address, rating, latitude, longitude, price_level, open_now, photo_url, contact_phone, primary_type)
SELECT * FROM (
    VALUES
        ('Giga Mall Thủ Đức', '240-242 Phạm Văn Đồng, Hiệp Bình Chánh, Thủ Đức, Hồ Chí Minh', 4.6, 10.839482, 106.728202, 2, TRUE, NULL, NULL, 'shopping_mall'),
        ('Vincom Plaza Thủ Đức', '216 Võ Văn Ngân, Bình Thọ, Thủ Đức, Hồ Chí Minh', 4.4, 10.850742, 106.771805, 2, TRUE, NULL, NULL, 'shopping_mall'),
        ('Suối Tiên Theme Park', '120 Xa Lộ Hà Nội, Tân Phú, Thủ Đức, Hồ Chí Minh', 4.4, 10.867814, 106.802802, 2, TRUE, NULL, NULL, 'amusement_park'),
        ('Khu du lịch Văn Thánh', '48/10 Điện Biên Phủ, Bình Thạnh, Hồ Chí Minh', 4.3, 10.803912, 106.720488, 2, TRUE, NULL, NULL, 'tourist_attraction'),
        ('Dinh Độc Lập', '135 Nam Kỳ Khởi Nghĩa, Bến Thành, Quận 1, Hồ Chí Minh', 4.6, 10.777098, 106.695313, 1, TRUE, NULL, NULL, 'tourist_attraction'),
        ('Saigon Centre Takashimaya', '65 Lê Lợi, Bến Nghé, Quận 1, Hồ Chí Minh', 4.5, 10.773664, 106.700276, 3, TRUE, NULL, NULL, 'shopping_mall'),
        ('Thảo Cầm Viên Sài Gòn', '2 Nguyễn Bỉnh Khiêm, Bến Nghé, Quận 1, Hồ Chí Minh', 4.4, 10.787028, 106.705429, 1, TRUE, NULL, NULL, 'park'),
        ('Công viên Lê Thị Riêng', '875 Cách Mạng Tháng 8, Phường 15, Quận 10, Hồ Chí Minh', 4.3, 10.786916, 106.664632, 1, TRUE, NULL, NULL, 'park'),
        ('AEON Mall Bình Tân', '1 Đường Số 17A, Bình Trị Đông B, Bình Tân, Hồ Chí Minh', 4.6, 10.801876, 106.618744, 2, TRUE, NULL, NULL, 'shopping_mall'),
        ('Crescent Mall', '101 Tôn Dật Tiên, Tân Phú, Quận 7, Hồ Chí Minh', 4.5, 10.729599, 106.718225, 3, TRUE, NULL, NULL, 'shopping_mall'),
        ('Khu du lịch Bình Quới', '1147 Bình Quới, Phường 28, Bình Thạnh, Hồ Chí Minh', 4.4, 10.826315, 106.734232, 2, TRUE, NULL, NULL, 'tourist_attraction'),
        ('Công viên Thành phố mới Bình Dương', 'Hùng Vương, Hòa Phú, Thủ Dầu Một, Bình Dương', 4.5, 10.987452, 106.664523, 1, TRUE, NULL, NULL, 'park'),
        ('AEON Mall Bình Dương Canary', '1 Đại lộ Bình Dương, Thuận An, Bình Dương', 4.6, 10.894977, 106.744809, 2, TRUE, NULL, NULL, 'shopping_mall'),
        ('Lạc Cảnh Đại Nam Văn Hiến', '1765A Đại lộ Bình Dương, Hiệp An, Thủ Dầu Một, Bình Dương', 4.3, 11.036529, 106.676945, 2, TRUE, NULL, NULL, 'amusement_park'),
        ('Bửu Long Tourist Area', 'Huỳnh Văn Nghệ, Bửu Long, Biên Hòa, Đồng Nai', 4.4, 10.977874, 106.854296, 1, TRUE, NULL, NULL, 'tourist_attraction'),
        ('Vincom Plaza Biên Hòa', '1096 Phạm Văn Thuận, Tân Mai, Biên Hòa, Đồng Nai', 4.4, 10.944812, 106.823741, 2, TRUE, NULL, NULL, 'shopping_mall'),
        ('Sơn Tiên Tourist City', 'Xa lộ Hà Nội, An Hòa, Biên Hòa, Đồng Nai', 4.2, 10.896851, 106.892542, 2, TRUE, NULL, NULL, 'amusement_park'),
        ('Bãi Sau Vũng Tàu', 'Thùy Vân, Phường Thắng Tam, Vũng Tàu, Bà Rịa - Vũng Tàu', 4.5, 10.336944, 107.094444, 1, TRUE, NULL, NULL, 'tourist_attraction'),
        ('Công viên Bãi Trước', 'Quang Trung, Phường 1, Vũng Tàu, Bà Rịa - Vũng Tàu', 4.5, 10.346214, 107.084948, 1, TRUE, NULL, NULL, 'park'),
        ('Lotte Mart Vũng Tàu', 'Đường 3/2, Phường 10, Vũng Tàu, Bà Rịa - Vũng Tàu', 4.4, 10.361736, 107.101074, 2, TRUE, NULL, NULL, 'shopping_mall')
) AS seed(name, address, rating, latitude, longitude, price_level, open_now, photo_url, contact_phone, primary_type)
WHERE NOT EXISTS (
    SELECT 1
    FROM places
    WHERE places.name = seed.name
      AND places.address = seed.address
);
