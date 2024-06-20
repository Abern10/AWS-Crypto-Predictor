-- DROP TABLE IF EXISTS raw_data_bitcoin;
-- DROP TABLE IF EXISTS raw_data_ethereum;
-- DROP TABLE IF EXISTS processed_data_bitcoin;
-- DROP TABLE IF EXISTS processed_data_ethereum;
-- DROP TABLE IF EXISTS predictions_bitcoin;
-- DROP TABLE IF EXISTS predictions_ethereum;
-- DROP TABLE IF EXISTS past_predictions_bitcoin;
-- DROP TABLE IF EXISTS past_predictions_ethereum;

DELETE FROM predictions_bitcoin;
DELETE FROM predictions_ethereum;
DELETE FROM past_predictions_bitcoin;
DELETE FROM past_predictions_ethereum;

-- CREATE TABLE raw_data_bitcoin (
--     timestamp BIGINT PRIMARY KEY,
--     price FLOAT,
--     volume FLOAT,
--     market_cap FLOAT,
--     open FLOAT,
--     high FLOAT,
--     low FLOAT,
--     close FLOAT
-- );

-- CREATE TABLE raw_data_ethereum (
--     timestamp BIGINT PRIMARY KEY,
--     price FLOAT,
--     volume FLOAT,
--     market_cap FLOAT,
--     open FLOAT,
--     high FLOAT,
--     low FLOAT,
--     close FLOAT
-- );

-- CREATE TABLE processed_data_bitcoin (
--     timestamp_arima DATETIME PRIMARY KEY,
--     timestamp_ml BIGINT,
--     price FLOAT,
--     volume FLOAT,
--     market_cap FLOAT,
--     open FLOAT,
--     high FLOAT,
--     low FLOAT,
--     close FLOAT
-- );

-- CREATE TABLE processed_data_ethereum (
--     timestamp_arima DATETIME PRIMARY KEY,
--     timestamp_ml BIGINT,
--     price FLOAT,
--     volume FLOAT,
--     market_cap FLOAT,
--     open FLOAT,
--     high FLOAT,
--     low FLOAT,
--     close FLOAT
-- );

-- CREATE TABLE predictions_bitcoin (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     timestamp DATETIME,
--     predicted_price FLOAT
-- );

-- CREATE TABLE predictions_ethereum (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     timestamp DATETIME,
--     predicted_price FLOAT
-- );

-- CREATE TABLE past_predictions_bitcoin (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     timestamp DATETIME,
--     model_name VARCHAR(50),
--     predicted_price FLOAT,
--     actual_price FLOAT,
--     prediction_error FLOAT,
--     prediction_accuracy FLOAT
-- );

-- CREATE TABLE past_predictions_ethereum (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     timestamp DATETIME,
--     model_name VARCHAR(50),
--     predicted_price FLOAT,
--     actual_price FLOAT,
--     prediction_error FLOAT,
--     prediction_accuracy FLOAT
-- );