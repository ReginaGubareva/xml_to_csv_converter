import csv
import io
import logging.config
import xml.etree.ElementTree as ET
import zipfile

import requests

from logging_config import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


###############################################################################
# SERVICE LOCATIONS
###############################################################################
FILES_PATH = 'external_files'
MAIN_XML_PATH = f'{FILES_PATH}/main.xml'
PARSE_XML_PATH = f'{FILES_PATH}/DLTINS_20210117_01of01.xml'
CSV_FILE_PATH = f'{FILES_PATH}/DLTINS_20210117_01of01.csv'
CSV_FILE_HEADERS = ["FinInstrmGnlAttrbts.Id",
                    "FinInstrmGnlAttrbts.FullNm",
                    "FinInstrmGnlAttrbts.ClssfctnTp",
                    "FinInstrmGnlAttrbts.CmmdtyDerivInd",
                    "FinInstrmGnlAttrbts.NtnlCcy",
                    "Issr"]


class XmlCsvConverter:
    def xml_to_csv(self):
        """
        Parse xml and convert it to csv
        """
        logger.info("Start convertion xml to csv:")
        self.extract_zip()
        csv_file = self.get_csv_file()
        csvfile_writer = csv.writer(csv_file)
        csvfile_writer.writerow(CSV_FILE_HEADERS)

        tree = self.read_xml(PARSE_XML_PATH)
        root = tree.getroot()
        doc = root.find('Pyld/Document')

        path = f"FinInstrmRptgRefDataDltaRpt/FinInstrm/TermntdRcrd/"
        FinInstrmGnlAttrbts = doc.findall(f"{path}FinInstrmGnlAttrbts")
        Issr = doc.findall(f"{path}Issr")

        if not FinInstrmGnlAttrbts and not Issr:
            logger.info("The error in parsing FinInstrmGnlAttrbts and Issr, they are empty")
        else:
            logger.info("The xml parsing has started")
            for el, issr in zip(FinInstrmGnlAttrbts, Issr):
                Id = el.find(f"Id").text
                FullNm = el.find(f"FullNm").text
                ClssfctnTp = el.find(f"ClssfctnTp").text
                CmmdtyDerivInd = el.find(f"CmmdtyDerivInd").text
                NtnlCcy = el.find(f"NtnlCcy").text
                csvfile_writer.writerow([Id, FullNm, ClssfctnTp, CmmdtyDerivInd, NtnlCcy, issr.text])
            csv_file.close()
            logger.info("CSV file has been created")

    def get_csv_file(self):
        """
        Open csv file to write and write header
        :return: csvfile_writer
        """
        try:
            csvfile = open(CSV_FILE_PATH, 'w', encoding='utf-8', newline='')
            logger.info("CSV file is opened successfully")
            return csvfile
        except IOError:
            logger.error("Didn't manage to open csv file. Something went wrong.")

    def remove_namespace(self, tree):
        """
        Strip namespace from parsed XML
        """
        for node in tree.iter():
            try:
                has_namespace = node.tag.startswith("{")
            except AttributeError:
                continue  # node.tag is not a string (node is a comment or similar)
            if has_namespace:
                node.tag = node.tag.split("}", 1)[1]

    def read_xml(self, path) -> ET.ElementTree:
        """
        Parse tree from given XML path
        """
        try:
            tree = ET.parse(path)
            logger.info("The xml was readed successfully.")
            self.remove_namespace(tree)  # strip namespace when reading an XML file
        except:
            try:
                tree = ET.fromstring(path)
            except Exception:
                logger.error(
                    "Can't open xml file. It was not able to read a path, a file-like object, "
                    "or a string as an XML"
                )
                raise

        return tree

    def get_download_link(self) -> str:
        """
        Parse external_files/main.xml file to get download link for the DLTINS.xml
        :return: download_link
        """
        tree = self.read_xml(MAIN_XML_PATH)
        root = tree.getroot()
        download_link = root.findall("result/doc/str[2]")[0].text
        logger.info(download_link)
        return download_link


    def extract_zip(self):
        """
        Download zip file with download link, extract all files to external_files.
        """
        r = self.request_to_url()
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            if z.testzip() is not None:
                logger.error("Bad zip file")
            z.extractall(FILES_PATH)
            logger.info("ZIP file was successfully downloaded and extracted.")
            return z.testzip()

    def request_to_url(self) -> requests.Response:
        """
        Get http request by the download link.
        :return: r - request result
        """
        try:
            r = requests.get(self.get_download_link(), timeout=3)
            r.raise_for_status()
            logger.info("Http request is done")
            return r
        except requests.exceptions.HTTPError as errh:
            logger.error("Http Error - ", errh)
        except requests.exceptions.ConnectionError as errc:
            logger.error("Connection Error - ", errc)
        except requests.exceptions.Timeout as errt:
            logger.error("Timeout Error - ", errt)
        except requests.exceptions.RequestException as err:
            logger.error(err)
