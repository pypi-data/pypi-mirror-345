import Orange
import Orange.data.pandas_compat as pc
import pandas as pd
from Orange.data import Table
from Orange.widgets.widget import OWWidget, Output, Msg
from Orange.widgets import gui
from AnyQt.QtWidgets import (QHeaderView, QStyle)
from Orange.widgets.data.utils.models import RichTableModel, TableSliceProxy
from Orange.widgets.data.utils.tableview import RichTableView
from Orange.widgets.utils.itemmodels import TableModel
from AnyQt.QtCore import (Qt, QSize, QModelIndex)
from PyQt5.QtWidgets import QLabel, QComboBox, QVBoxLayout, QLineEdit, QSpacerItem, QSizePolicy
from orangewidget.gui import OrangeUserRole
from dataclasses import dataclass
from typing import (Optional, Any, Container)
import numpy as np

from openquake.hmtk.seismicity.catalogue import Catalogue
from openquake.hmtk.seismicity.declusterer.dec_gardner_knopoff import GardnerKnopoffType1
from openquake.hmtk.seismicity.declusterer.distance_time_windows import (GardnerKnopoffWindow)

SubsetRole = next(OrangeUserRole)

@dataclass
class OutputData:
    table: Table
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
        except (IndexError, AttributeError):  # pragma: no cover
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

class oweqcatalogdeclustering(OWWidget):
    name = "EQ Catalog Declustering"
    description = "Cleans earthquake data"
    icon = "icons/EQCatalogCleaning.png"
    keywords = "earthquakes, cleaning, declustering"
    priority = 2250

    class Inputs:
        data = Orange.widgets.widget.Input("Catalog", Orange.data.Table)

    class Outputs:
        cleaned_data = Output("Cleaned Catalog", Orange.data.Table)
        configuration_table = Output("Cleaned Catalog Configuration Table", Orange.data.Table)

    class Error(OWWidget.Error):
        no_data = Msg("No data input provided. Please connect a data source.")
        declustering_failed = Msg("Error occurred during declustering.")

    def __init__(self):
        super().__init__()
        self.data = None
        self.cleaned_data = None

        self.output: Optional[OutputData] = None

        self.method = "Gardner-Knopoff"
        self.time_window = 15 / 24
        self.fs_time_prop = 1.0
        self.q_value = 0.5
        self.fractal_dimension = 1.6
        self.b_value = 1.0

        self.controlArea.layout().setAlignment(Qt.AlignTop)

        box_decluster = gui.widgetBox(self.controlArea, "Declustering Settings")
        self.decluster_combobox = QComboBox(self)
        self.decluster_combobox.addItems(["Gardner-Knopoff", "Nearest Neighbor"])
        gui.widgetLabel(box_decluster, "Select Declustering Method:")
        box_decluster.layout().addWidget(self.decluster_combobox)
        self.decluster_combobox.editTextChanged.connect(self.configurations_table)

        self.dynamic_layout = QVBoxLayout()
        box_decluster.layout().addLayout(self.dynamic_layout)

        self.decluster_combobox.currentIndexChanged.connect(self.update_method_fields)
        self.update_method_fields()

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.controlArea.layout().addItem(spacer)

        box_input = gui.widgetBox(self.mainArea, "Original Events Catalog")
        self.view_input = DataTableView(sortingEnabled=True)
        box_input.layout().addWidget(self.view_input)

        box_output = gui.widgetBox(self.mainArea, "Declustered Events Catalog")
        view_output = DataTableView(sortingEnabled=True)

        header = view_output.horizontalHeader()
        header.setSectionsMovable(True)
        header.setSectionsClickable(True)
        header.setSortIndicatorShown(True)
        header.setSortIndicator(-1, Qt.AscendingOrder)

        self.view_output = view_output
        box_output.layout().addWidget(self.view_output)


        gui.button(self.controlArea, self, "Decluster ", callback=self.decluster_and_clean)
        gui.button(self.controlArea, self, "Reset", callback=self.reset_node)

    def update_method_fields(self):
        for i in reversed(range(self.dynamic_layout.count())):
            widget_to_remove = self.dynamic_layout.itemAt(i).widget()
            self.dynamic_layout.removeWidget(widget_to_remove)
            widget_to_remove.deleteLater()

        if self.decluster_combobox.currentText() == "Gardner-Knopoff":
            self.time_window_edit = QLineEdit(self)
            self.time_window_edit.setText(str(self.time_window))
            self.dynamic_layout.addWidget(QLabel("Time Window (days):"))
            self.dynamic_layout.addWidget(self.time_window_edit)
            self.time_window_edit.textChanged.connect(self.configurations_table)
            self.fs_time_prop_edit = QLineEdit(self)
            self.fs_time_prop_edit.setText(str(self.fs_time_prop))
            self.dynamic_layout.addWidget(QLabel("Time Proportion:"))
            self.dynamic_layout.addWidget(self.fs_time_prop_edit)
            self.fs_time_prop_edit.textChanged.connect(self.configurations_table)
        else:
            self.b_value_edit = QLineEdit(self)
            self.b_value_edit.setText(str(self.b_value))
            self.dynamic_layout.addWidget(QLabel("b Value:"))
            self.dynamic_layout.addWidget(self.b_value_edit)
            self.b_value_edit.textChanged.connect(self.configurations_table)
            self.q_value_edit = QLineEdit(self)
            self.q_value_edit.setText(str(self.q_value))
            self.dynamic_layout.addWidget(QLabel("q Value:"))
            self.dynamic_layout.addWidget(self.q_value_edit)
            self.q_value_edit.textChanged.connect(self.configurations_table)
            self.fractal_dimension_edit = QLineEdit(self)
            self.fractal_dimension_edit.setText(str(self.fractal_dimension))
            self.dynamic_layout.addWidget(QLabel("Fractal Dimension:"))
            self.dynamic_layout.addWidget(self.fractal_dimension_edit)
            self.fractal_dimension_edit.textChanged.connect(self.configurations_table)

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
    def set_data(self, data):
        if data is not None:
            self.clear()
            self.data = data
            df = pc.table_to_frame(data)
            if 'index' in df.columns:
                df = df.drop('index', axis=1)
            cleaned = pc.table_from_frame(df)
            self.view_input.setModel(_TableModel(cleaned)) if data else self.view_input.setModel(None)
        else:
            self.Error.no_data()

        self.Outputs.cleaned_data.send(None)

    def decluster_and_clean(self):
        if not self.data:
            self.Error.no_data()
            return

        try:
            df = pc.table_to_frame(self.data).drop_duplicates()
            if self.decluster_combobox.currentText() == "Gardner-Knopoff":
                df = self.decluster_gardner_knopoff(df)
            else:
                df = self.decluster_nearest_neighbor(df)

            columns_to_keep = ['mag', 'magnitude', 'place', 'latitude', 'longitude', 'time', 'alert', 'status', 'tsunami']
            df = df[[col for col in columns_to_keep if col in df.columns]]

            if "magnitude" in df.columns:
                df.rename(columns={"magnitude": "mag"}, inplace=True)

            cleaned_table = pc.table_from_frame(df)

            self.configurations_table()
            self.Outputs.cleaned_data.send(cleaned_table)

            self.output = OutputData(
                table=cleaned_table,
                model=_TableModel(cleaned_table)
            )

            self._setup_table_view()

        except Exception as e:
            self.Error.declustering_failed()
            print(e)

    def configurations_table(self):
        df = pd.DataFrame()

        df['Declustering Method'] = [self.decluster_combobox.currentText()]

        if self.decluster_combobox.currentText() == "Gardner-Knopoff":
            df['Param1'] = [self.time_window_edit.text()]
            df['Param2'] = [self.fs_time_prop_edit.text()]
            df['Param3'] = None
        else:
            df['Param1'] = [self.b_value_edit.text()]
            df['Param2'] = [self.q_value_edit.text()]
            df['Param3'] = [self.fractal_dimension_edit.text()]

        out_configurations = pc.table_from_frame(df)

        self.Outputs.configuration_table.send(out_configurations)

    def decluster_nearest_neighbor(self, df):
        catalog = df.copy()
        catalog['time'] = pd.to_datetime(catalog['time'], errors='coerce')
        catalog = catalog.sort_values(by='time').reset_index(drop=True)

        catalog['Tij'] = 0.0
        catalog['Rij'] = 0.0
        catalog['Nij'] = 0.0
        catalog['parent_magnitude'] = 0.0
        catalog['neighbor'] = 0

        children = catalog.iloc[0:].copy().reset_index(drop=True)

        for i, child in children.iterrows():
            potential_parents = catalog[catalog['time'] < child['time']]
            if potential_parents.empty:
                continue

            potential_parents = potential_parents.copy()
            potential_parents['Tij'] = (child['time'] - potential_parents['time']).dt.total_seconds() / 3600
            potential_parents['Tij'] *= 10 ** (-float(self.q_value_edit.text()) * float(self.b_value_edit.text()) * potential_parents['mag'])

            potential_parents['Rij'] = np.sqrt((child['latitude'] - potential_parents['latitude']) ** 2 +
                                               (child['longitude'] - potential_parents['longitude']) ** 2)
            potential_parents['Rij'] = (potential_parents['Rij'] ** float(self.fractal_dimension_edit.text())) * 10 ** \
                                       ((float(self.q_value_edit.text()) - 1) * float(self.b_value_edit.text()) * potential_parents['mag'])

            potential_parents['Nij'] = potential_parents['Tij'] * potential_parents['Rij']


            nearest_neighbor = potential_parents.loc[potential_parents['Nij'].idxmin()]
            children.at[i, 'Tij'] = nearest_neighbor['Tij']
            children.at[i, 'Rij'] = nearest_neighbor['Rij']
            children.at[i, 'Nij'] = nearest_neighbor['Nij']
            children.at[i, 'parent_magnitude'] = nearest_neighbor['mag']
            children.at[i, 'neighbor'] = nearest_neighbor.name

        valid_indices = set(children['neighbor'].unique())

        catalog = catalog[catalog.index.isin(valid_indices)].reset_index(drop=True)

        return catalog

    def decluster_gardner_knopoff(self, df):
        pd.set_option('display.max_columns', None)

        times = df['time'].to_list()
        latitudes = df['latitude'].to_list()
        longitudes = df['longitude'].to_list()
        magnitudes = df['mag'].to_list()
        places = df['place'].to_list()
        alerts = df['alert'].to_list()
        status = df['status'].to_list()
        tsunamis = df['tsunami'].to_list()

        data = pd.DataFrame({
            'time': times,
            'latitude': latitudes,
            'longitude': longitudes,
            'magnitude': magnitudes,
            'place': places,
            'alert': alerts,
            'status': status,
            'tsunami': tsunamis
        })

        catalogue = Catalogue()
        catalogue.data = data

        catalogue.data['time'] = pd.to_datetime(catalogue.data['time'], errors='coerce')
        catalogue.data['year'] = catalogue.data['time'].dt.year
        catalogue.data['month'] = catalogue.data['time'].dt.month
        catalogue.data['day'] = catalogue.data['time'].dt.day
        catalogue.data['hour'] = catalogue.data['time'].dt.hour
        catalogue.data['minute'] = catalogue.data['time'].dt.minute
        catalogue.data['second'] = catalogue.data['time'].dt.second

        catalogue.sort_catalogue_chronologically()

        # Método de declusterización Gardner-Knopoff
        declust_method = GardnerKnopoffType1()

        declust_config = {
            "time_distance_window": GardnerKnopoffWindow(),
            "fs_time_prop": float(self.fs_time_prop_edit.text()),
            "time_cutoff": float(self.time_window_edit.text())
        }

        cluster_index, cluster_flag = declust_method.decluster(catalogue, declust_config)

        catalogue.data["cluster_index"] = cluster_index
        catalogue.data["cluster_flag"] = cluster_flag

        # Filtrar solo mainshocks
        declustered_catalogue = catalogue.data[catalogue.data['cluster_flag'] == 0]

        declustered_df = pd.DataFrame(declustered_catalogue,
                                      columns=['time', 'latitude', 'longitude', 'magnitude', 'place', 'alert',
                                               'status', 'tsunami', 'cluster_index', 'cluster_flag'])

        return declustered_df

    def reset_node(self):
        """Reinicia el nodo y muestra una tabla vacía."""
        self.clear()

        self.Outputs.cleaned_data.send(None)

        self.output: Optional[OutputData] = None

        self._setup_table_view()

        self.time_window = 1
        self.space_window = 0.0

        self.Outputs.configuration_table.send(None)

    def clear(self):
        self.Error.no_data.clear()
        self.Error.declustering_failed.clear()