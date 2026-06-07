-- 1. Create a temporary table with new Vertex AI embeddings
-- Using existing model: email_embedding_model
CREATE OR REPLACE TABLE `grah-2026.fivetran_mongo_smart_email_manager.EmailData_Vertex_Migration` AS
SELECT 
  * EXCEPT(ml_generate_embedding_result, ml_generate_embedding_statistics, ml_generate_embedding_status),
  ml_embedding.ml_generate_embedding_result as ml_generate_embedding_result,
  ml_embedding.ml_generate_embedding_status as ml_generate_embedding_status
FROM ML.GENERATE_EMBEDDING(
  MODEL `grah-2026.mongo_sync_smart_email_manger.email_embedding_model`,
  (SELECT * EXCEPT(ml_generate_embedding_result, ml_generate_embedding_statistics, ml_generate_embedding_status) FROM `grah-2026.fivetran_mongo_smart_email_manager.v_live_emails_enriched`),
  STRUCT('RETRIEVAL_DOCUMENT' AS task_type, true AS flatten_json_output)
) as ml_embedding;

-- 2. Swap the tables
-- DROP TABLE `grah-2026.fivetran_mongo_smart_email_manager.EmailData_Enriched_Live`;
ALTER TABLE `grah-2026.fivetran_mongo_smart_email_manager.EmailData_Vertex_Migration` RENAME TO `EmailData_Enriched_Live`;
