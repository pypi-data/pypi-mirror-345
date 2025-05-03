import os
import sys
import socket
import time
import json
import Orange
from Orange.widgets.widget import OWWidget, Input, Output
from Orange.widgets.settings import Setting
from Orange.widgets import gui
from AnyQt.QtWidgets import QLineEdit, QFileDialog,QApplication
from Orange.data import Table, Domain, StringVariable, ContinuousVariable


if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.utils import thread_management
    from Orange.widgets.orangecontrib.AAIT.utils.import_uic import uic
    from Orange.widgets.orangecontrib.HLIT_dev.remote_server_smb import server_uvicorn
    from Orange.widgets.orangecontrib.AAIT.utils import MetManagement
else:
    from orangecontrib.AAIT.utils import thread_management
    from orangecontrib.AAIT.utils.import_uic import uic
    from orangecontrib.HLIT_dev.remote_server_smb import server_uvicorn
    from orangecontrib.AAIT.utils import MetManagement

class InputInterface(OWWidget):
    name = "Input Interface"
    description = "Send data to a local interface"
    icon = "icons/input_interface.png"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/input_interface.png"
    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/input_interface.ui")
    priority = 3000
    input_id = Setting("")
    workflow_id = Setting("")
    help_description = Setting("")

    class Outputs:
        data = Output("Data", Orange.data.Table)

    def __init__(self):
        super().__init__()
        self.data = None
        # Qt Management
        self.setFixedWidth(700)
        self.setFixedHeight(300)
        uic.loadUi(self.gui, self)
        #self.input_id_input = QLineEdit(self)
        self.input_id_input = self.findChild(QLineEdit, 'InputId')
        self.input_id_input.setPlaceholderText("Input Id")
        self.input_id_input.setText(self.input_id)
        self.input_id_input.editingFinished.connect(self.update_settings)
        #gui.widgetBox(self.controlArea, orientation='vertical').layout().addWidget(self.input_id_input)

        #self.workflow_id_input = QLineEdit(self)
        self.workflow_id_input = self.findChild(QLineEdit, 'WorkflowId')
        self.workflow_id_input.setPlaceholderText("Workflow ID")
        self.workflow_id_input.setText(self.workflow_id)
        self.workflow_id_input.editingFinished.connect(self.update_settings)
        #gui.widgetBox(self.controlArea, orientation='vertical').layout().addWidget(self.workflow_id_input)

        self.description_input = self.findChild(QLineEdit, 'Description')
        self.description_input.setText(self.help_description)
        self.description_input.editingFinished.connect(self.update_settings)

        self.thread = None
        self.run()

    def update_settings(self):
        self.input_id = self.input_id_input.text()
        self.workflow_id = self.workflow_id_input.text()
        self.help_description = self.description_input.text()
        if self.workflow_id != "" and self.input_id != "":
            if self.thread is None:
                self.run()


    def check_file_exists(self, path):
        while not os.path.exists(path +".ok") or not os.path.exists(path + "input_data_" + self.input_id + ".tab"):
            time.sleep(1)

    def execute(self):
        path_file = MetManagement.get_api_local_folder(workflow_id=self.workflow_id)
        self.check_file_exists(path_file)
        # Execution of the workflow
        if not os.path.exists(path_file + "config.json"):
            self.error("Le fichier 'config.json' n'existe pas.")
            return

        with open(path_file + "config.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        data_table_path = ""
        if self.workflow_id == data["workflow_id"]:
            for input in data["data_config"]:
                if self.input_id == str(input["num_input"]):
                    data_table_path = input["path"]

        if data_table_path == "" or not os.path.exists(path_file + data_table_path):
            #self.information("Le fichier input n'existe pas.")
            return

        out_data = Orange.data.Table(path_file + data_table_path)
        #suppression du fichier d'entrée après utilisation
        MetManagement.reset_files([path_file + data_table_path])
        return out_data

    def run(self):
        self.error("")
        self.warning("")

        # if thread is running quit
        if self.thread is not None:
            self.thread.safe_quit()

        if self.workflow_id == "" or self.input_id == "":
            self.warning("Workflow ID et/ou Input ID manquant(s).")
            return

        self.thread = thread_management.Thread(self.execute)
        self.thread.result.connect(self.handle_result)
        self.thread.finished.connect(self.run)
        self.thread.start()

    def handle_result(self, result):
        if result is None:
            self.error("error out data is None")
            return
        self.error("")
        try:
            out_data = Orange.data.Table(result)
            self.Outputs.data.send(out_data)
        except Exception as e:
            print("An error occurred when sending out_data:", e)
            self.Outputs.data.send(None)
            return

if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_widget = InputInterface()
    my_widget.show()
    app.exec_()
