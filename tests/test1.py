import unittest
import scanning as sc
from utils import write_json, read_json



class TestScenarios(unittest.TestCase):

    def setUp(self):
        self.new_data = read_json("test_data_dict.json")
        self.org_list = read_json("test_org_list.json")
        self.file_path = "test_last_data_juguete.json"
        self.missing_path = "test_missing_data.json"

    def test_scan_updates(self):
        """En test_last_data_juguete hay 3 datasets menos, pero dos de estos nuevos
        están en test_missing_data así que scan_updates sólo debería detectar uno"""

        updates = sc.scan_updates(
            self.new_data,
            self.org_list,
            self.file_path,
            self.missing_path,
            "url"
        )
        self.assertEqual(len(updates), 1)

    def test_scan_organizations(self):
        org_updates = sc.scan_organizations(self.org_list, self.file_path)
        new_org_names = [org["name"] for org in org_updates if org.get("new") is True]
        self.assertEqual(new_org_names, ["energia"])


if __name__ == "__main__":
    unittest.main()





