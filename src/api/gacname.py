import cherrypy

from LmRex.tools.api import GbifAPI

# .............................................................................
@cherrypy.expose
class GAcName:
    
    # ...............................................
    def get_gbif_accepted_taxon(self, namestr, kingdom=None):
        rec = GbifAPI.parse_name(namestr)
        try:
            can_name = rec['canonicalName']
        except:
            # Default to original namestring if parsing fails
            can_name = namestr
        good_names = GbifAPI.match_name(can_name, status='accepted')
        if len(good_names) == 0:
            return {'spcoco.error': 
                    'No matching GBIF taxon records for {}'.format(namestr)}
        else:
            return good_names

    # ...............................................
    @cherrypy.tools.json_out()
    def GET(self, namestr=None):
        """Get a one GBIF accepted taxon record for a scientific name string
        
        Args:
            namestr: a scientific name
        Return:
            one dictionary containing a message or GBIF record corresponding 
            to the accepted name in the GBIF Backbone taxonomy
        """
        if namestr is None:
            return {'spcoco.message': 'S^n GBIF name resolution is online'}
        else:
            return self.get_gbif_accepted_taxon(namestr)

# .............................................................................
if __name__ == '__main__':
    cherrypy.tree.mount(
        GAcName(), '/api/gacname',
        {'/':
            {'request.dispatch': cherrypy.dispatch.MethodDispatcher()}
         }
    )

    cherrypy.engine.start()
    cherrypy.engine.block()

"""
test names:

Acer caesium Wall. ex Brandis
Acer heldreichii Orph. ex Boiss.
Acer pseudoplatanus L.
Acer velutinum Boiss.
Acer hyrcanum Fisch. & Meyer
Acer monspessulanum L.
Acer obtusifolium Sibthorp & Smith
Acer opalus Miller
Acer sempervirens L.
Acer floridanum (Chapm.) Pax
Acer grandidentatum Torr. & Gray
Acer leucoderme Small
Acer nigrum Michx.f.
Acer skutchii Rehder
Acer saccharum Marshall

bies pisapo var. mrocana (Trab.) Ceballos & Bolaño 1928
quercus berridifolia

"""