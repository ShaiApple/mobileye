from lib.parsing.UniParser import UniParser
# from lib.parsing.recorders.dataRecorder import DataRecorder
from lib.parsing.recorders.csvRecorder import CsvRecorder
from recorder_per_frame import MadarRecorder
from lib.parsing.adapters.generalAdapter import GeneralAdapter
from lib.parsing.logstreams.text_log_stream import TextLogStream
from lib.parsing.adapters.searchInfo import *
import time
import os


script_path = os.path.abspath(os.path.dirname(__file__))


def adcam_mestp():
    space_after_sep = 1
    chars_per_byte = 3
    line_sep = ','
    data_values_sep = " "
    adapter_custom_cfg = None
    idAsInt = False
    dbc_file = [r'C:\MESTs\R1911_V1\2019_09_25_1722\dbc\Core_Calibration_Dynamic_protocol.dbc']
    log_file = r'C:\RobotFramework\Automation\pv_tests\adcam_low\[MESTP]_19-10-06_A320_R1911_V1_06102019_D_UR_CL_SPC'
    msg_info = [SearchInfo("0x63", "", ["*"])]
    data_temp_cfg = UniParser.MESTP_DATA_TEMPLATE
    adapter_cfg = {'line_sep': line_sep, 'data_template_cfg': data_temp_cfg, 'chars_per_byte': chars_per_byte,
                   'space_after_sep': space_after_sep, 'data_values_sep': data_values_sep,
                   'adapter_custom_cfg': adapter_custom_cfg}

    adapter = GeneralAdapter(adapter_cfg)
    reader = TextLogStream(file=log_file)
    # recorder = DataRecorder()
    # recorder = MadarRecorder()
    recorder = CsvRecorder(os.path.join(script_path, 'csv_log_for.csv'))
    upr = UniParser(adapter, reader, dbc_file, idAsInt)
    upr.read(msg_info, recorder)
    # custom_print_data(recorder)
    # recorder.print_data()


def main():
    _st = time.time()
    print "-------- start --------"
    adcam_mestp()

    print "--------- end ---------"
    print time.time() - _st


def custom_print_data(self):
    for msg_id in self.data:
        msg_data = self.data[msg_id]

        print "msg: ", msg_id

        for frame in msg_data.frames:
            for sig_data in msg_data.frames[frame]:
                print frame, ': ', sig_data


if __name__ == '__main__':
     main()

