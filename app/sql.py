DummySQL = "SELECT * FROM Car"
FilterCustomer = "SELECT * FROM Customer where customerID=%s"
SalesByManufacturer = """
SELECT allManu.manu_name, COALESCE(`30days`, '0') as '30days', COALESCE(`365days`, '0') as '365days', COALESCE(`allTime`, '0') as 'allTime' FROM Manufacturer AS allManu
LEFT JOIN
(SELECT Manufacturer.manu_name, COUNT(*) AS 30days
FROM Purchase, Vehicle, Manufacturer
WHERE DATEDIFF(CURDATE() - 1, purchase_date) <= 30
AND Purchase.VIN = Vehicle.VIN
AND Vehicle.manu_name = Manufacturer.manu_name
Group By Manufacturer.manu_name) AS daysform
ON daysform.manu_name = allManu.manu_name
LEFT JOIN
(SELECT Manufacturer.manu_name, COUNT(*) AS 365days
FROM Purchase, Vehicle, Manufacturer
WHERE DATEDIFF(CURDATE() - 1, purchase_date) <= 365
AND Purchase.VIN = Vehicle.VIN
AND Vehicle.manu_name = Manufacturer.manu_name
Group By Manufacturer.manu_name
) AS yearsform
ON yearsform.manu_name = allManu.manu_name
LEFT JOIN
(SELECT Manufacturer.manu_name, COUNT(*) AS allTime
FROM Purchase, Vehicle, Manufacturer
WHERE Purchase.VIN = Vehicle.VIN
AND Vehicle.manu_name = Manufacturer.manu_name
Group By Manufacturer.manu_name
) AS allTimeform
ON allTimeform.manu_name = allManu.manu_name
WHERE 30days != 0 OR 365days != 0 OR allTime != 0
ORDER BY allManu.manu_name ASC
"""

SalesByType = """
SELECT DISTINCT allType.type_name, COALESCE(`30days`, '0') as '30days', COALESCE(`365days`, '0') as '365days', COALESCE(`allTime`, '0') as 'allTime' FROM VehicleType AS allType
LEFT JOIN
(SELECT type_name, COUNT(*) AS 30days
FROM Purchase, Vehicle, VehicleType
WHERE DATEDIFF(CURDATE() - 1, purchase_date) <= 30
AND Purchase.VIN = Vehicle.VIN
AND Vehicle.vehicleTypeID = VehicleType.vehicleTypeID
Group By type_name) AS daysform
ON daysform.type_name = allType.type_name
LEFT JOIN
(SELECT type_name, COUNT(*) AS 365days
FROM Purchase, Vehicle, VehicleType
WHERE DATEDIFF(CURDATE() - 1, purchase_date) <= 365
AND Purchase.VIN = Vehicle.VIN
AND Vehicle.vehicleTypeID = VehicleType.vehicleTypeID
Group By type_name
) AS yearsform
ON yearsform.type_name = allType.type_name
LEFT JOIN
(SELECT type_name, COUNT(*) AS allTime
FROM Purchase, Vehicle, VehicleType
WHERE Purchase.VIN = Vehicle.VIN
AND Vehicle.vehicleTypeID = VehicleType.vehicleTypeID
Group By type_name
) AS allTimeform
ON allTimeform.type_name = allType.type_name
ORDER BY allType.type_name ASC"""

PartStatistics = """
SELECT vendor_name, SUM(part_quantity) as quantityPerVendor, SUM(part_quantity * price) as dollorAmountPerVendor
FROM Part
GROUP BY vendor_name
ORDER BY dollorAmountPerVendor DESC"""


SalesByColor = """
SELECT allColor.CategorizedColor, COALESCE(`30days`, '0') as '30days', COALESCE(`365days`, '0') as '365days', COALESCE(`allTime`, '0') as 'allTime' FROM 
(SELECT DISTINCT(CategorizedColor)
FROM
(SELECT VIN,
(CASE WHEN amtPerColor > 1
THEN 'Multiple'
ELSE color
END) AS CategorizedColor 
FROM
(SELECT VIN, color, COUNT(*) AS amtPerColor
FROM VehicleColor
GROUP BY VehicleColor.VIN) AS amtPerCForm) AS VINCateColor)
AS allColor
LEFT JOIN
(SELECT VINCateColor.CategorizedColor, COUNT(*) AS 30days
FROM Purchase, 
(SELECT VIN,
(CASE WHEN amtPerColor > 1
THEN 'Multiple'
ELSE color
END) AS CategorizedColor 
FROM
(SELECT VIN, color, COUNT(*) AS amtPerColor
FROM VehicleColor
GROUP BY VehicleColor.VIN) AS amtPerCForm) AS VINCateColor
WHERE DATEDIFF(CURDATE() - 1, purchase_date) <= 30
AND Purchase.VIN = VINCateColor.VIN
Group By VINCateColor.CategorizedColor) AS daysform
ON daysform.CategorizedColor = allColor.CategorizedColor
LEFT JOIN
(SELECT VINCateColor.CategorizedColor, COUNT(*) AS 365days
FROM Purchase, 
(SELECT VIN,
(CASE WHEN amtPerColor > 1
THEN 'Multiple'
ELSE color
END) AS CategorizedColor 
FROM
(SELECT VIN, color, COUNT(*) AS amtPerColor
FROM VehicleColor
GROUP BY VehicleColor.VIN) AS amtPerCForm) AS VINCateColor
WHERE DATEDIFF(CURDATE() - 1, purchase_date) <= 365
AND Purchase.VIN = VINCateColor.VIN
Group By VINCateColor.CategorizedColor) AS yearsform
ON yearsform.CategorizedColor = allColor.CategorizedColor
LEFT JOIN
(SELECT VINCateColor.CategorizedColor, COUNT(*) AS allTime
FROM Purchase,
(SELECT VIN,
(CASE WHEN amtPerColor > 1
THEN 'Multiple'
ELSE color
END) AS CategorizedColor 
FROM
(SELECT VIN, color, COUNT(*) AS amtPerColor
FROM VehicleColor
GROUP BY VehicleColor.VIN) AS amtPerCForm) AS VINCateColor
WHERE Purchase.VIN = VINCateColor.VIN
Group By VINCateColor.CategorizedColor) AS allTimeform
ON allTimeform.CategorizedColor = allColor.CategorizedColor
ORDER BY allColor.CategorizedColor ASC
"""
AvailableVehicles = """
SELECT COUNT(DISTINCT VIN) 
FROM Vehicle
WHERE VIN NOT IN (SELECT VIN FROM Purchase)
"""

AverageInventoryTime = """
SELECT t.type_name, IFNULL(AVG(datediff(p.purchase_date, v.inbound_date) + 1), 'N/A') AS inventory_time
FROM Purchase AS p
RIGHT OUTER JOIN Vehicle AS v
ON v.VIN = p.VIN
LEFT JOIN VehicleType AS t
ON  t.vehicleTypeID = v.vehicleTypeID
GROUP BY t.type_name
ORDER BY t.type_name ASC;
"""

BelowCost = """
SELECT purchase_date,
       invoice_price,
       sold_price,
       ratio,
       customer_name,
       ( user_first_name + ' ' + user_last_name ) AS salesperson_name
FROM   (SELECT purchase_date,
               invoice_price,
               sold_price,
               ( sold_price / invoice_price ) AS ratio,
               customer_name,
               username
        FROM   Purchase
               LEFT JOIN (SELECT customerID,
                                 ( ind_first_name + ' ' + ind_last_name ) AS
                                 customer_name
                          FROM   Individual
                          UNION
                          SELECT customerID,
                                 business_name AS customer_name
                          FROM   Business) AS CustomerName
                      ON Purchase.customerID = CustomerName.customerID
               LEFT JOIN Vehicle
                      ON Purchase.vin = Vehicle.vin
               LEFT JOIN (SELECT username,
                                 salesInputterID
                          FROM   Salesperson
                          UNION
                          SELECT username,
                                 salesInputterID
                          FROM   Owner) AS SalesInputterWithUsername
                      ON Purchase.salesInputterID =
                         SalesInputterWithUsername.salesInputterID) AS
       temp_table
       LEFT JOIN RegisteredUser
              ON temp_table.username = RegisteredUser.username
-- WHERE ratio <= 0.95
ORDER  BY purchase_date DESC,
          ratio DESC
"""

GrossIncome = """
create view customer_names AS
SELECT customerID, concat(ind_first_name,' ', ind_last_name) as customer_name FROM Individual
UNION ALL
SELECT customerID, business_name as customer_name FROM Business;
create view customer_sales AS (
SELECT customerID, count(sold_price) AS sales_count, sum(sold_price) AS total_sales, MIN(purchase_date) AS first_sale, MAX(purchase_date) AS last_sale
FROM Purchase 
GROUP BY customerID);
create view customer_repairs AS (
SELECT d.customerID, d.repair_count, d.labor_sum, d.first_repair, d.last_repair, e. total_part, (d.labor_sum+e.total_part) AS total_repair
FROM
	(SELECT customerID, count(labor_charge) AS repair_count, sum(labor_charge) AS labor_sum, MIN(start_date) AS first_repair, MAX(start_date) AS last_repair
	FROM Repair
	GROUP BY customerID) AS d
LEFT JOIN
	(SELECT customerID, sum(part_amount) AS total_part
	FROM 
	(SELECT a.VIN, a.customerID, a.start_date, b.part_number, (b.used_part_quantity * c.price)  AS part_amount
	FROM Repair as a
	LEFT JOIN Uses as b
	ON a.VIN=b.VIN and a.customerID=b.customerID and a.start_date=b.start_date
	LEFT JOIN Part AS c
	ON b.part_number=c.part_number) AS f

	GROUP BY customerID) AS e
ON d.customerID=e.customerID
);
create view top15 AS (
SELECT a.customer_name, b.first_sale, b.last_sale, c.first_repair, c.last_repair, b.sales_count, c.repair_count, (b.total_sales+c.total_repair) as gross_income
FROM customer_names AS a
LEFT JOIN customer_sales AS b
ON a.customerID=b.customerID
LEFT JOIN customer_repairs AS c
ON a.customerID=c.customerID
ORDER BY gross_income DESC, last_sale DESC, last_repair DESC
LIMIT 15);
SELECT a.customer_name, b.*
FROM customer_names AS a
LEFT JOIN 
	(SELECT a.customerID, a.purchase_date, a.sold_price, a.VIN, b.model_year, b.manu_name, b.model_name, c.username AS salesname
	FROM Purchase AS a
	LEFT JOIN Vehicle AS b
	ON a.VIN=b.VIN
	LEFT JOIN Salesperson AS c
	ON a.SalesInputterID=c.SalesInputterID) AS b 
ON a.customerID=b.customerID
WHERE  a.customer_name='Dennis Conley'
ORDER BY b.purchase_date DESC, VIN ASC ;
SELECT a.customer_name, b.*
FROM customer_names AS a
LEFT JOIN 
	(
	SELECT a.customerID, a.start_date, a.complete_date, a.VIN, a.odometer, a.labor_charge, c.one_total_part, (a.labor_charge+c.one_total_part) as one_total_cost, b.username AS service_writer
	FROM Repair AS a
	LEFT JOIN ServiceWriter AS b
	ON a.RecordInputterID=b.RecordInputterID

	LEFT JOIN

		(SELECT VIN, customerID, start_date, SUM(part_amount) AS  one_total_part
		FROM 
			(SELECT a.VIN, a.customerID, a.start_date, (a.used_part_quantity*b.price) AS part_amount
			FROM Uses AS a
			LEFT JOIN Part AS b
			ON a.part_number=b.part_number) AS e
		GROUP BY VIN, customerID, start_date) AS c

	ON a.VIN=c.VIN AND a.customerID=c.customerID AND a.start_date=c.start_date
	) AS b

ON a.customerID=b.customerID
WHERE  customer_name='Dennis Conley'
ORDER BY start_date DESC,  complete_date IS NULL DESC, complete_date DESC, VIN ASC;
"""

MonthlySale = """
SELECT DATE_FORMAT(p.purchase_date, '%Y-%m') as YYYYMM , 
      COUNT(*) as TotalNumber, 
      SUM(p.sold_price) as TotalSalesIncome, 
      SUM(p.sold_price - v.invoice_price) AS NetIncome,
      FORMAT(SUM(p.sold_price) * 100.0 / SUM(v.invoice_price), 'P2') AS Ratio,
         CASE 
              WHEN SUM(p.sold_price) / SUM(v.invoice_price) > 1.25 THEN 'Green'
              WHEN SUM(p.sold_price) / SUM(v.invoice_price) <= 1.10 THEN 'Yellow'
          ELSE 'N/A'
       END AS DisplayColor
FROM Purchase AS p
LEFT JOIN Vehicle AS v
ON p.VIN = v.VIN
GROUP BY YEAR(p.purchase_date), MONTH(p.purchase_date)
ORDER BY YEAR(p.purchase_date), MONTH(p.purchase_date) DESC;
"""

RepairReport = """
create view total_VIN_manu AS (
SELECT a.VIN, a.repair_count, a. total_labor_VIN, b. total_part_amount_VIN, (a. total_labor_VIN+b. total_part_amount_VIN) AS total_VIN, c.manu_name, c.vehicleTypeID, c.model_name

FROM
	(SELECT VIN, count(labor_charge) as repair_count, sum(labor_charge) as total_labor_VIN
	FROM Repair
	GROUP BY VIN) AS a

LEFT JOIN
	(SELECT VIN, sum(part_amount) AS total_part_amount_VIN

	FROM 

		(SELECT a.VIN, a.customerID, a.start_date, b.part_number, (b.used_part_quantity * c.price) AS part_amount
		FROM Repair as a
		LEFT JOIN Uses as b
		ON a.VIN=b.VIN and a.customerID=b.customerID and a.start_date=b.start_date
		LEFT JOIN Part AS c
		ON b.part_number=c.part_number) AS e

	GROUP BY VIN) AS b
ON a.VIN=b.VIN

LEFT JOIN Vehicle AS c

ON a.VIN=c.VIN
);
create view repair_manu AS (

SELECT a.manu_name, b.repair_manu, b.part_manu, b.labor_manu, b. total_manu

FROM Manufacturer AS a

LEFT JOIN

	(SELECT manu_name, sum(repair_count) as repair_manu, sum(total_labor_VIN) as labor_manu, sum(total_part_amount_VIN) as part_manu, sum(total_VIN) as total_manu
	FROM total_VIN_manu
	GROUP BY manu_name
	) AS b

ON a.manu_name=b.manu_name

ORDER BY a.manu_name ASC);
SELECT sum(repair_count) as repair_type, sum(total_labor_VIN) as labor_type, sum(total_part_amount_VIN) as part_type, sum(total_labor_VIN+total_part_amount_VIN) AS total_type, a.manu_name, c.type_name
FROM total_VIN_manu AS a
LEFT JOIN Vehicle AS b
ON a.VIN=b.VIN
LEFT JOIN VehicleType AS c
ON b.vehicleTypeID=c.vehicleTypeID
WHERE a.manu_name='$manu_name'
GROUP BY a.manu_name, b.vehicleTypeID
ORDER BY repair_type;
SELECT sum(repair_count) as repair_model, sum(total_labor_VIN) as labor_model, sum(total_part_amount_VIN) as part_model, sum(total_labor_VIN+total_part_amount_VIN) AS total_model, a.manu_name, c.type_name, a.model_name
FROM total_VIN_manu AS a
LEFT JOIN Vehicle AS b
ON a.VIN=b.VIN
LEFT JOIN VehicleType AS c
ON b.vehicleTypeID=c.vehicleTypeID
WHERE c.type_name='$type_name'
GROUP BY a.manu_name, b.vehicleTypeID, a.model_name
ORDER BY repair_model;
"""
DrilldownReport = """
SELECT p.VIN, s.username, SUM(p.sold_price) AS totalDollar, COUNT(*) AS totalCar
FROM Purchase AS p
LEFT JOIN Salesperson AS s
ON s.salesInputterID = p.salesInputterID
WHERE YEAR(p.purchase_date)=%s AND MONTH(p.purchase_date)=%s
GROUP BY p.salesInputterID
ORDER BY totalCar, totalDollar DESC;
"""