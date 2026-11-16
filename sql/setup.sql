CREATE DATABASE IF NOT EXISTS road_accident_db;
USE road_accident_db;

CREATE TABLE IF NOT EXISTS accident_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    accident_date DATE,
    city VARCHAR(100),
    severity VARCHAR(50),
    weather VARCHAR(100),
    road_type VARCHAR(100),
    cause VARCHAR(255),
    accident_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SELECT * from accident_records;
