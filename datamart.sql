SELECT
	c.customer_id,
	concat(c.first_name, ' ', c.last_name) AS fullname,
	o.order_value 
FROM data_warehouse.orders o
JOIN data_warehouse.customers c
ON o.customer_id = c.customer_id
ORDER BY order_value DESC 
LIMIT 5
;

SELECT
	oi.product_id,
	oi.product_category,
	SUM(oi.quantity * oi.unit_price) AS order_value
FROM data_warehouse.orders o
JOIN data_warehouse.order_items oi
ON o.order_id = oi.order_id 
WHERE EXTRACT(YEAR FROM o.order_date) = 2025
GROUP BY 1,2
ORDER BY order_value DESC 
LIMIT 10
;
