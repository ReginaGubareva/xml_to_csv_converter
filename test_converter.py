import re
import unittest

import pandas as pd

from xml_to_csv import PARSE_XML_PATH, CSV_FILE_PATH
from xml_to_csv import XmlCsvConverter


class TestConverter(unittest.TestCase):
    def setUp(self) -> None:
        self.converter = XmlCsvConverter()

    def test_request_to_url(self):
        print("tests_requests_to_url")
        self.assertEqual(self.converter.request_to_url().status_code, 200)

    def test_extract_zip(self):
        self.assertEqual(self.converter.extract_zip(), None)

    def test_get_download_link(self):
        self.assertEqual(self.converter.get_download_link(), "http://firds.esma.europa.eu/firds"
                                                             "/DLTINS_20210117_01of01.zip")

    def test_read_xml(self):
        tree = self.converter.read_xml(PARSE_XML_PATH)
        assert tree is not None

    def test_remove_namespace(self):
        tree = self.converter.read_xml(PARSE_XML_PATH)
        m = {}
        for element in tree.iter():
            m = re.match(r'\{.*}', element.tag)
        assert m is None

    def converter(self):
        df = pd.read_csv(CSV_FILE_PATH)
        self.assertEqual(df.columns.tolist(), ['FinInstrmGnlAttrbts.Id', 'FinInstrmGnlAttrbts.FullNm',
                                               'FinInstrmGnlAttrbts.ClssfctnTp', 'FinInstrmGnlAttrbts.CmmdtyDerivInd',
                                               'FinInstrmGnlAttrbts.NtnlCcy', 'Issr'])
        self.assertEqual(df.iloc[0].tolist(), ['DE000A1R07V3', 'Kreditanst.f.Wiederaufbau     Anl.v.2014 (2021)',
                                               'DBFTFB', 'False', 'EUR', '549300GDPG70E3MBBU98'])

        self.assertEqual(df.iloc[len(df) - 1].tolist(), ['DE000C42LZJ8', 'OEMB SI 20210115 PS AM P 112.50 0', 'OPAIPS',
                                                         'False', 'USD', '529900UT4DG0LG5R9O07'])
        self.assertEqual(df.iloc[(len(df) - 1) // 2].tolist(),
                         ['DE000MA2HM39', 'Call DAX emittiert von Morgan Stanley & '
                                          'Co. Int. plc', 'RWINCE', False, 'EUR',
                          '4PQUHN3JPFGFNF3BB653'])


if __name__ == "__main__":
    unittest.main()