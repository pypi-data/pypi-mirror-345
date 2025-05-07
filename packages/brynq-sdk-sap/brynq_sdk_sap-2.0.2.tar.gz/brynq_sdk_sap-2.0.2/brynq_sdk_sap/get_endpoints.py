from .base_functions import BaseFunctions
import requests
import pandas as pd


class GetEndpoints:

    def __init__(self, label: str, data_dir: str, certificate_file: str = None, key_file: str = None, debug: bool = False):
        self.base_class = BaseFunctions(label=label, data_dir=data_dir, certificate_file=certificate_file, key_file=key_file, debug=debug)
        self.data_dir = data_dir
        self.debug = debug

    def get_batch_data(self, uri: str, filter: str, id_key: str, id_list: list, batch_size: int = 10, xml_root: str = None, breaking_on_error: bool = False):
        """
        In some cases you want to get a lot of data from the endpoint. This function will combine a lot of calls for you into one dataframe
        SAP is not able to do this itself.
        :param uri: The URI you want to get the data from
        :param filter: The filter you want to use to filter the data on
        :param id_key: The key for all the ID's you want to get the data from. i.e. 'employee_id'
        :param id_list: A list of all the ID's you want to get the data from. i.e. ['123456', '654321']
        :param batch_size: the number of ID's you want to get the data from in one call. by default 10
        :param xml_root: the response from SAP comes within XML format. Give the root of the XML file from which you want to get the data
        :return: a Pandas dataframe with the data from the endpoint
        """
        # Put all the given ID's in one list
        id_batches = [id_list[i:i + batch_size] for i in range(0, len(id_list), batch_size)]
        df = pd.DataFrame()
        counter = 0
        for i, id_batch in enumerate(id_batches):
            # Creat the filter for each batch
            temp_filter = ''
            for id in id_batch:
                temp_filter += f"{id_key} eq '{id}' or "
            final_filter = f"({temp_filter[:-4]}) and {filter}"

            # Now call the simple get_data endpoint
            try:
                df_tmp = self.base_class.get_data(uri=uri, xml_root=xml_root, filter=final_filter)
                df = pd.concat([df, df_tmp], axis=0)
                df.reset_index(drop=True, inplace=True)

                counter += batch_size
                print(f'Processed {counter} records from {len(id_list)}')
            except Exception as e:
                if breaking_on_error:
                    raise Exception(f"Error getting data from SAP in batch {i}: {e}")
                else:
                    print(f"Error getting data from SAP in batch {i}: {e}")
                    continue
        return df
