
  SELECT 
    d.mmsi, 
    d.time, 
    d.longitude,
    d.latitude,
    d.cog, 
    d.sog
  FROM ais_{}_dynamic AS d
  WHERE
