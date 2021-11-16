<<<<<<< HEAD
from lmtrex.common.lmconstants import (APIService)
from lmtrex.frontend.templates import stats_template
from lmtrex.flask_app.broker.base import _S2nService


# .............................................................................
=======
import cherrypy

from lmtrex.common.lmconstants import (APIService)
from lmtrex.frontend.templates import stats_template
from lmtrex.services.api.v1.base import _S2nService


# .............................................................................
@cherrypy.expose
>>>>>>> bugfix - call from instance not class
class StatsSvc(_S2nService):
    SERVICE_TYPE = APIService.Stats

    # ...............................................
    # ...............................................
<<<<<<< HEAD
    @classmethod
    def get_stats(self, **params):
=======
    def GET(self, **params):
>>>>>>> bugfix - call from instance not class
        """Institution and collection level stats

        Return:
            HTML page that fetches and formats stats
        """
<<<<<<< HEAD
=======


>>>>>>> bugfix - call from instance not class
        return stats_template()
