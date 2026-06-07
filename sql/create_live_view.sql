CREATE OR REPLACE VIEW `grah-2026.fivetran_mongo_smart_email_manager.v_live_emails_enriched` AS
SELECT 
  _id as mongo_id,
  JSON_VALUE(data.message_id) as message_id,
  JSON_VALUE(data.subject) as subject,
  JSON_VALUE(data.sender) as sender,
  JSON_VALUE(data.user_email) as user_email,
  JSON_VALUE(data.snippet) as content,
  JSON_VALUE(data.label) as label,
  JSON_VALUE(data.arrival_at) as arrival_at,
  JSON_VALUE(data.processed_at) as processed_at,
  -- Extract the existing Vertex Embedding if SEM Dual-Write has already sent it
  JSON_EXTRACT_ARRAY(data.vertex_embedding) as ml_generate_embedding_result
FROM `grah-2026.fivetran_mongo_smart_email_manager.email_data`
WHERE _fivetran_deleted IS FALSE;
