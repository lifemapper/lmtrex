Occurrence Broker results
-----------------------------

specify_cache 
~~~~~~~~~~~~~~~~~~

* Implemented in solr, collection is specimen_records
* Schema is in lmysft/solr_cores/specimen_records/conf/schema.xml
* Go to development or production machine (currently Syftorium, notyeti-195 and joe-125) and query solr directly
  ::
  
  curl http://localhost:8983/solr/specimen_records/select?q=identifier:2c1becd5-e641-4e83-b3f5-76a55206539a

Consider fields in S2nSchema

Consider fields in specify_cache and exported from Sp 6 and 7
