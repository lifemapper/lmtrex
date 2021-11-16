<<<<<<< HEAD
<<<<<<< HEAD
from lmtrex.common.lmconstants import (APIService)
from lmtrex.frontend.templates import stats_template
from lmtrex.flask_app.broker.base import _S2nService


# .............................................................................
=======
import cherrypy

=======
>>>>>>> converted more APIs to Flask; other APIs unfinished
from lmtrex.common.lmconstants import (APIService)
from lmtrex.frontend.templates import stats_template
from lmtrex.flask_app.broker.base import _S2nService


# .............................................................................
<<<<<<< HEAD
@cherrypy.expose
>>>>>>> bugfix - call from instance not class
=======
>>>>>>> converted more APIs to Flask; other APIs unfinished
class StatsSvc(_S2nService):
    SERVICE_TYPE = APIService.Stats

    # ...............................................
    # ...............................................
<<<<<<< HEAD
<<<<<<< HEAD
    @classmethod
    def get_stats(self, **params):
=======
    def GET(self, **params):
>>>>>>> bugfix - call from instance not class
=======
    @classmethod
    def get_stats(self, **params):
>>>>>>> converted more APIs to Flask; other APIs unfinished
        """Institution and collection level stats

        Return:
            HTML page that fetches and formats stats
        """
<<<<<<< HEAD
<<<<<<< HEAD
=======


>>>>>>> bugfix - call from instance not class
=======
>>>>>>> converted more APIs to Flask; other APIs unfinished
        return stats_template()
