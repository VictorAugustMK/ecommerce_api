
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'lu_estilos'
  AND pid <> pg_backend_pid();

DROP DATABASE IF EXISTS 'lu_estilos';
CREATE DATABASE 'lu_estilos';
