## Data Sources Documentation

This document describes the core data sources in the `Data Sources` folder, their schemas, and how they relate to each other for analytics and data warehousing purposes.

- **Scope**: `customers.csv`, `orders.csv`, `order_items.csv`, `promotions.csv`
- **Domain**: E‑commerce sales, customers, and marketing promotions

---

## `customers.csv`

**Grain**: One row per unique customer.

**Primary key**
- `customer_id` (integer): Unique identifier for each customer.

**Columns**

| Column                    | Type        | Description |
|---------------------------|------------|-------------|
| `customer_id`            | int        | Unique ID of the customer. Used to link to `orders.customer_id`. |
| `first_name`             | string     | Customer's first name. |
| `last_name`              | string     | Customer's last name. |
| `email`                  | string     | Customer email address (used for communication and identification). |
| `phone_number`           | string     | Customer phone number including country code. |
| `registration_date`      | datetime   | Timestamp when the customer registered in the system. |
| `customer_segment`       | string     | Current or most recent customer value segment (e.g. `New_Customer`, `Low_Value`, `Medium_Value`, `High_Value`, `Lapsed`). |
| `preferred_channel`      | string     | Preferred marketing/communication channel (e.g. `Email`, `SMS`, `Push`, `Social`, `Direct`). |
| `age_group`              | string     | Age band of the customer (e.g. `18-25`, `26-35`, `36-45`, `46-55`, `55+`). May be blank if unknown. |
| `income_level`           | string     | Income band (`Low`, `Medium`, `High`, `Premium`) or blank if unknown. |
| `avg_order_value`        | decimal    | Historical average order value for the customer. |
| `promo_sensitivity`      | decimal    | Score between 0 and 1 indicating how responsive the customer is to promotions (higher = more sensitive). |
| `email_opt_in`           | boolean    | Whether the customer has opted in to email communications. |
| `sms_opt_in`             | boolean    | Whether the customer has opted in to SMS communications. |
| `push_opt_in`            | boolean    | Whether the customer has opted in to app push notifications. |
| `last_purchase_date`     | datetime   | Timestamp of the most recent completed purchase, if any. May be blank for non-buyers. |
| `total_lifetime_orders`  | int        | Total count of historical orders placed by the customer. |
| `preferred_category`     | string     | Product category this customer most frequently buys from (e.g. `Books`, `Electronics`, `Clothing`, `Home`, `Sports`, `Beauty`). |

**Usage notes**
- Use as the primary customer dimension in analytical models.
- Combine with `orders` and `order_items` to derive customer lifetime value, recency, frequency, and channel performance.

---

## `orders.csv`

**Grain**: One row per order.

**Primary key**
- `order_id` (integer): Unique identifier for each order.

**Foreign keys**
- `customer_id` → `customers.customer_id`
- `promotion_id` → `promotions.promotion_id` (nullable, only populated when a promotion is associated to the order).

**Columns**

| Column                      | Type      | Description |
|-----------------------------|-----------|-------------|
| `order_id`                 | int       | Unique ID of the order. Links to `order_items.order_id`. |
| `customer_id`              | int       | ID of the customer who placed the order. Links to `customers.customer_id`. |
| `order_date`               | datetime  | Timestamp when the order was created. |
| `order_status`             | string    | Status of the order (e.g. `PAID`, `CANCEL`). |
| `promotion_id`             | int       | ID of the promotion applied at order level, if any. Links to `promotions.promotion_id`. May be blank. |
| `order_channel`            | string    | Channel through which the order was placed (e.g. `Email`, `SMS`, `Push`, `Social`, `Direct`, `Website`, `In_App`). |
| `order_value`              | decimal   | Monetary value of the order (typically sum of `order_items` net of discounts). |
| `attributed_to_promo`      | boolean   | Indicates whether this order is considered influenced by a promotion. |
| `customer_segment_at_time` | string    | Customer segment snapshot at the time of order (e.g. `New_Customer`, `High_Value`). May differ from current `customers.customer_segment`. |

**Usage notes**
- Use as the main fact table for order-level analytics (e.g. revenue by day, channel, promotion).
- Combine with `order_items` for product-level detail and with `promotions` to measure campaign performance.
- Filter on `order_status = 'PAID'` to approximate completed, billable orders.

---

## `order_items.csv`

**Grain**: One row per product line item on an order.

**Primary key**
- `order_item_id` (integer): Unique identifier for each order line item.

**Foreign keys**
- `order_id` → `orders.order_id`
- `promotion_id` → `promotions.promotion_id` (nullable, only populated when a promotion is associated to this specific item).

**Columns**

| Column           | Type      | Description |
|------------------|-----------|-------------|
| `order_item_id` | int       | Unique ID for the order line item. |
| `order_id`      | int       | ID of the parent order. Links to `orders.order_id`. |
| `product_id`    | int       | Identifier for the product purchased. Product dimension is not included in this folder but could join to a separate product table if available. |
| `product_category` | string | High-level category of the product (e.g. `Books`, `Electronics`, `Clothing`, `Home`, `Sports`, `Beauty`). |
| `quantity`      | int       | Number of units of the product in this line item. |
| `unit_price`    | decimal   | Price per unit at time of purchase (before/after discount depending on modeling). |
| `promotion_id`  | int       | ID of the promotion applied to this line item, if any. Links to `promotions.promotion_id`. May be blank. |
| `attributed_to_promo` | boolean | Indicates whether this specific line item is attributed to the associated promotion. |

**Usage notes**
- Use to analyze product- and category-level performance, basket composition, and promotion effectiveness at the item level.
- Summing `quantity * unit_price` (with appropriate filters) can be used to recompute revenue and compare with `orders.order_value`.

---

## `promotions.csv`

**Grain**: One row per marketing promotion or campaign.

**Primary key**
- `promotion_id` (integer): Unique identifier for each promotion.

**Columns**

| Column                  | Type      | Description |
|-------------------------|-----------|-------------|
| `promotion_id`         | int       | Unique ID of the promotion. Links from `orders.promotion_id` and `order_items.promotion_id`. |
| `campaign_name`        | string    | Human-readable name of the promotion (includes type and an index, e.g. `Acquisition_BOGO_3`). |
| `promo_type`           | string    | Promotion mechanism type (e.g. `Fixed_Amount`, `Percentage_Discount`, `BOGO`, `Free_Shipping`). |
| `discount_value`       | decimal   | Size of the discount. Interpretation depends on `promo_type` (e.g. amount off, percentage off). May be `0.0` for non-discount promotions like `BOGO` or `Free_Shipping`. |
| `min_order_value`      | decimal   | Minimum order value required to be eligible for the promotion. May be `0.0` or blank if no threshold. |
| `start_date`           | datetime  | Campaign start timestamp. |
| `end_date`             | datetime  | Campaign end timestamp. |
| `campaign_duration_days` | int     | Duration of the campaign in days. |
| `target_segment`       | string    | Intended customer segment for the promotion (e.g. `High_Value`, `Low_Value`, `Medium_Value`, `New_Customer`, `Lapsed`, `All_Customers`). |
| `campaign_channel`     | string    | Channel where the campaign runs (e.g. `Email`, `SMS`, `Push`, `Social`, `Website_Banner`, `In_App`). |
| `campaign_objective`   | string    | Primary objective (e.g. `Acquisition`, `Retention`, `Reactivation`, `Upsell`, `Cross_Sell`). |
| `target_category`      | string    | Product category targeted by the promotion, if applicable (e.g. `Books`, `Home`, `Clothing`, etc.). May be blank if it applies to all categories. |
| `expected_response_rate` | decimal | Expected fraction of targeted customers who will respond (typically between 0 and 1). |
| `budget_allocated`     | decimal   | Total budget assigned to the promotion. |
| `cost_per_acquisition` | decimal   | Expected or modeled cost per acquisition for this promotion. |

**Usage notes**
- Join to `orders` and `order_items` to evaluate uplift, ROI, and performance by campaign, promo type, channel, and target segment.
- Filter by `campaign_objective` to segment analyses into acquisition, retention, reactivation, upsell, and cross-sell initiatives.

---

## Relationships Summary

- **Customers ↔ Orders**
  - `orders.customer_id` → `customers.customer_id`
  - Enables customer-level analysis of order frequency, recency, and revenue.

- **Orders ↔ Order Items**
  - `order_items.order_id` → `orders.order_id`
  - Enables drilling from orders into product-level details and constructing full baskets.

- **Promotions ↔ Orders and Order Items**
  - `orders.promotion_id` → `promotions.promotion_id` (order-level promotions).
  - `order_items.promotion_id` → `promotions.promotion_id` (item-level promotions).
  - Together with `attributed_to_promo` flags, supports promotion attribution and effectiveness measurement.

These structures are suitable as a base for a star-schema style data warehouse, with `customers` and `promotions` as dimensions and `orders` and `order_items` as core fact tables.
