## Table `admins`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `user_id` | `int8` | Primary |
| `status` | `text` |  |
| `role` | `text` |  |
| `approved_by` | `int8` |  Nullable |
| `approved_at` | `timestamptz` |  Nullable |
| `created_at` | `timestamptz` |  |

## Table `favorites`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `id` | `int8` | Primary |
| `user_id` | `int8` |  |
| `place_id` | `int8` |  |

## Table `place_change_request_images`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `id` | `int8` | Primary |
| `request_id` | `int8` |  |
| `image_type` | `text` |  |
| `image_url` | `text` |  |
| `sort_order` | `int4` |  |
| `created_at` | `timestamptz` |  |

## Table `place_change_requests`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `id` | `int8` | Primary |
| `requester_user_id` | `int8` |  |
| `request_type` | `text` |  |
| `status` | `text` |  |
| `target_place_id` | `int8` |  Nullable |
| `title` | `text` |  Nullable |
| `category` | `text` |  Nullable |
| `address_text` | `text` |  Nullable |
| `latitude` | `float8` |  Nullable |
| `longitude` | `float8` |  Nullable |
| `price_range` | `text` |  Nullable |
| `price_level` | `int4` |  Nullable |
| `website` | `text` |  Nullable |
| `phone` | `text` |  Nullable |
| `descriptions` | `text` |  Nullable |
| `request_note` | `text` |  Nullable |
| `review_content` | `text` |  Nullable |
| `review_rating` | `int4` |  Nullable |
| `admin_user_id` | `int8` |  Nullable |
| `admin_note` | `text` |  Nullable |
| `created_at` | `timestamptz` |  |
| `reviewed_at` | `timestamptz` |  Nullable |

## Table `place_images`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `id` | `int8` | Primary |
| `place_id` | `int8` |  |
| `image_url` | `text` |  |
| `title` | `text` |  Nullable |
| `sort_order` | `int4` |  |
| `is_primary` | `bool` |  |
| `source` | `text` |  |
| `created_at` | `timestamptz` |  |

## Table `place_review_stats`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `place_id` | `int8` | Primary |
| `average_rating` | `numeric` |  Nullable |
| `review_count` | `int4` |  |
| `rating_1_count` | `int4` |  |
| `rating_2_count` | `int4` |  |
| `rating_3_count` | `int4` |  |
| `rating_4_count` | `int4` |  |
| `rating_5_count` | `int4` |  |
| `updated_at` | `timestamptz` |  |

## Table `places`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `id` | `int8` | Primary |
| `title` | `text` |  |
| `category` | `text` |  Nullable |
| `complete_address_json` | `text` |  Nullable |
| `address_text` | `text` |  |
| `borough` | `text` |  Nullable |
| `street` | `text` |  Nullable |
| `city` | `text` |  Nullable |
| `postal_code` | `text` |  Nullable |
| `state` | `text` |  Nullable |
| `country` | `text` |  Nullable |
| `latitude` | `float8` |  Nullable |
| `longitude` | `float8` |  Nullable |
| `open_hours_json` | `text` |  |
| `popular_times_json` | `text` |  |
| `price_range` | `text` |  Nullable |
| `price_level` | `int4` |  Nullable |
| `website` | `text` |  Nullable |
| `phone` | `text` |  Nullable |
| `descriptions` | `text` |  Nullable |
| `about_json` | `text` |  |
| `status` | `text` |  Nullable |
| `place_id` | `text` |  Nullable Unique |
| `cid` | `text` |  Nullable Unique |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

## Table `review_images`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `id` | `int8` | Primary |
| `review_id` | `int8` |  |
| `image_url` | `text` |  |
| `sort_order` | `int4` |  |
| `created_at` | `timestamptz` |  |

## Table `social_post_comments`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `id` | `int8` | Primary |
| `post_id` | `int8` |  |
| `user_id` | `int8` |  |
| `content` | `text` |  |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

## Table `social_post_likes`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `id` | `int8` | Primary |
| `post_id` | `int8` | Unique with user_id |
| `user_id` | `int8` | Unique with post_id |
| `created_at` | `timestamptz` |  |

## Table `social_post_shares`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `id` | `int8` | Primary |
| `post_id` | `int8` | Unique with user_id |
| `user_id` | `int8` | Unique with post_id |
| `created_at` | `timestamptz` |  |

## Table `social_posts`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `id` | `int8` | Primary |
| `user_id` | `int8` |  |
| `place_id` | `int8` |  |
| `visited_place_id` | `int8` | Nullable |
| `content` | `text` |  |
| `rating` | `int4` |  |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

## Table `user_visited_places`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `id` | `int8` | Primary |
| `user_id` | `int8` |  |
| `place_id` | `int8` |  |
| `route_origin` | `text` | Nullable |
| `route_destination` | `text` | Nullable |
| `distance_text` | `text` | Nullable |
| `duration_text` | `text` | Nullable |
| `distance_km` | `float8` | Nullable |
| `duration_seconds` | `int4` | Nullable |
| `travel_mode` | `text` | Nullable |
| `visited_at` | `timestamptz` |  |

## Table `reviews`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `id` | `int8` | Primary |
| `user_id` | `int8` |  |
| `place_id` | `int8` |  |
| `content` | `text` |  |
| `rating` | `int4` |  |
| `reviewed_at` | `text` |  Nullable |
| `is_imported` | `bool` |  |
| `created_at` | `timestamptz` |  |

## Table `user_place_picks`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `id` | `int8` | Primary |
| `user_id` | `int8` |  |
| `place_id` | `int8` |  |
| `picked_at` | `timestamptz` |  |

## Table `user_search_history`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `id` | `int8` | Primary |
| `user_id` | `int8` |  |
| `query` | `text` |  |
| `latitude` | `float8` |  Nullable |
| `longitude` | `float8` |  Nullable |
| `searched_at` | `timestamptz` |  |

## Table `users`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `id` | `int8` | Primary |
| `user_name` | `text` |  Unique |
| `email` | `text` |  Unique |
| `password_hash` | `text` |  |
| `first_name` | `text` |  Nullable |
| `last_name` | `text` |  Nullable |
| `birth_date` | `date` |  Nullable |
| `gender` | `text` |  Nullable |
| `address` | `text` |  Nullable |
| `avatar_url` | `text` |  Nullable |
| `is_virtual` | `bool` |  |
| `created_at` | `timestamptz` |  |
