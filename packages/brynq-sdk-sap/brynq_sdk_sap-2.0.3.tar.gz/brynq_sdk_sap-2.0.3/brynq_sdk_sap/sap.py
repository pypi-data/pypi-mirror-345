from .base_functions import BaseFunctions
from .get_endpoints import GetEndpoints
from .delimit_endpoints import DelimitEndpoints
from .post_endpoints import PostEndpoints


class SAP(BaseFunctions, GetEndpoints, PostEndpoints, DelimitEndpoints):
    def __init__(self, label: str, data_dir: str, certificate_file: str = None, key_file: str = None, debug: bool = False):
        """
        Inherit all the child classes into this one class. Users can now use all the functions from the child classes just by initializing this class.
        :param label: The label of the SAP connection in SalureConnect
        :param data_dir: The directory where the data will be stored. Needed for pandas to read the XML file
        :param certificate_file: The certificate file: open(file, 'rb')
        :param key_file: The key file in bytes format: open(file, 'rb')
        """
        BaseFunctions.__init__(self, label, data_dir, certificate_file, key_file, debug)
        GetEndpoints.__init__(self, label, data_dir, certificate_file, key_file, debug)
        PostEndpoints.__init__(self, label, data_dir, certificate_file, key_file, debug)
        DelimitEndpoints.__init__(self, label, data_dir, certificate_file, key_file, debug)

