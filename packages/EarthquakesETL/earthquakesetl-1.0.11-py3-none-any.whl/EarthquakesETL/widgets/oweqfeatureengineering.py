from dataclasses import dataclass
from typing import Any, Container, Optional

from Orange.data.pandas_compat import table_to_frame
from Orange.widgets.data.owsql import TableModel
from Orange.widgets.data.utils.models import RichTableModel, TableSliceProxy
from Orange.widgets.data.utils.tableview import RichTableView
from Orange.widgets.widget import Input
import Orange.data.pandas_compat as pc

import Orange
from Orange.widgets import widget
from Orange.widgets.widget import OWWidget
from Orange.widgets.utils.concurrent import ConcurrentWidgetMixin
from Orange.widgets import gui
from Orange.widgets.widget import Output, Msg
from PyQt5.QtCore import QModelIndex, QSize, QDate
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy, QHeaderView, QStyle, QDateEdit

from EarthquakesETL.eqmodel.EQPgen import EQPgen

from EarthquakesETL.widgets.oweqcatalogdeclustering import SubsetRole

import pandas as pd
from PyQt5.QtCore import Qt


@dataclass
class OutputData:
    table: pd.DataFrame
    model: TableModel

class _TableModel(RichTableModel):
    SubsetRole = SubsetRole

    def __init__(self, *args, subsets=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._subset = subsets or set()

    def setSubsetRowIds(self, subsetids: Container[int]):
        self._subset = subsetids
        if self.rowCount():
            self.headerDataChanged.emit(Qt.Vertical, 0, self.rowCount() - 1)
            self.dataChanged.emit(
                self.index(0, 0),
                self.index(self.rowCount() - 1, self.columnCount() - 1),
                [SubsetRole],
            )

    def _is_subset(self, row):
        row = self.mapToSourceRows(row)
        try:
            id_ = self.source.ids[row]
        except (IndexError, AttributeError):
            return False
        return int(id_) in self._subset

    def data(self, index: QModelIndex, role=Qt.DisplayRole) -> Any:
        if role == _TableModel.SubsetRole:
            return self._is_subset(index.row())
        return super().data(index, role)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Vertical and role == _TableModel.SubsetRole:
            return self._is_subset(section)
        return super().headerData(section, orientation, role)

class DataTableView(gui.HScrollStepMixin, RichTableView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        vheader = QHeaderView(Qt.Vertical, self)
        vheader.setSectionsClickable(True)
        self.setVerticalHeader(vheader)


class oweqfeatureengineering(OWWidget, ConcurrentWidgetMixin):
    name = "EQ Feature Engineering"
    description = "Generate earthquake-related attributes from seismic events data."
    icon = "icons/EQFeatureEngineering.png"
    priority = 2250

    UserAdviceMessages = [
        widget.Message(
            "Hovering over the parameters displays their descriptions."
            " You can use the Help button for more information.",
            "click_cell"
        )
    ]

    class Inputs:
        data = Orange.widgets.widget.Input("Catalog", Orange.data.Table)

    class Outputs:
        data_output = Output("Dataset", Orange.data.Table)
        configuration_table = Output("Dataset Configuration Table", Orange.data.Table)

    class Error(OWWidget.Error):
        no_input = Msg("No data input provided. Please connect a data source.")

    def __init__(self):
        super().__init__()
        ConcurrentWidgetMixin.__init__(self)
        self.data = None
        self.data_output = None

        self.output: Optional[OutputData] = None

        self.Information.clear()
        self.Information.add_message("click_cell", self.UserAdviceMessages[0].text)

        self.eqpgen = EQPgen()

        self.nMorales = 10
        self.nAdeli = 1
        self.referenceMagnitude = 3.0
        self.dayspred = 6
        self.classFrom = 2.0
        self.classTo = 5.0
        self.classStep = 0.05
        self.chth = 0.01
        self.attYorch_bM = True
        self.attYorch_bA = False
        self.attAdeli_bM = False
        self.attAdeli_bA = False
        self.outputType = ""

        self.controlArea.layout().setAlignment(Qt.AlignTop)

        box_time = gui.widgetBox(self.controlArea, "Period of time")
        self.timeFrom = QDateEdit(self)
        self.timeTo = QDateEdit(self)
        self.timeFrom.setCalendarPopup(True)
        self.timeTo.setCalendarPopup(True)
        gui.widgetLabel(box_time, "Start Date:")
        box_time.layout().addWidget(self.timeFrom)
        gui.widgetLabel(box_time, "End Date:")
        box_time.layout().addWidget(self.timeTo)
        self.timeFrom.setDisplayFormat("dd/MM/yyyy")
        self.timeTo.setDisplayFormat("dd/MM/yyyy")

        params_box = gui.widgetBox(self.controlArea, "Configuration Parameters")

        self.nMorales_spin = gui.spin(params_box, self, "nMorales", 1, 1000, step=1, label="Events for b-value Morales")
        self.nMorales_spin.box.setToolTip("Number of events used to calculate the b-value using Morales' method.")
        params_box.layout().addWidget(self.nMorales_spin)
        self.nAdeli_spin = gui.spin(params_box, self, "nAdeli", 1, 1000, step=1, label="Events for b-value Adeli")
        self.nAdeli_spin.box.setToolTip("Number of previous seismic events considered for the calculation of the b-value using Adeli's method.")
        params_box.layout().addWidget(self.nAdeli_spin)
        self.referenceMagnitude_spin = gui.doubleSpin(params_box, self, "referenceMagnitude", 1.0, 9.0, step=0.1, label="Reference Magnitude")
        self.referenceMagnitude_spin.box.setToolTip("Reference magnitude used in the calculation of the b-value. Affects how seismic activity is quantified.")
        params_box.layout().addWidget(self.referenceMagnitude_spin)
        self.dayspred_spin = gui.spin(params_box, self, "dayspred", 1, 1000, step=1, label="Prediction Days")
        self.dayspred_spin.box.setToolTip("Number of future days considered for earthquake prediction. A longer period may reduce precision.")
        params_box.layout().addWidget(self.dayspred_spin)
        self.classFrom_spin = gui.doubleSpin(params_box, self, "classFrom", 1.0, 9.0, step=0.1, label="Classification: From")
        self.classFrom_spin.box.setToolTip("Minimum earthquake magnitude considered for discrete classification.")
        params_box.layout().addWidget(self.classFrom_spin)
        self.classTo_spin = gui.doubleSpin(params_box, self, "classTo", 1.0, 9.0, step=0.1, label="Classification: To")
        self.classTo_spin.box.setToolTip("Maximum earthquake magnitude considered for discrete classification.")
        params_box.layout().addWidget(self.classTo_spin)
        self.classStep_spin = gui.doubleSpin(params_box, self, "classStep", 0.01, 9.0, step=0.05, label="Classification: Step")
        self.classStep_spin.box.setToolTip("Step size for defining magnitude classes. Smaller values increase granularity.")
        params_box.layout().addWidget(self.classStep_spin)
        self.chth_spin = gui.doubleSpin(params_box, self, "chth", 0.01, 9.0, step=0.01, label="Threshold for mu and c")
        self.chth_spin.box.setToolTip("Characteristic threshold for mu and c attributes, affecting event clustering and variability assessment.")
        params_box.layout().addWidget(self.chth_spin)
        gui.widgetLabel(params_box, "Attribute Sets:")
        self.attYorch_bM_checkbox = gui.checkBox(params_box, self, "attYorch_bM", label="attYorch/bM")
        self.attYorch_bA_checkbox = gui.checkBox(params_box, self, "attYorch_bA", label="attYorch/bA")
        self.attAdeli_bM_checkbox = gui.checkBox(params_box, self, "attAdeli_bM", label="attAdeli/bM")
        self.attAdeli_bA_checkbox = gui.checkBox(params_box, self, "attAdeli_bA", label="attAdeli/bA")
        params_box.layout().addWidget(self.attYorch_bM_checkbox)
        params_box.layout().addWidget(self.attYorch_bA_checkbox)
        params_box.layout().addWidget(self.attAdeli_bM_checkbox)
        params_box.layout().addWidget(self.attAdeli_bA_checkbox)

        actions_box = gui.widgetBox(self.controlArea, "Actions")
        self.generatebutton = gui.button(actions_box, self, "Generate Attributes", callback=self.process)

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.controlArea.layout().addItem(spacer)

        box_output = gui.widgetBox(self.mainArea, "New attributes")
        view_output = DataTableView(sortingEnabled=True)

        header = view_output.horizontalHeader()
        header.setSectionsMovable(True)
        header.setSectionsClickable(True)
        header.setSortIndicatorShown(True)
        header.setSortIndicator(-1, Qt.AscendingOrder)

        self.view_output = view_output
        box_output.layout().addWidget(self.view_output)

    def _setup_table_view(self):
        """Setup the view with current input data."""
        if self.output is None:
            self.view_output.setModel(None)
            return

        datamodel = self.output.model
        datamodel.setSubsetRowIds(set())

        view = self.view_output
        data = self.output.table
        rowcount = data.approx_len()
        view.setModel(datamodel)

        vheader = view.verticalHeader()
        option = view.viewOptions()
        size = view.style().sizeFromContents(
            QStyle.CT_ItemViewItem, option,
            QSize(20, 20), view)

        vheader.setDefaultSectionSize(size.height() + 2)
        vheader.setMinimumSectionSize(5)
        vheader.setSectionResizeMode(QHeaderView.Fixed)

        maxrows = (2 ** 31 - 1) // (vheader.defaultSectionSize() + 2)
        if rowcount > maxrows:
            sliceproxy = TableSliceProxy(
                parent=view, rowSlice=slice(0, maxrows))
            sliceproxy.setSourceModel(datamodel)
            view.setModel(None)
            view.setModel(sliceproxy)

        assert view.model().rowCount() <= maxrows
        assert vheader.sectionSize(0) > 1 or datamodel.rowCount() == 0

    @Inputs.data
    def set_data(self, data=None):
        """Recibe la data de entrada y configura los QDateEdit según el rango de fechas."""
        self.data = data

        if data is not None:
            df = table_to_frame(data)

            if 'index' in df.columns:
                df = pd.DataFrame(df.drop('index', axis=1))

            min_datetime = df["time"].min()
            max_datetime = df["time"].max()
            qmin_date = QDate(min_datetime.year, min_datetime.month, min_datetime.day)
            qmax_date = QDate(max_datetime.year, max_datetime.month, max_datetime.day)
            # Configurar los QDateEdit para limitar la selección al rango de fechas del catálogo
            self.timeFrom.setMinimumDate(qmin_date)
            self.timeFrom.setDate(qmin_date)
            self.timeTo.setMaximumDate(qmax_date)
            self.timeTo.setDate(qmax_date)

        self.Outputs.data_output.send(None)

    def configurations_table(self):
        selected_options = []
        if self.attYorch_bM:
            selected_options.append("attYorch/bM")
        if self.attYorch_bA:
            selected_options.append("attYorch/bA")
        if self.attAdeli_bM:
            selected_options.append("attAdeli/bM")
        if self.attAdeli_bA:
            selected_options.append("attAdeli/bA")
        outputtype = ", ".join(selected_options)

        config = {
            "Start Date": self.timeFrom.date().toString(Qt.ISODate),
            "End Date": self.timeTo.date().toString(Qt.ISODate),
            "Events for b-value Morales": self.nMorales,
            "Events for b-value Adeli": self.nAdeli,
            "Reference Magnitude": self.referenceMagnitude,
            "Prediction Days": self.dayspred,
            "Classification From": self.classFrom,
            "Classification To": self.classTo,
            "Classification Step": self.classStep,
            "Threshold (mu and c)": self.chth,
            "Output Type": outputtype
        }

        df = pd.DataFrame([config])

        out_configurations = pc.table_from_frame(df)

        self.Outputs.configuration_table.send(out_configurations)

    def process(self):
        self.generatebutton.setEnabled(False)

        if self.data is None:
            self.Error.no_input()
            return

        self.eqpgen.timeFrom = self.timeFrom
        self.eqpgen.timeTo = self.timeTo
        self.eqpgen.nMorales = self.nMorales
        self.eqpgen.nAdeli = self.nAdeli
        self.eqpgen.referenceMagnitude = self.referenceMagnitude
        self.eqpgen.dayspred = self.dayspred
        self.eqpgen.classFrom = self.classFrom
        self.eqpgen.classTo = self.classTo
        self.eqpgen.classStep = self.classStep
        self.eqpgen.chth = self.chth

        selected_options = []
        if self.attYorch_bM:
            selected_options.append("attYorch/bM")
        if self.attYorch_bA:
            selected_options.append("attYorch/bA")
        if self.attAdeli_bM:
            selected_options.append("attAdeli/bM")
        if self.attAdeli_bA:
            selected_options.append("attAdeli/bA")
        self.eqpgen.outputType = ",".join(selected_options)

        df = table_to_frame(self.data)

        self.progressBarInit()
        self.eqpgen.progress_callback = self.progressBarSet

        processed_data = self.eqpgen.run(df)

        numeric_cols = [c for c in processed_data.columns
                        if c not in ('time', 'event')]
        processed_data[numeric_cols] = processed_data[numeric_cols].astype(float)

        processed_data['event'] = processed_data['event'].astype(int)

        self.progressBarFinished()

        output_data = pc.table_from_frame(processed_data)

        self.Outputs.data_output.send(output_data)

        self.output = OutputData(
            table=output_data,
            model=_TableModel(output_data)
        )

        self._setup_table_view()
        self.configurations_table()

        self.generatebutton.setEnabled(True)