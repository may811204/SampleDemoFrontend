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