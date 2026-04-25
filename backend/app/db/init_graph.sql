CREATE EXTENSION IF NOT EXISTS age;
SET search_path = ag_catalog, "$user", public;
SELECT create_graph('indus_production');
ALTER USER postgres SET search_path = ag_catalog, "$user", public;
