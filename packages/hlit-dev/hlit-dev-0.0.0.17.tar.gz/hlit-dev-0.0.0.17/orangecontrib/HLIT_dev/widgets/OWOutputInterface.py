import os
import sys
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
    from Orange.widgets.orangecontrib.HLIT_dev.remote_server_smb import server_uvicorn, convert
    from Orange.widgets.orangecontrib.AAIT.utils import MetManagement
else:
    from orangecontrib.AAIT.utils import thread_management
    from orangecontrib.AAIT.utils.import_uic import uic
    from orangecontrib.HLIT_dev.remote_server_smb import server_uvicorn,convert
    from orangecontrib.AAIT.utils import MetManagement

class OutputInterface(OWWidget):
    name = "Output Interface"
    description = "Convert pdf from a directory to docx using word"
    icon = "icons/output_interface.png"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
         icon = "icons_dev/output_interface.png"
    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/output_interface.ui")
    priority = 3000

    workflow_id = Setting("")
    help_description = Setting("")
    class Inputs:
        data = Input("Data", Table)

    @Inputs.data
    def set_data(self, in_data):
        self.data = in_data
        self.run()

    def __init__(self):
        super().__init__()
        self.data = None
        # Qt Management
        self.setFixedWidth(700)
        self.setFixedHeight(200)
        uic.loadUi(self.gui, self)

        self.workflow_id_input = self.findChild(QLineEdit, 'WorkflowId')
        self.workflow_id_input.setPlaceholderText("Workflow ID")
        self.workflow_id_input.setText(self.workflow_id)
        self.workflow_id_input.editingFinished.connect(self.update_settings)


        self.description_input = self.findChild(QLineEdit, 'Description')
        self.description_input.setText(self.help_description)
        self.description_input.editingFinished.connect(self.update_settings)


    def update_settings(self):
        self.workflow_id = self.workflow_id_input.text()
        self.help_description = self.description_input.text()
        self.run()

    def run(self):
        self.error("")
        self.warning("")
        if self.workflow_id == "":
            self.warning("Workflow ID manquant(s).")
            return

        path_file = MetManagement.get_api_local_folder(workflow_id=self.workflow_id)
        # Execution of the workflow
        if not os.path.exists(path_file + "config.json"):
            self.information("Le fichier 'config.json' n'existe pas encore en attente de données du serveur.")
            return

        with open(path_file + "config.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        if self.workflow_id != data["workflow_id"]:
            self.error("Le workflow id ne correspond pas avec votre configuration.")
            return

        json_output = convert.convert_data_table_to_json(self.data)
        if json_output == 1:
            return

        with open(path_file + "output.json", "w", encoding="utf-8") as file_out:
            json.dump(json_output, file_out, indent=4, ensure_ascii=False)

        with open(path_file + ".out_ok", "w") as fichier:
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_widget = OutputInterface()
    my_widget.show()
    app.exec_()
